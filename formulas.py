from scipy.optimize import brentq
import math

# Constants
R = 0.0831446261815324  # L-bar/mol-K
n = 2  # number of ions for Van Hoff's equation
MM_NaCl = 58.44277  # g/mol
MM_W = 18.01528  # g/mol
v = 2  # dissociation constant for NaCl
vm = 1  # cations
vx = 1  # anions
zm = 1  # e
zx = -1  # e
b = 1.2  # (kg / mol)^(1/2)
alpha = 2  # (kg / mol)^(1/2)
degCtoK = 273.15  # add to convert °C to K

# Formulas

def IDF(Qdi, Jw, ds):
    # Iterate to the next draw flow
    Qdf = Qdi + Jw*ds
    return Qdf

def IDFPizter(Qdi, Jw, dA):
    # Iterate to the next draw flow
    Qdf = Qdi + Jw*dA #L/h + (L/m^2/h * m^2 = L/h) 
    return Qdf

def IFF(Qfi, Jw, ds):
    # Iterate to the next feed flow
    Qff = Qfi - Jw*ds
    return Qff

def MF(Q, ns, npv):
    # Membrane flow
    Qm = Q/ns/npv
    return Qm

def IDC(Qdi, Cdi, Qdf, Js, ds):
    # Iterate to the next draw concentration
    Cdf = (Qdi*Cdi*MM_NaCl - Js*ds)/Qdf/MM_NaCl
    return Cdf

def IFC(Qfi, Cfi, Qff, Js, ds):
    # Iterate to the next feed concentration
    Cff = (Qfi*Cfi*MM_NaCl + Js*ds)/Qff/MM_NaCl
    return Cff

def OsP(C, n, R, T):
    # Osmotic pressure
    R = 0.0831446261815324  # cm^3 bar / K / mol
    OsP = C*n*R*T
    return OsP

def OpP(PId, PIf):
    # Optimum pressure difference
    dP = (PId - PIf)/2
    return dP

def WF(A, B, D, k, S, PId, PIf, dP, Jwt):
    # Solve the water flux
    def func(Jwt): return Jwt - A*((PId*math.exp(-Jwt/k) - PIf*math.exp(Jwt * 1e-3*S/D)) / \
        (1 + B/Jwt*(math.exp(Jwt*1e-3*S/D)-math.exp(-Jwt/k)))-dP)
    Jw = brentq(func, 1e-6, 1000)  # L/m^3/h
    return Jw

def SF(B, D, k, S, Cd, Cf, Jw):
    # Salt flux kg/m^3/h
    Js = B*(Cd*MM_NaCl*math.exp(-Jw/k) - Cf*MM_NaCl*math.exp(Jw*1e-3*S/D)) / \
        (1+B/Jw*(math.exp(Jw*1e-3*S/D) - math.exp(-Jw/k)))
    return Js

def V(Q, L, H):
    # Velocity in m/s
    Q = Q*1e-3/60/60  # L/h to m^3/s
    A = L * H  # m^2
    V = Q/A
    return V

def BPD(Pi, Vi, Vf, Di, Df):
    # Pressure drop using Bernoulli's equation assuming density is equal
    # Velocity component from Pa to bar
    Pf = Pi + (0.5*Vi**2*Di - 0.5*Vf**2*Df)/1e5
    return Pf

def RelativeDiffusivity(T, P):
    U1 = 3.4279E2
    U2 = -5.0866E-3
    U3 = 9.4690E-7
    U4 = -2.0525
    U5 = 3.1159E3
    U6 = -1.8289E2
    U7 = -8.0325E3
    U8 = 4.2142E6
    U9 = 2.1417
    C = U4 + U5/(U6 + T)
    B = U7 + U8/T + U9*T
    D1000 = U1*math.exp(U2*T + U3*T**2)
    try:
        D = D1000 + C*math.log((B + (P))/(B + 1000))
    except:
        D = 0
    return D

def APhi(D, T):  # Debye-Hückel slope for the osmotic coefficient
    NA = 6.022045E23
    PI = math.pi
    pw = 1
    k = 1.3806049E-16 #erg K-1
    e = 4.803242E-10  # esu
    A_phi = 1/3*(2*PI*NA*pw/1000)**(1/2)*(e**2/(D*k*T))**(3/2)
    return A_phi

def IonicStrength(Molal_NaCl):
    Ions = [
        {"molality": Molal_NaCl, "charge": 1},
        {"molality": Molal_NaCl, "charge": -1}
    ]
    I = 0
    for i in range(0, len(Ions)):
        I += 0.5*Ions[i]['molality']*math.pow(Ions[i]['charge'], 2)
    return I

def OLIOP(c):
    PI = 0.55332*math.pow(c, 3) + 4.56902*math.pow(c, 2) + 44.24188*c
    return PI

def Beta0NaCl(T, P):
    z1 = -656.81518
    z2 = 24.879183
    z3 = -2.1552731e-5
    z4 = 5.0166855e-8
    z5 = 0
    z6 = -4.4640952
    z7 = 0.011087099
    z8 = -6.4479761e-8
    z9 = -2.3234032e-10
    z10 = 0
    z11 = -5.2194871e-6
    z12 = 2.4445210e-10
    z13 = 2.8527066e-13
    z14 = -1.5696231
    z15 = 2.2337864e-3
    z16 = -6.3933891e-7
    z17 = 4.5270573e-11
    z18 = 5.4151933
    z19 = 0
    z20 = 0
    z21 = 0
    Beta_0_NaCl = z1/T + z2 + z3*P + z4*P**2 + z5*P**3 + z6*math.log(T) + \
        (z7+z8*P + z9*P**2 + z10*P**3)*T + \
        (z11 + z12*P + z13*P**2)*T**2 + (z14 + z15*P + z16*P**2 + z17*P**3)/(T-227) + \
        (z18 + z19*P + z20*P**2 + z21*P**3)/(680-T)
    return Beta_0_NaCl

def Beta1NaCl(T, P):
    z22 = 119.31966
    z23 = -0.48309327
    z24 = 1.4068095e-3
    z25 = -4.2345814
    Beta_1_NaCl = z22/T + z23 + z24*T + z25/(T-227)
    return Beta_1_NaCl

def CphiNaCl(T, P):
    z26 = -6.1084589
    z27 = 0.40743803
    z28 = -6.8152430e-6
    z29 = -0.075354649
    z30 = 1.2609014e-4
    z31 = 6.2480692e-8
    z32 = 1.8994373e-8
    z33 = -1.0731264e-10
    z34 = 0.32136572
    z35 = -2.5382945e-4
    z36 = 0
    z37 = 0
    C_phi_NaCl = z26/T + z27 + z28*P + z29*math.log(T) + (z30 + z31*P)*T + \
        (z32 + z33*P)*T**2 + (z34 + z35*P)/(T-227) + (z36 + z37*P)/(680-T)
    return C_phi_NaCl

def GammaPhi(A_phi, Beta_0_NaCl, Beta_1_NaCl, C_phi_NaCl, I, M):
    ln_gamma_NaCl = -abs(zm*zx)*A_phi* \
        (math.sqrt(I)/(1 + b*math.sqrt(I)) + 2/b*math.log(1 + b*math.sqrt(I))) + \
        M*2*vm*vx/v*(2*Beta_0_NaCl + 2 * \
        Beta_1_NaCl/(alpha**2*I)*(1 - (1 + alpha*math.sqrt(I) - alpha**2*I/2)* \
        math.exp(-alpha*math.sqrt(I)))) + 3/2*M**2*(2*(vm*vx)**(3/2)/v*C_phi_NaCl)
    gamma_NaCl = math.exp(ln_gamma_NaCl)
    return gamma_NaCl

def Phi(A_phi, Beta_0_NaCl, Beta_1_NaCl, C_phi_NaCl, I, M):
    phi = 1 - abs(zm*zx)*A_phi*math.sqrt(I)/(1 + b*math.sqrt(I)) + \
        M*2*vm*vx/v*(Beta_0_NaCl + Beta_1_NaCl*math.exp(-alpha*math.sqrt(I))) + \
        M**2*2*(vm*vx)**(3/2)/v*C_phi_NaCl
    return phi

def Av(T):
    A_v = 1.50415 + 1.3421e-2*(T-273.15) + 3.0591e-5*(T-273.15)**2 + \
        1.15588e-6*(T-273.15)**3 - 5.2393e-9*(T-273.15)**4 + 2.6561e-11*(T-273.15)**5
    return A_v

def BVNaCl(T, P):
    P0 = 1.01325
    u1 = -2.1451068e-5
    u2 = 2.2324909e-3
    u3 = -6.4950599e-8
    u4 = 2.4503020e-10
    u5 = 0
    u6 = 1.0033371e-7
    u7 = -1.2784026e-6
    u8 = -4.6468063e-10
    u9 = 5.7054131e-13
    u10 = 0
    u11 = 0
    u12 = 1.3581172e-10
    u13 = 0
    u14 = 0
    B_V_NaCl = u1 + u2/(T-227) + u3*T + u4*T**2 + u5/(680-T) + (P-P0)*(u6 + u7/(T-227) + \
        u8*T + u9**T*2 + u10/(680-T)) + (P-P0)**2*(u11 + u12/(T-227) + u13*T + u14/(680-T))
    return B_V_NaCl
def CVNaCl(T):
    u15 = -6.8152430e-6
    u16 = -2.5382945e-4
    u17 = 6.2480692e-8
    u18 = -1.0731284e-10
    u19 = 0
    TWO_C_V_NaCl = u15 + u16/(T-227) + u17*T + u18*T**2 + u19/(680-T)
    C_V_NaCl = TWO_C_V_NaCl /2
    return C_V_NaCl

def V0NaCl(T):
    A0 = 16.620
    A1 = 8.7385e-2
    A2 = -1.9994e-3
    A3 = 1.7452e-5
    A4 = -0.8023e-7
    V_0_NaCl = A0 + A1*(T-298.15) + A2*(T-298.15)**2 + A3*(T-298.15)**3 + A4*(T-298.15)**4
    return V_0_NaCl

def VPhiNaCL(A_v, B_V_NaCl, C_V_NaCl, I, M, T, V_0_NaCl):
    R = 83.1446261815324  # cm^3 bar / K / mol
    V_phi_NaCl = V_0_NaCl + v*abs(zm*zx)*(A_v)/(2*b)*math.log(1 + b * math.sqrt(I)) + \
        2*R*T*vm*vx*(M)*(B_V_NaCl + (M)*vm*zm*C_V_NaCl)
    return V_phi_NaCl

def DensityWater(T):
    dT0 = lambda T: T - 273.15
    P0 = (0.99983952 + 16.945176e-3*dT0(T) - 7.987040e-6*dT0(T)**2 - \
        46.170461e-9*dT0(T)**3 + 105.56302e-12*dT0(T)**4 - \
        280.54253e-15*dT0(T)**5)/(1 + 16.879850e-3*dT0(T)) #g/cm^3
    return P0

def ApparentDensity(M, rho_w, V_phi_NaCl):
    rho = (1000 + M*MM_NaCl)/(1000/rho_w + M*V_phi_NaCl)
    return rho

def WaterActivity(M, phi):
    n_s = M
    n_w = 1000/MM_W
    a_w = math.exp(-phi*v*n_s/n_w)
    return a_w

def OsmoticPressurePitzer(a_w, MVW, T):
    R = 83.1446261815324  # cm^3 bar / K / mol
    PI = -R*T/(MVW)*math.log(a_w)
    return PI

def MolarVolumeWater(rho_w):
    MVW = MM_W/rho_w #g/mol / g/cm^3 = cm^3 / mol
    return MVW

def Molality(m_NaCl):
    Molal_NaCl = m_NaCl/MM_NaCl
    return Molal_NaCl

def MolalityToMolarity(m_NaCl, rho):
    m_W = 1000
    V = (m_NaCl + m_W)/(rho*1000)
    M = (m_NaCl/MM_NaCl)/V
    return M

def mNaCl(pc_wt):
    m_W = 1000  # mass of water g
    m_NaCl = (pc_wt)/(1-pc_wt)*m_W  # mass of MM_NaCl g
    return m_NaCl

def OsmoticProperties(P, T, pc_wt):
    m_NaCl = mNaCl(pc_wt)
    Molal_NaCl = Molality(m_NaCl)
    I = IonicStrength(Molal_NaCl)
    MVW, rho, rho_w = SolutionDensity(P, T, I, Molal_NaCl)
    a_w = OsmoticActivity(P, T, I, Molal_NaCl)
    M_NaCl = MolalityToMolarity(m_NaCl, rho)
    PI = OsmoticPressurePitzer(a_w, MVW, T)
    return [PI, rho]

def OsmoticActivity(P, T, I, Molal_NaCl):
    D = RelativeDiffusivity(T, P)
    A_phi = APhi(D, T)
    Beta_0_NaCl = Beta0NaCl(T, P)
    Beta_1_NaCl = Beta1NaCl(T, P)
    C_phi_NaCl = CphiNaCl(T, P)
    gamma_MX = GammaPhi(A_phi,Beta_0_NaCl,Beta_1_NaCl, C_phi_NaCl, I,Molal_NaCl)
    phi = Phi(A_phi, Beta_0_NaCl, Beta_1_NaCl, C_phi_NaCl, I, Molal_NaCl)
    a_w = WaterActivity(Molal_NaCl, phi)
    return a_w

def SolutionDensity(P, T, I, Molal_NaCl):
    A_v = Av(T)
    B_V_NaCl = BVNaCl(T,P)
    C_V_NaCl = CVNaCl(T)
    V_0_NaCl = V0NaCl(T)
    rho_w = DensityWater(T)  # kg/L
    V_phi_NaCl = VPhiNaCL(A_v, B_V_NaCl, C_V_NaCl, I, Molal_NaCl, T, V_0_NaCl)
    rho = ApparentDensity(Molal_NaCl, rho_w, V_phi_NaCl)
    MVW = MolarVolumeWater(rho_w)
    return [MVW, rho, rho_w]
    
def QDfPcM(pc_wt, Jw, Js):
    
    return 1
