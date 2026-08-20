"""CRAM-DF core substrate.

Axiomatic discipline:
  A1 — zero floating point. Every value in this module is a Python int or an
       integer-dtype numpy array. No f32/f64 anywhere on a production path.
  A2 — reconstruction-free. No Garner, no mixed-radix, no positional decode.
       Magnitude/winding is derived on demand by K-Elimination: one modular
       subtraction (+ one multiply outside the star family). derive() exists
       only for the sanctioned emission seam (display/audit boundary).
  A3 — all lane operators used here are standard CRT ring homomorphisms
       (no operator distortion), so the distortion certificate is trivial
       (F_eff = F_base, Gamma = 1). The one non-homomorphic probe (Sqr on the
       shadow lane 11) is the sanctioned SD-11 construct and is used as a
       read-only probe, never as arithmetic.

Canon guard: modular inverses via pow(a, -1, m) — extended-Euclid semantics,
valid on composite moduli. NEVER Fermat pow(a, m-2, m) (silently wrong on
composite/anchor moduli — the classic CRAM trap).

DKAM note: the only degree-2 operator (Sqr) runs on lane 11 only; transport
core resonance order rho = 3 > d = 2 (subcritical), and lane 7 never squares.
"""

from math import gcd

import numpy as np

# ---------------------------------------------------------------------------
# Safe Basis and typed lanes
# ---------------------------------------------------------------------------

S6 = (2, 3, 5, 7, 11, 13)          # Safe Basis (Fabric/Measurement/Boundary)
M6 = 30030
S8 = (2, 3, 5, 7, 11, 13, 17, 19)  # Colony extension
C8 = 9699690
TRANSPORT_CORE = (3, 7, 11, 13)    # coprime to SCALE=10^4
QR11 = frozenset({1, 3, 4, 5, 9})  # quadratic residues mod 11 (11 = 3 mod 4)
QNR11 = frozenset({2, 6, 7, 8, 10})


def modinv(a: int, m: int) -> int:
    """Extended-Euclid modular inverse (raises if gcd(a, m) != 1)."""
    return pow(a % m, -1, m)


# ---------------------------------------------------------------------------
# Dual-Track K-Elimination (star family aware)
# ---------------------------------------------------------------------------

class DualTrack:
    """Main modulus M + anchor A, gcd(M, A) = 1.

    K-Elimination: for X in [0, M*A),  k = floor(X / M) is derived from the
    residue pair alone:      k = (vA - vM) * M^{-1} (mod A).
    Star family A = c*M + 1: M^{-1} mod A = A - c  (no precomputed constants);
    for c = 1 (adjacent pair) this collapses to k = (vM - vA) mod A —
    a single modular subtraction.
    """

    def __init__(self, M: int, A: int):
        if gcd(M, A) != 1:
            raise ValueError("dual track requires gcd(M, A) == 1")
        self.M, self.A = M, A
        self.range = M * A
        # star-family detection: A = c*M + 1  ->  inverse is A - c by construction
        if (A - 1) % M == 0:
            self.star_c = (A - 1) // M
            self.Minv = (A - self.star_c) % A
        else:
            self.star_c = None
            self.Minv = modinv(M, A)
        # cross-check the constructed inverse against extended Euclid
        assert self.Minv == modinv(M, A)

    # -- scalar paths -------------------------------------------------------
    def encode(self, X: int):
        return X % self.M, X % self.A

    def k(self, vM: int, vA: int) -> int:
        if self.star_c == 1:                       # adjacent star pair
            return (vM - vA) % self.A              # pure subtraction
        return ((vA - vM) * self.Minv) % self.A

    def k_general(self, vM: int, vA: int) -> int:
        return ((vA - vM) * self.Minv) % self.A

    def derive(self, vM: int, vA: int) -> int:
        """Emission-seam only: X = vM + k*M (sanctioned boundary, not hot path)."""
        return vM + self.k(vM, vA) * self.M

    # -- vector paths (numpy int64) ----------------------------------------
    def k_map(self, arr):
        a = np.asarray(arr).astype(np.int64)
        vM = a % self.M
        vA = a % self.A
        if self.star_c == 1:
            return (vM - vA) % self.A
        return ((vA - vM) * self.Minv) % self.A


# Star ladders used by KELD
STAR8 = DualTrack(36, 37)      # 8-bit luminance ladder (range 1332)
STAR16 = DualTrack(256, 257)   # 16-bit ladder, adjacent Fermat pair (range 65792)


# ---------------------------------------------------------------------------
# KELD — K-Elimination Luminance Decode (exact stratification)
# ---------------------------------------------------------------------------

def keld_map(img, dt: DualTrack = STAR8):
    """Exact layer index K = floor(L / M), derived residue-natively.

    Valid for L in [0, dt.range). For 8-bit imagery use STAR8 (bands of width
    36, harmonic centers k*37); for 16-bit use STAR16.
    """
    return dt.k_map(img)


def keld_masks(img, dt: DualTrack = STAR8):
    K = keld_map(img, dt)
    return K, {int(k): (K == k) for k in np.unique(K)}


def keld_isopleth(img, k_boundary: int = 3, dt: DualTrack = STAR8):
    """Binary silhouette: pixels below the k_boundary band vs at/above it.

    The 111 = 3*37 harmonic sits at the median of the 8-bit range; every
    pigment-to-ground transition crosses this boundary.
    """
    K = keld_map(img, dt)
    dark = (K < k_boundary).astype(np.int64)
    h = np.zeros_like(dark)
    v = np.zeros_like(dark)
    h[:, 1:] = dark[:, 1:] ^ dark[:, :-1]
    v[1:, :] = dark[1:, :] ^ dark[:-1, :]
    return (h | v)


# ---------------------------------------------------------------------------
# Shadow Prime 11 — sigma fiber, Sqr-carry, QR/QNR straddle
# ---------------------------------------------------------------------------

def sigma(img, p: int = 11):
    return np.asarray(img).astype(np.int64) % p


def sqr_carry(img, p: int = 11):
    """C_p = floor(2 * (r^2 mod p) / p) in {0,1} — Sqr-carry stratification on a
    shadow-channel lane (p = 3 mod 4 partitions residues into QR/QNR strata).

    Exact behaviour (verified exhaustively in the harness): fires iff the
    lane residue lies in a fixed class set ({3, 8} for p = 11) — a
    residue-class indicator probe, not a gradient.

    A8 guard: Sqr never runs on lane 7 (the Bridge). Refused, not warned.
    """
    if p == 7:
        raise ValueError("A8: Sqr operator is forbidden on lane 7 (Bridge)")
    s = (sigma(img, p) ** 2) % p
    return (2 * s) // p


def sqr_carry_fire_set(p: int):
    """The exact residue classes on which sqr_carry fires (derived, not listed)."""
    if p == 7:
        raise ValueError("A8: Sqr operator is forbidden on lane 7 (Bridge)")
    return sorted(a for a in range(p) if 2 * ((a * a) % p) >= p)


# ---------------------------------------------------------------------------
# Tower K-Elimination (multi-level winding recovery, residue-space O(levels))
# ---------------------------------------------------------------------------

def tower_k(residues, moduli):
    """Recover all winding levels of X < prod(moduli) from its residues alone.

    moduli = (m0, a1, a2, ...), pairwise coprime. Level 1 recovers
    k1 mod a1 by ordinary K-Elimination; each further level j recovers the
    next winding digit from residue a_j via one modular subtract + multiply:

        X = v0 + m0*(k^(1) + a1*(k^(2) + a2*(...)))

    Returns (K, X) with K = floor(X / m0) — every step stays in residue
    space; no Garner, no mixed-radix emission (the nested form above is a
    derivation ladder over anchors, each digit read out independently by
    K-Elimination against its own anchor, not a positional decode of the
    residue tray).
    """
    ms = list(moduli)
    vs = list(residues)
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            if gcd(ms[i], ms[j]) != 1:
                raise ValueError("tower moduli must be pairwise coprime")
    prefix = ms[0]                 # product of resolved levels
    x = vs[0] % ms[0]              # value known exactly below `prefix`
    for j in range(1, len(ms)):
        a = ms[j]
        inv = modinv(prefix, a)    # extended Euclid (composite-safe)
        digit = ((vs[j] - x) * inv) % a
        x = x + digit * prefix
        prefix *= a
    return (x - (vs[0] % ms[0])) // ms[0], x


def straddle_edges(img, axis: int = 1):
    """QR/QNR Complement Straddle marks: adjacent pixels with
    sigma(a) + sigma(b) = 0 (mod 11), both nonzero. By Theorem 5.3 exactly one
    of the pair is a QR and the other a QNR (11 = 3 mod 4)."""
    s = sigma(img)
    a = np.take(s, range(0, s.shape[axis] - 1), axis=axis)
    b = np.take(s, range(1, s.shape[axis]), axis=axis)
    return ((a + b) % 11 == 0) & (a != 0) & (b != 0)


# ---------------------------------------------------------------------------
# Lane-Comb selective differencing (residue-native, CRT-selective)
# ---------------------------------------------------------------------------

def _lane_diffs(img, p: int, axis: int):
    r = np.asarray(img).astype(np.int64) % p
    return np.diff(r, axis=axis) % p           # equals (true step) mod p


def selective_delta(img, deltas, lanes=TRANSPORT_CORE[1:], axis: int = 1):
    """Fire exactly where the local step d satisfies d = delta (mod every lane)
    for some target delta. Residue-native: the integer difference d is never
    materialized — each lane compares its own residue diff to the target's
    residue. With lanes (7, 11, 13) the joint class identifies d mod 1001,
    i.e. the probe is exact-value-selective for |d| <= 500.

    `deltas` may be a single int or an iterable (use (+1, -1) to catch both
    edges of a +1 ink stroke).
    """
    if isinstance(deltas, int):
        deltas = (deltas,)
    hit = None
    per_lane = {p: _lane_diffs(img, p, axis) for p in lanes}
    for d in deltas:
        h = None
        for p in lanes:
            t = per_lane[p] == (d % p)
            h = t if h is None else (h & t)
        hit = h if hit is None else (hit | h)
    return hit


def any_delta(img, lanes=TRANSPORT_CORE[1:], axis: int = 1):
    """Fire where the local step is nonzero mod at least one lane
    (catches every |d| < prod(lanes) except d = 0)."""
    hit = None
    for p in lanes:
        t = _lane_diffs(img, p, axis) != 0
        hit = t if hit is None else (hit | t)
    return hit


# ---------------------------------------------------------------------------
# NODE-INF02 — bit-depth-driven lane sets (P6 sizing rule)
# A lane set L with product P is value-exact for steps |d| <= (P-1)//2.
# Source bit depth therefore SELECTS the lane set; it is not a free choice.
#   8-bit  evidence, |d| <= 255    -> (7,11,13)      P=1,001    B=500
#   14-bit evidence, |d| <= 16383  -> (11,13,17,19)  P=46,189   B=23,094
#   headroom                       -> (7,11,13,17,19) P=323,323 B=161,661
# ---------------------------------------------------------------------------

LANES_8BIT = (7, 11, 13)
LANES_14BIT = (11, 13, 17, 19)
LANES_EXT = (7, 11, 13, 17, 19)


def lane_bound(lanes):
    """Largest |d| for which this lane set is value-exact (P6)."""
    P = 1
    for p in lanes:
        P *= p
    return (P - 1) // 2


def lanes_for_bitdepth(bits: int):
    """Smallest shipped lane set that is value-exact for `bits`-bit evidence."""
    need = (1 << bits) - 1
    for lanes in (LANES_8BIT, LANES_14BIT, LANES_EXT):
        if lane_bound(lanes) >= need:
            return lanes
    raise ValueError(f"no shipped lane set covers {bits}-bit evidence")
