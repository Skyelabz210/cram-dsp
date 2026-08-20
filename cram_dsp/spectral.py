"""Exact spectral unmixing for palimpsest separation.

The recovery problem, stated honestly: every pixel of a palimpsest is a
mixture of materials — parchment, overtext ink, undertext ink, damage. What
the scholar wants is the *abundance of the undertext ink* at every pixel.
Band subtraction and PCA do not answer that question; they produce a
statistical axis and leave the reader to squint at it.

The linear mixing model is Y = M a, where M is the (bands x k) matrix of
endmember signatures and a is the per-pixel abundance vector. Solving it is
a least-squares problem whose solution is the pseudoinverse P = (M^T M)^-1
M^T applied to each pixel.

The exactness lever: P has RATIONAL entries. Compute it once in exact
rational arithmetic, clear denominators to get an integer matrix P_int and a
single common denominator D. Then every per-pixel abundance is an exact
integer matmul, and the true abundance is P_int @ y / D — carried as scaled
integers, never evaluated in float. The separation is therefore exact for
every pixel simultaneously, at integer-matmul speed.

A1: Fraction (exact rationals) and integers only. No float on any path.
"""

from fractions import Fraction

import numpy as np


def _mat_from_pixels(sigs):
    """(bands x k) integer endmember matrix from a list of spectra."""
    return np.array(sigs, dtype=np.int64).T


def _exact_pseudoinverse_raw(M):
    """P = (M^T M)^-1 M^T in exact rational arithmetic.

    Returns (P_int, D): integer matrix and common denominator with
    P == P_int / D exactly.
    """
    bands, k = M.shape
    Mf = [[Fraction(int(M[i][j])) for j in range(k)] for i in range(bands)]
    # G = M^T M  (k x k)
    G = [[sum((Mf[r][i] * Mf[r][j] for r in range(bands)), Fraction(0))
          for j in range(k)] for i in range(k)]
    # augment with M^T (k x bands) and solve G X = M^T by exact elimination
    A = [G[i][:] + [Mf[r][i] for r in range(bands)] for i in range(k)]
    for col in range(k):
        piv = None
        for r in range(col, k):
            if A[r][col] != 0:
                piv = r
                break
        if piv is None:
            raise ValueError("endmember matrix is rank-deficient")
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [v / pv for v in A[col]]
        for r in range(k):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [a - f * b for a, b in zip(A[r], A[col])]
    P = [row[k:] for row in A]                      # k x bands, rational
    D = 1
    for row in P:
        for v in row:
            D = D * v.denominator // _gcd(D, v.denominator)
    P_int = np.array([[int(v * D) for v in row] for row in P], dtype=object)
    return P_int, int(D)


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


INT64_MAX = (1 << 63) - 1


def _reduce(P_int, D):
    """Divide out the common factor so the exact ratio P_int/D is minimal."""
    g = int(D)
    for v in np.asarray(P_int).ravel():
        g = _gcd(g, abs(int(v)))
        if g == 1:
            return P_int, int(D)
    return (np.asarray(P_int) // g).astype(object), int(D) // g


def fit_basis_to_int64(endmembers, max_value: int, bands: int):
    """Quantise the endmember basis until the exact solve fits in int64.

    Exactness is always with respect to the basis actually used. Endmember
    signatures are a MODELLING CHOICE, so coarsening them by an exact integer
    shift yields a different — but still exactly solvable — model. This
    returns the finest basis whose exact pseudoinverse and per-pixel matmul
    provably cannot overflow, together with the shift applied.

    Returns (basis, P_int, D, shift).
    """
    shift = 0
    while True:
        basis = [(np.asarray(e, dtype=np.int64) >> shift) for e in endmembers]
        M = _mat_from_pixels(basis)
        if np.abs(M).max() == 0:
            raise ValueError("basis collapsed to zero under quantisation")
        try:
            P_int, D = _exact_pseudoinverse_raw(M)
        except ValueError:
            raise
        P_int, D = _reduce(P_int, D)
        pmax = max(abs(int(v)) for v in np.asarray(P_int).ravel())
        # worst-case magnitude of one row of P_int @ y
        bound = pmax * max_value * bands
        if bound < INT64_MAX and D < INT64_MAX and pmax < INT64_MAX:
            return basis, np.asarray(P_int, dtype=np.int64), int(D), shift
        shift += 1
        if shift > 14:
            raise ValueError("cannot fit an exact solve into int64 for this basis")


def extract_endmembers(cube, k: int = 4, stride: int = 8):
    """Greedy exact endmember search (simplex-vertex style, no float).

    cube: (bands, H, W) integer array.
    Picks the pixel farthest from the origin, then repeatedly the pixel with
    the largest exact residual against the span of those already chosen.
    Residuals are compared as exact rationals; ties break to lower index, so
    the result is deterministic.
    """
    bands = cube.shape[0]
    flat = cube.reshape(bands, -1)[:, ::stride].astype(np.int64)
    n = flat.shape[1]
    energy = (flat.astype(np.int64) ** 2).sum(axis=0)
    idx = [int(np.argmax(energy))]
    for _ in range(k - 1):
        try:
            basis, P_int, D, sh = fit_basis_to_int64(
                [flat[:, i] for i in idx], int(flat.max()), bands)
        except ValueError:
            break
        M = _mat_from_pixels(basis)
        fl = flat >> sh
        A = P_int @ fl                         # (k_cur, n) scaled abundances
        recon = M @ A                          # scaled by D
        resid = fl.astype(np.int64) * D - recon
        r2 = np.abs(resid).sum(axis=0)         # L1: no squaring, no overflow
        for chosen in idx:
            r2[chosen] = -1
        nxt = int(np.argmax(r2))
        if r2[nxt] <= 0:
            break
        idx.append(nxt)
    return [flat[:, i].copy() for i in idx], idx


def unmix_exact_cube(cube, endmembers):
    """Exact abundances for every pixel.

    Returns (A_scaled, D): A_scaled[j] is the abundance map of endmember j,
    scaled by D. True abundance = A_scaled / D, carried exactly.
    """
    bands = cube.shape[0]
    H, W = cube.shape[1], cube.shape[2]
    flat = cube.reshape(bands, -1).astype(np.int64)
    basis, P_int, D, sh = fit_basis_to_int64(endmembers, int(flat.max()), bands)
    A = P_int @ (flat >> sh)
    return A.reshape(-1, H, W), D, basis, sh


def reconstruction_residual(cube, basis, A_scaled, D, shift):
    """Exact per-pixel residual of the mixing model, scaled by D.

    A pixel with residual zero is EXACTLY explained by the endmember set —
    a decision, not a score. Float pipelines can never make this statement.
    """
    bands = cube.shape[0]
    M = _mat_from_pixels(basis)
    flat = (cube.reshape(bands, -1).astype(np.int64) >> shift)
    recon = M @ A_scaled.reshape(A_scaled.shape[0], -1)
    resid = flat * D - recon
    return np.abs(resid).sum(axis=0).reshape(cube.shape[1], cube.shape[2])
