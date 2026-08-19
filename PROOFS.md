# PROOFS

Every claim the engine makes rests on one of the statements below. Each carries a
proof and a pointer to the exhaustive test that witnesses it in `RESULTS.md`.
Notation: `M`, `A` positive integers with `gcd(M, A) = 1`; `v_M = X mod M`,
`v_A = X mod A`; `k = floor(X / M)`.

---

## P1 — K-Elimination Theorem

**Statement.** For every `X` with `0 <= X < M·A`,
`k = (v_A − v_M) · M⁻¹ (mod A)`, exactly, with `M⁻¹` the inverse of `M` mod `A`.

**Proof.** By the division algorithm `X = kM + v_M`. Reducing mod `A`:
`v_A ≡ kM + v_M (mod A)`, so `v_A − v_M ≡ kM (mod A)`. Since `gcd(M, A) = 1`,
Bézout gives a unique `M⁻¹ (mod A)`; multiplying, `(v_A − v_M)·M⁻¹ ≡ k (mod A)`.
For the bound: `0 ≤ v_M < M` and `X < M·A` give `k = (X − v_M)/M < A`, so
`0 ≤ k < A` and the residue class has exactly one representative in `[0, A)`,
which is therefore `k` itself. ∎

**Consequence (A2).** Magnitude is recovered from two residues by one modular
subtraction and one modular multiply. No lane other than the anchor pair is read,
so no synthetic emission is injected and lane independence survives. Garner and
mixed-radix are never invoked.

**Witnessed.** T1 — exhaustive over `[0, 1332)` on (36, 37); exhaustive over
`[0, 65792)` on (256, 257); exhaustive over `[0, 1,801,800)` on the fully
composite pair (1800, 1001); 200,000 random on (30030, 30031).

---

## P2 — Star-Family Inverse Rule

**Statement.** If `A = cM + 1` for a positive integer `c`, then `M⁻¹ ≡ A − c (mod A)`.

**Proof.** `M·(A − c) = MA − cM = MA − (A − 1) ≡ 0 − A + 1 ≡ 1 (mod A)`. ∎

**Consequence.** The inverse is read off the construction index `c`; no
precomputed constant, no extended-Euclid call at runtime.

**Witnessed.** T1 — every `DualTrack` constructor cross-checks the constructed
inverse against extended Euclid; verified for `c = 1..200` on `M = 36`.

---

## P3 — Adjacency Collapse

**Statement.** If `A = M + 1` (i.e. `c = 1`) then `k = (v_M − v_A) mod A`.

**Proof.** By P2 with `c = 1`, `M⁻¹ ≡ A − 1 ≡ −1 (mod A)`. Substituting into P1:
`k ≡ −(v_A − v_M) ≡ v_M − v_A (mod A)`. ∎

**Consequence.** Winding recovery is a single modular subtraction — multiply-free.

**Witnessed.** T1 — subtraction form equals the general form over all of `[0, 1332)`.

---

## P4 — KELD Exactness

**Statement.** For luminance `L` with `0 ≤ L < M·A`, the band index returned by
KELD equals `floor(L / M)` exactly.

**Proof.** Immediate from P1 with `X = L`: the derived `k` *is* `floor(L/M)`. ∎

**Scope note.** This is the exact statement. The pigment/material table that maps
band index to a physical layer is a per-corpus calibration laid over the exact
index — it is not part of the theorem and is not claimed by it.

**Witnessed.** T2 — exhaustive `0..255` at `M = 36`; exhaustive `0..65535` at
`M = 256`; pixel-perfect band recovery on the synthetic strata page.

---

## P5 — Tower K-Elimination

**Statement.** For pairwise-coprime `m₀, a₁, …, a_n` and `X < m₀·a₁···a_n`, the
ladder that reads digit `j` as `((v_j − x) · P_j⁻¹) mod a_j`, where `P_j` is the
product of levels already resolved and `x` the value known below `P_j`, recovers
`X` and `floor(X/m₀)` exactly in `O(n)` residue-space operations.

**Proof.** By induction. Base: `x = X mod m₀` is exact below `P₁ = m₀`. Step:
suppose `x ≡ X (mod P_j)` and `x` is the representative in `[0, P_j)`. Write
`X = x + t·P_j`. Reducing mod `a_j`: `v_j ≡ x + t·P_j`, so
`t ≡ (v_j − x)·P_j⁻¹ (mod a_j)`, which exists since `gcd(P_j, a_j) = 1` by
pairwise coprimality. As `X < P_j·a_j` at this level, `0 ≤ t < a_j` and the
representative is exact; `x + t·P_j` is then exact below `P_{j+1} = P_j·a_j`. ∎

**A2 note.** Each digit is read against *its own anchor* by P1. This is a ladder
of independent K-Eliminations, not a positional decode of a residue tray: no lane
is a function of all previously visited lanes, so the emission that breaks i.i.d.
in Garner/MRC never occurs.

**Witnessed.** T1 — exhaustive over `[0, 97236)` on the tower (36, 37, 73).

---

## P6 — Lane-Comb Selectivity (and the bit-depth sizing rule)

**Statement.** Let `L = {p₁,…,p_r}` be pairwise coprime with product `P`. For a
target step `δ` and observed step `d`, testing `d ≡ δ (mod p_i)` for every `i` is
equivalent to `d ≡ δ (mod P)`. Hence if `|d| ≤ B` and `|δ| ≤ B` with
`2B < P`, the test fires **iff `d = δ` exactly**. The bound `B = floor((P−1)/2)`
is tight.

**Proof.** The equivalence is CRT. If `d ≡ δ (mod P)` then `P | (d − δ)`, while
`|d − δ| ≤ 2B < P` forces `d − δ = 0`. Tightness: `d` and `d + P` agree in every
lane, so no bound above `P/2` can separate all pairs. ∎

**Consequence — the sizing rule.** The source's bit depth selects the lane set.
Eight-bit evidence (`|d| ≤ 255`) is covered by `{7,11,13}` (P = 1,001, B = 500).
Fourteen-bit evidence (`|d| ≤ 16,383` — see the Archimedes lattice result in
`METRICS.md`) is **not**; it requires the Safe Basis extenders, e.g.
`{11,13,17,19}` (P = 46,189, B = 23,094) or `{7,11,13,17,19}` (P = 323,323,
B = 161,661). S8 is load-bearing for real forensic bit depths.

**Witnessed.** T3 (8-bit selectivity, 100% precision and recall on Δ=+1 ink;
Δ=12 rejected where a single lane aliases it) and T10 (no aliasing within the
bound for three lane sets; tightness exhibited; 14-bit coverage tabulated).

---

## P7 — QR/QNR Complement Straddle Lemma

**Statement.** For `a, b ∈ Z/11Z` nonzero with `a + b ≡ 0 (mod 11)`, exactly one
of `a`, `b` is a quadratic residue.

**Proof.** The Legendre symbol is multiplicative, so
`(b|11) = (−a|11) = (−1|11)·(a|11)`. Since `11 ≡ 3 (mod 4)`, Euler's criterion
gives `(−1|11) = (−1)^5 = −1`. Hence `(b|11) = −(a|11)`, and as `a ≢ 0` the
symbol is `±1`. ∎

**Witnessed.** T3 — exhaustive over all ten ordered nonzero complement pairs.

---

## P8 — Sqr-Carry Fire Set

**Statement.** The carry `C_p(a) = floor(2·(a² mod p)/p)` equals 1 iff
`2·(a² mod p) ≥ p`. For `p = 11` the fire set is `{3, 8}`; for `p = 13` it is
derived identically. `C_p` is a residue-class indicator, not a gradient.

**Proof.** Immediate from the floor: the value is 1 exactly when the doubled
square-residue reaches `p`, and 0 otherwise (it cannot exceed 1 since
`a² mod p < p`). The fire set is computed by enumeration over `Z/pZ`, not
asserted. ∎

**A8 guard.** `Sqr` is refused on lane 7 (the Bridge) programmatically — the call
raises rather than warning.

**Witnessed.** T3 — fire sets derived and then verified exhaustively over
`0..255` for `p = 11` and `p = 13`; the lane-7 refusal is asserted.

---

## P9 — Rational-Grid Exact Unmixing

**Statement.** Given `Yr = q·Sr + p·flip(Sv)` and `Yv = q·Sv + p·flip(Sr)` with
integers `0 ≤ p < q` and `D = q² − p² ≠ 0`, the sources are recovered exactly by
`D·Sr = q·Yr − p·flip(Yv)` and `D·Sv = q·Yv − p·flip(Yr)`, with every division
exact.

**Proof.** `flip` is an involution and linear, so `flip(Yv) = q·flip(Sv) + p·Sr`.
Then `q·Yr − p·flip(Yv) = q²·Sr + pq·flip(Sv) − pq·flip(Sv) − p²·Sr = (q²−p²)·Sr`.
Symmetrically for `Sv`. Exactness of the division follows because the left side
is `D` times an integer matrix by construction. ∎

**Blind estimation.** At the true `(p,q)` the divisibility residual is
identically zero; off it, generically nonzero. This makes the violation count an
exact integer objective, tie-broken by negativity and integer cross-energy — no
float optimization, no local minima.

**Witnessed.** T6 — zero violations and exact equality to ground truth at (3,8);
the blind grid recovers (3,8); the float PCA foil leaves MAE 2.296 / 4.899 on the
same input.

---

## P10 — Kill #113 (Skew-Symmetric Energy Neutrality)

**Statement.** For the periodic central-difference operator `D` on the cyclic
lattice, `⟨I, D I⟩ = 0` identically over `Z`, for every integer image `I`.

**Proof.** `D` is skew-symmetric (`Dᵀ = −D`) because the periodic shift is
orthogonal and `D = S − S⁻¹`. For any real vector `x`, `xᵀDx = (xᵀDx)ᵀ = xᵀDᵀx =
−xᵀDx`, hence `xᵀDx = 0`. Over `Z` the identity holds exactly with no rounding. ∎

**Consequence.** Iterative filtering cannot leak energy into synthetic
high-frequency noise; the classical concern that band subtraction *amplifies
noise* (conceded by the incumbent stack — see `PRIOR_ART.md`) does not arise
from this operator.

**Witnessed.** T5 — exactly zero on 50 random images, both axes.

---

## P11 — Reversibility of the Transduction Layer

**Statement.** The LeGall 5/3 integer lifting transform, the JPEG2000 RCT, and
reversible ChromaDI are bijections on integer arrays; forward-then-inverse is the
identity, bit for bit.

**Proof.** Each is a composition of lifting steps of the form
`y_i ← x_i + f(x_{j≠i})` with `f` integer-valued. Any such step is invertible by
`x_i ← y_i − f(x_{j≠i})`, since `f`'s arguments are untouched by the step. A
composition of bijections is a bijection. Boundary handling uses the clamped
neighbour rule identically in both directions, so the inverse sees the same `f`
arguments. ∎

**Witnessed.** T5 — 400 random 1-D round trips; 18 shape/level combinations in 2-D
including odd and degenerate shapes at 16-bit; 200,000 random RCT triples; 5-band
ChromaDI — all bit-exact.

---

## P12 — Provenance as a Reproducibility Certificate

**Statement.** Under A1 the pipeline is a deterministic integer function of its
input. Therefore two executions on identical input produce identical outputs, and
the SHA-256 hash chain over `(operation, parameters, input digest, output digest)`
is equal across executions iff the computations agree.

**Proof.** Determinism: every operation is integer arithmetic with no
floating-point rounding mode, no platform-dependent transcendental, and no
unordered reduction; hence the output bytes are a function of the input bytes
alone. Chain equality: the chain is a fold of a collision-resistant hash over the
receipt sequence, so equal chains imply equal sequences up to hash collision, and
differing sequences imply differing chains. ∎

**Why it does not hold for the incumbents.** A float pipeline's output depends on
compilation, library version, and instruction set, so no chain hash can be
committed to in advance. This is the axis on which no comparator competes — and
it is the question the Vesuvius Challenge posted as unsolved (`PRIOR_ART.md`).

**Witnessed.** T7 — round-trip receipt true; two independent runs produce the
identical chain head; receipts exported.

---

## P13 — A3 Distortion Certificate is Trivial Here

**Statement.** Every lane operator on the production path is a standard CRT ring
homomorphism; therefore the effective forbidden set equals the base forbidden set
and the distortion ratio is `Γ = 1`.

**Proof.** Law A3 requires an exact pullback certificate
`F_eff = (root ∘ post)⁻¹(F_base)` for operator-distorted arithmetic. Here
`root = post = id` on every production lane, so `F_eff = F_base` and
`Γ = |F_eff|/|F_base| = 1`. ∎

**Scope.** The one non-homomorphic construct, `Sqr` on the shadow lanes, is used
strictly as a read-only probe (its output is a mask, never fed back into
arithmetic), so it does not enter the certificate. `Sqr` on lane 7 is refused.

---

## Standing guards

- **Modular inverses** are computed by extended Euclid (`pow(a, -1, m)`) only.
  Fermat's `pow(a, m-2, m)` is silently wrong on composite and anchor moduli and
  is never used.
- **DKAM.** The only degree-2 operator is the shadow probe; the transport core's
  resonance order is `ρ = 3 > d = 2`, so the torus stays subcritical.
- **A1.** Enforced statically by `cram_dsp/a1_lint.py` as part of every harness
  run; the classical foils are quarantined by name and never on a production path.
