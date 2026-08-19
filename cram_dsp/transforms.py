"""CRAM-DF exact transforms.

All operations are integer-exact (A1). The reversible transforms here are the
Transduction layer of the pipeline: exact, signature-preserving moves between
frames (pixel frame <-> decorrelated frame <-> band-difference frame) with
bit-exact round trip — T-X-REV realized on image state.

Convolution runs in NTT space over the CLASS-F prime P = 998244353
(= 119 * 2^23 + 1, primitive root 3): zero Gibbs ringing, zero drift,
bit-identical on every platform. Rational kernels are carried as
(integer array, integer denominator) pairs; the single exact-rounding
division happens only at the emission seam.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Integer NTT convolution (exact)
# ---------------------------------------------------------------------------

P = 998244353            # 119 * 2^23 + 1, NTT-friendly CLASS-F prime
G = 3                    # primitive root of P


def _ntt(a, invert: bool):
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        w = pow(G, (P - 1) // length, P)
        if invert:
            w = pow(w, -1, P)
        half = length >> 1
        for i in range(0, n, length):
            wn = 1
            for k in range(i, i + half):
                u = a[k]
                v = a[k + half] * wn % P
                a[k] = (u + v) % P
                a[k + half] = (u - v) % P
                wn = wn * w % P
        length <<= 1
    if invert:
        ninv = pow(n, -1, P)
        for i in range(n):
            a[i] = a[i] * ninv % P
    return a


def _next_pow2(n: int) -> int:
    m = 1
    while m < n:
        m <<= 1
    return m


def _ntt2d(mat, invert: bool):
    nh, nw = len(mat), len(mat[0])
    for r in range(nh):
        _ntt(mat[r], invert)
    for c in range(nw):
        col = [mat[r][c] for r in range(nh)]
        _ntt(col, invert)
        for r in range(nh):
            mat[r][c] = col[r]
    return mat


def _center_lift(x: int) -> int:
    return x - P if x > P // 2 else x


def conv2d_exact(img, ker, mode: str = "full"):
    """Exact 2D integer convolution of img with ker via NTT over F_P.

    Inputs are integer arrays (kernels may be negative). Output entries must
    satisfy |value| < P/2 (true for 16-bit imagery with any practical kernel);
    they are recovered by centered lift. Returns numpy int64.
    """
    img = np.asarray(img)
    ker = np.asarray(ker)
    H, W = img.shape
    kh, kw = ker.shape
    oh, ow = H + kh - 1, W + kw - 1
    nh, nw = _next_pow2(oh), _next_pow2(ow)
    A = [[0] * nw for _ in range(nh)]
    B = [[0] * nw for _ in range(nh)]
    for i in range(H):
        row = img[i]
        for j in range(W):
            A[i][j] = int(row[j]) % P
    for i in range(kh):
        row = ker[i]
        for j in range(kw):
            B[i][j] = int(row[j]) % P
    _ntt2d(A, False)
    _ntt2d(B, False)
    for r in range(nh):
        Ar, Br = A[r], B[r]
        for c in range(nw):
            Ar[c] = Ar[c] * Br[c] % P
    _ntt2d(A, True)
    out = np.zeros((oh, ow), dtype=np.int64)
    for i in range(oh):
        Ai = A[i]
        for j in range(ow):
            out[i, j] = _center_lift(Ai[j])
    if mode == "same":
        r0, c0 = kh // 2, kw // 2
        out = out[r0:r0 + H, c0:c0 + W]
    return out


def conv2d_direct(img, ker):
    """O(HWkhkw) reference convolution in unbounded Python ints (oracle)."""
    img = np.asarray(img)
    ker = np.asarray(ker)
    H, W = img.shape
    kh, kw = ker.shape
    out = [[0] * (W + kw - 1) for _ in range(H + kh - 1)]
    for i in range(H):
        for j in range(W):
            v = int(img[i, j])
            if v == 0:
                continue
            for a in range(kh):
                oa = out[i + a]
                for b in range(kw):
                    oa[j + b] += v * int(ker[a, b])
    return np.array(out, dtype=np.int64)


def conv2d_modp(img, ker, p: int):
    """INV-8-style check lane: independent, cheap recomputation of the full
    convolution modulo a small out-of-band prime p, via lane-residue shifted
    adds (no NTT, no big integers). Comparing conv2d_exact(...) % p against
    this verifies the NTT engine's algebraic integrity in parallel."""
    a = np.asarray(img).astype(np.int64) % p
    k = np.asarray(ker).astype(np.int64) % p
    H, W = a.shape
    kh, kw = k.shape
    out = np.zeros((H + kh - 1, W + kw - 1), dtype=np.int64)
    for i in range(kh):
        for j in range(kw):
            out[i:i + H, j:j + W] = (out[i:i + H, j:j + W] + a * int(k[i, j])) % p
    return out


def check_lane_verify(img, ker, ntt_out_full, p: int = 17) -> bool:
    """True iff the NTT result agrees with the independent mod-p lane."""
    return bool(np.array_equal(np.asarray(ntt_out_full) % p, conv2d_modp(img, ker, p)))


def skew_grad_periodic(img, axis: int = 1):
    """Central-difference operator with periodic boundary — an exactly
    skew-symmetric integer operator D (D^T = -D on the cyclic lattice)."""
    a = np.asarray(img).astype(np.int64)
    return np.roll(a, -1, axis=axis) - np.roll(a, 1, axis=axis)


def skew_energy_ip(img, axis: int = 1) -> int:
    """Kill #113 witness: <I, D(I)> over Z. Identically 0 for every integer
    image because D is skew-symmetric — advection-style energy transfer sums
    to exact integer zero, so iterative filters cannot leak energy into
    synthetic high-frequency noise."""
    a = np.asarray(img).astype(np.int64)
    return int((a * skew_grad_periodic(a, axis)).sum())


def binomial_kernel(n: int):
    """Integer binomial low-pass kernel (row (1,2,1)^n outer product) with its
    exact denominator. Returned as (kernel int64, den int)."""
    row = np.array([1], dtype=np.int64)
    base = np.array([1, 2, 1], dtype=np.int64)
    for _ in range(n):
        row = np.convolve(row, base)
    ker = np.outer(row, row).astype(np.int64)
    return ker, int(ker.sum())


def emit_round_div(num, den: int):
    """Sanctioned emission seam: exact round-half-up integer division."""
    num = np.asarray(num).astype(np.int64)
    return (num + den // 2) // den


# ---------------------------------------------------------------------------
# Reversible integer colour / band transforms (bit-exact round trip)
# ---------------------------------------------------------------------------

def rct_fwd(R, G_, B):
    """JPEG2000 Reversible Colour Transform (integer, lossless)."""
    R = np.asarray(R).astype(np.int64)
    G_ = np.asarray(G_).astype(np.int64)
    B = np.asarray(B).astype(np.int64)
    Y = (R + 2 * G_ + B) >> 2
    U = B - G_
    V = R - G_
    return Y, U, V


def rct_inv(Y, U, V):
    G_ = Y - ((U + V) >> 2)
    R = V + G_
    B = U + G_
    return R, G_, B


def chromadi_fwd(bands):
    """Reversible ChromaDI: (b0, b1-b0, b2-b1, ...). Consecutive band
    differences (the false-colour derivative stack) kept invertible by
    retaining the base band."""
    bands = [np.asarray(b).astype(np.int64) for b in bands]
    out = [bands[0]]
    for i in range(1, len(bands)):
        out.append(bands[i] - bands[i - 1])
    return out


def chromadi_inv(diffs):
    out = [np.asarray(diffs[0]).astype(np.int64)]
    for i in range(1, len(diffs)):
        out.append(out[-1] + diffs[i])
    return out


# ---------------------------------------------------------------------------
# LeGall 5/3 integer lifting wavelet (reversible, multilevel 2D)
# ---------------------------------------------------------------------------

def fwd53(x):
    """1D forward 5/3 lifting on a list of ints. Returns (s, d).
    Boundary rule: clamped neighbour (consistent with inv53 -> exact inverse).
    """
    n = len(x)
    if n == 0:
        return [], []
    if n == 1:
        return [x[0]], []
    nd = n // 2
    ne = (n + 1) // 2
    d = [0] * nd
    for i in range(nd):
        left = x[2 * i]
        right = x[2 * i + 2] if 2 * i + 2 < n else x[2 * i]
        d[i] = x[2 * i + 1] - ((left + right) >> 1)
    s = [0] * ne
    for i in range(ne):
        dl = d[i - 1] if i - 1 >= 0 else d[0]
        dr = d[i] if i < nd else d[nd - 1]
        s[i] = x[2 * i] + ((dl + dr + 2) >> 2)
    return s, d


def inv53(s, d):
    ne, nd = len(s), len(d)
    n = ne + nd
    if n == 0:
        return []
    if n == 1:
        return [s[0]]
    x = [0] * n
    for i in range(ne):
        dl = d[i - 1] if i - 1 >= 0 else d[0]
        dr = d[i] if i < nd else d[nd - 1]
        x[2 * i] = s[i] - ((dl + dr + 2) >> 2)
    for i in range(nd):
        left = x[2 * i]
        right = x[2 * i + 2] if 2 * i + 2 < n else x[2 * i]
        x[2 * i + 1] = d[i] + ((left + right) >> 1)
    return x


def wav2d_fwd(img, levels: int = 1):
    """Multilevel 2D 5/3 forward transform. Returns (coeff grid as list of
    lists of ints, list of processed (h, w) shapes for inversion)."""
    a = [[int(v) for v in row] for row in np.asarray(img)]
    H = len(a)
    W = len(a[0]) if H else 0
    h, w = H, W
    shapes = []
    for _ in range(levels):
        if h < 2 and w < 2:
            break
        for r in range(h):
            s, d = fwd53(a[r][:w])
            a[r][:w] = s + d
        for c in range(w):
            col = [a[r][c] for r in range(h)]
            s, d = fwd53(col)
            for r, v in enumerate(s):
                a[r][c] = v
            for r, v in enumerate(d):
                a[len(s) + r][c] = v
        shapes.append((h, w))
        h = (h + 1) // 2
        w = (w + 1) // 2
    return a, shapes


def wav2d_inv(coeffs, shapes):
    a = [row[:] for row in coeffs]
    for (h, w) in reversed(shapes):
        ne_h = (h + 1) // 2
        for c in range(w):
            s = [a[r][c] for r in range(ne_h)]
            d = [a[r][c] for r in range(ne_h, h)]
            x = inv53(s, d)
            for r, v in enumerate(x):
                a[r][c] = v
        ne_w = (w + 1) // 2
        for r in range(h):
            s = a[r][:ne_w]
            d = a[r][ne_w:w]
            a[r][:w] = inv53(s, d)
    return a
