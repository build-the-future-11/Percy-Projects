#!/usr/bin/env python3
"""Exact/rational verifier for the Math 11 cubic-field results.

No floating-point arithmetic is used in any PASS/FAIL decision.
The only transcendental step (logarithms for the global norm-coset
reduction) is bounded by an exact atanh series over fractions.
"""
from fractions import Fraction as Q
from itertools import product

# -----------------------------------------------------------------------------
# Basic exact interval arithmetic
# -----------------------------------------------------------------------------

def I(lo, hi=None):
    if hi is None:
        hi = lo
    lo, hi = Q(lo), Q(hi)
    assert lo <= hi
    return (lo, hi)

def iadd(a,b): return (a[0]+b[0], a[1]+b[1])
def isub(a,b): return (a[0]-b[1], a[1]-b[0])
def iscale(k,a):
    k=Q(k)
    return (k*a[0], k*a[1]) if k>=0 else (k*a[1], k*a[0])
def imul(a,b):
    vals=(a[0]*b[0],a[0]*b[1],a[1]*b[0],a[1]*b[1])
    return (min(vals),max(vals))
def irec(a):
    assert not (a[0] <= 0 <= a[1])
    vals=(1/a[0],1/a[1])
    return (min(vals),max(vals))
def idiv(a,b): return imul(a,irec(b))
def iabs(a):
    lo,hi=a
    if lo>=0: return a
    if hi<=0: return (-hi,-lo)
    return (Q(0),max(-lo,hi))
def iabsmax(a): return max(abs(a[0]),abs(a[1]))
def imax(a,b): return (max(a[0],b[0]),max(a[1],b[1]))
def ipow2(a): return imul(a,a)

def qdec(s): return Q(s)

def fval(x): return x*x*x - 3*x - 1

# Root intervals for f(x)=x^3-3x-1, each width 1e-30.
R1=I(qdec('-1.532088886237956070404785301111'), qdec('-1.532088886237956070404785301110'))
R2=I(qdec('-0.347296355333860697703433253539'), qdec('-0.347296355333860697703433253538'))
R0=I(qdec('1.879385241571816768108218554649'), qdec('1.879385241571816768108218554650'))
ROOTS=[R0,R1,R2]  # sigma_0, sigma_1, sigma_2

# -----------------------------------------------------------------------------
# Polynomial reduction in Z[t]/(t^3-3t-1), for exact identities
# coefficients are low-to-high degree
# -----------------------------------------------------------------------------

def trim(p):
    p=list(p)
    while len(p)>1 and p[-1]==0: p.pop()
    return p

def padd(a,b):
    n=max(len(a),len(b)); out=[0]*n
    for i in range(n): out[i]=(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0)
    return trim(out)

def pmul(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]+=x*y
    return trim(out)

def pred(p):
    p=list(p)+[0]*8
    # t^3 = 3t + 1; reduce from high degree down
    for d in range(len(p)-1,2,-1):
        c=p[d]
        if c:
            p[d]=0
            p[d-3]+=c
            p[d-2]+=3*c
    return trim(p[:3])
def ppow(a,n):
    out=[1]
    while n:
        if n&1: out=pred(pmul(out,a))
        a=pred(pmul(a,a)); n//=2
    return pred(out)

def pscale(k,a): return [k*x for x in a]

def assert_poly_zero(p): assert pred(p)==[0], pred(p)

T=[0,1]
ONE=[1]
EPS=[1,1]      # theta+1
DELTA=[-1,1]   # theta-1
BETA=[1,5,3]
GAMMA=[2,6,3]

# Exact algebraic identities used in the paper.
assert pred(pmul(DELTA, ppow(EPS,3))) == BETA
assert ppow(EPS,3) == GAMMA
assert pred(pmul([2,-1], ppow(EPS,2))) == [1]  # (2-theta)(theta+1)^2=1
# delta^3 = 3(1-delta^2)
lhs=ppow(DELTA,3)
rhs=pscale(3,padd([1],pscale(-1,ppow(DELTA,2))))
assert lhs==pred(rhs)

# minpoly substitutions: beta^3-21 beta^2+3=0; gamma^3-24 gamma^2+3 gamma+1=0
assert_poly_zero(padd(padd(ppow(BETA,3),pscale(-21,ppow(BETA,2))),[3]))
assert_poly_zero(padd(padd(padd(ppow(GAMMA,3),pscale(-24,ppow(GAMMA,2))),pscale(3,GAMMA)),[1]))

# -----------------------------------------------------------------------------
# Root isolation, using exact signs + monotonic branches of f.
# f' = 3(x^2-1), hence f is monotone on (-inf,-1),(-1,1),(1,inf).
# -----------------------------------------------------------------------------

def verify_root_interval(name,J,branch):
    lo,hi=J
    assert fval(lo)*fval(hi) < 0, (name,'no sign change')
    if branch=='left': assert hi < -1
    elif branch=='middle': assert -1 < lo < hi < 1
    elif branch=='right': assert 1 < lo
    else: raise ValueError(branch)

verify_root_interval('r1',R1,'left')
verify_root_interval('r2',R2,'middle')
verify_root_interval('r0',R0,'right')

# Evaluate a+b*r+c*r^2 on a root interval.
def eval_quad(triple,J):
    a,b,c=triple
    return iadd(I(a), iadd(iscale(b,J), iscale(c,ipow2(J))))

def metrics(triple):
    vals=[eval_quad(triple,J) for J in ROOTS]
    h=iabs(vals[0])
    obj=imax(iabs(vals[1]),iabs(vals[2]))
    return vals,h,obj

beta_vals,L_iv,B_iv=metrics(tuple(BETA))
gamma_vals,U_iv,G_iv=metrics(tuple(GAMMA))

# -----------------------------------------------------------------------------
# Completeness bound for the [L,U] theorem.
# If beta is feasible, any optimizer has |y0|<U and |y1|,|y2|<=B.
# Inverse Vandermonde coefficients are, for root r_i and D_i=f'(r_i):
#   c=sum y_i/D_i, b=sum y_i*r_i/D_i, a=sum y_i/(r_i D_i).
# Rational interval bounds imply |a|<3, |b|<7, |c|<4.
# -----------------------------------------------------------------------------

def coeff_weight_intervals(J):
    D=isub(iscale(3,ipow2(J)),I(3))
    wc=irec(D)
    wb=imul(J,wc)
    wa=irec(imul(J,D))
    return wa,wb,wc
W=[coeff_weight_intervals(J) for J in ROOTS]
Uup=U_iv[1]; Bup=B_iv[1]
coeff_bounds=[]
for k in range(3):
    bd=Uup*iabsmax(W[0][k]) + Bup*(iabsmax(W[1][k])+iabsmax(W[2][k]))
    coeff_bounds.append(bd)
assert coeff_bounds[0] < 3
assert coeff_bounds[1] < 7
assert coeff_bounds[2] < 4

# -----------------------------------------------------------------------------
# Exact 454-triple finite certificate.
# -----------------------------------------------------------------------------
CANDS=[]
for a in range(-2,3):
    for b in range(-6,7):
        for c in range(-3,4):
            if (a,b,c)!=(0,0,0): CANDS.append((a,b,c))
assert len(CANDS)==454

neg_beta=tuple(-x for x in BETA)
neg_gamma=tuple(-x for x in GAMMA)
inside_U=[]; at_U=[]; after_U=[]
for t in CANDS:
    _,h,obj=metrics(t)
    if h[1] < U_iv[0]: inside_U.append((t,h,obj))
    elif h[0] > U_iv[1]: after_U.append((t,h,obj))
    else: at_U.append((t,h,obj))

assert not after_U
assert {t for t,_,_ in at_U} == {tuple(GAMMA),neg_gamma}

# Before U, beta is uniquely optimal up to sign.
for t,h,obj in inside_U:
    if t in {tuple(BETA),neg_beta}:
        # its objective is exactly the reference conjugate interval
        continue
    assert obj[0] > B_iv[1], (t,obj,B_iv)

# At U, gamma is uniquely optimal up to sign among all 454 candidates.
for t in CANDS:
    _,h,obj=metrics(t)
    if t in {tuple(GAMMA),neg_gamma}: continue
    assert obj[0] > G_iv[1], (t,obj,G_iv)

# -----------------------------------------------------------------------------
# Global norm-coset reduction.
# A rigorous log-lattice covering certificate supplies, for every H>0,
# a unit u in <theta,theta+1> with F(u) <= exp(0.9)/sqrt(H).
# Since exp(0.9)<sqrt(8), no norm >=8 element can optimize.
# Norms 2,4,5,6,7 are excluded by inertness of 2,5,7.
# -----------------------------------------------------------------------------

def log_bounds(x,N=42):
    """Exact rational lower/upper bounds for ln(x), x>0 rational."""
    assert x>0
    k=0; y=x
    while y>=2: y/=2; k+=1
    while y<1: y*=2; k-=1
    def series(zarg):
        z=(zarg-1)/(zarg+1)
        zz=z*z; term=z; s=Q(0)
        for n in range(N+1):
            s += term/Q(2*n+1)
            term *= zz
        ap=2*s
        if z==0: return ap,ap
        rem=2*(z**(2*N+3))/Q(2*N+3)/(1-z*z)
        return ap,ap+rem
    ly=series(y); l2=series(Q(2))
    if k>=0: return (ly[0]+k*l2[0], ly[1]+k*l2[1])
    return (ly[0]+k*l2[1], ly[1]+k*l2[0])

def positive_abs(J):
    lo,hi=J
    if lo>=0:return J
    if hi<=0:return (-hi,-lo)
    raise AssertionError('interval crosses zero')
def log_interval(J):
    lo,_=log_bounds(J[0]); _,hi=log_bounds(J[1]); return (lo,hi)

def ivecadd(v,w): return (iadd(v[0],w[0]),iadd(v[1],w[1]))

def coords_for_theta():
    l0=log_interval(positive_abs(R0)); l1=log_interval(positive_abs(R1)); l2=log_interval(positive_abs(R2))
    return (l0,iscale(Q(1,2),isub(l1,l2)))
def coords_for_eps():
    E0=iadd(R0,I(1)); E1=positive_abs(iadd(R1,I(1))); E2=positive_abs(iadd(R2,I(1)))
    l0=log_interval(E0); l1=log_interval(E1); l2=log_interval(E2)
    return (l0,iscale(Q(1,2),isub(l1,l2)))

V1=coords_for_theta(); V2=coords_for_eps()
det=isub(imul(V1[0],V2[1]),imul(V1[1],V2[0]))
assert not (det[0] <= 0 <= det[1])

# 16x16 exact interval cover of centered fundamental coefficient square.
# For e=s V1+t V2, |s|,|t|<=1/2, one of e,e+V1,e+V2,e+V1+V2
# lies in T_R={x>=0, x/2+|y|<=R}, R=9/10.
NGRID=16; R=Q(9,10)
Z=(I(0),I(0)); SH=[Z,V1,V2,ivecadd(V1,V2)]
cover_counts=[0,0,0,0]; max_D=Q(0)
for i in range(NGRID):
    S=I(-Q(1,2)+Q(i,NGRID),-Q(1,2)+Q(i+1,NGRID))
    for j in range(NGRID):
        Tj=I(-Q(1,2)+Q(j,NGRID),-Q(1,2)+Q(j+1,NGRID))
        ex=iadd(imul(S,V1[0]),imul(Tj,V2[0]))
        ey=iadd(imul(S,V1[1]),imul(Tj,V2[1]))
        good=False
        for k,sh in enumerate(SH):
            dx=iadd(ex,sh[0]); dy=iadd(ey,sh[1])
            if dx[0] >= 0:
                Dup=dx[1]/2 + iabsmax(dy)
                if Dup <= R:
                    good=True; cover_counts[k]+=1; max_D=max(max_D,Dup); break
        assert good,(i,j,ex,ey)

# ln(sqrt(8))=(3/2)ln2 > 1 > 0.9.
# Exact atanh series has ln2 > 2/3 + 2/(81) > 2/3.
ln2_lower = Q(2,3)+Q(2,81)
assert Q(3,2)*ln2_lower > 1 > R

# Cubic irreducibility mod p: a cubic over F_p is irreducible iff it has no root.
for p in (2,5,7):
    assert all((z**3-3*z-1)%p != 0 for z in range(p))

# -----------------------------------------------------------------------------
# Human-readable report
# -----------------------------------------------------------------------------

def dec(q,places=18):
    # exact truncation for reporting only; not used in decisions
    sign='-' if q<0 else ''
    q=abs(q); n=q.numerator*10**places//q.denominator
    s=str(n).rjust(places+1,'0')
    return sign+s[:-places]+'.'+s[-places:]

print('PASS: exact root isolation for x^3-3x-1')
print('PASS: algebraic identities for beta, gamma, delta, epsilon')
print('PASS: inverse-Vandermonde completeness bounds')
print('  |a| <',dec(coeff_bounds[0]),'-> |a|<=2')
print('  |b| <',dec(coeff_bounds[1]),'-> |b|<=6')
print('  |c| <',dec(coeff_bounds[2]),'-> |c|<=3')
print('PASS: enumerated',len(CANDS),'nonzero triples')
print('PASS: for L<=H<U, unique minimizers are +/- beta')
print('PASS: at H=U, unique minimizers are +/- gamma')
print('  L in [',dec(L_iv[0]),',',dec(L_iv[1]),']')
print('  U in [',dec(U_iv[0]),',',dec(U_iv[1]),']')
print('  F(beta) in [',dec(B_iv[0]),',',dec(B_iv[1]),']')
print('  F(gamma) in [',dec(G_iv[0]),',',dec(G_iv[1]),']')
print('PASS: 16x16 rational log-lattice cover with R=0.9')
print('  cells by witness shift:',cover_counts)
print('  largest certified cell upper bound:',dec(max_D))
print('PASS: 2,5,7 inertness checks and norm-gap reduction')
print('PASS: GLOBAL CONCLUSION: every optimizer has |Norm| in {1,3}')
print('PASS: since (3)=(theta-1)^3 as ideals, every |Norm|=3 optimizer is (theta-1)*unit')
