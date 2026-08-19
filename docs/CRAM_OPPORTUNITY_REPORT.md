# CRAM_OPPORTUNITY_REPORT.md
Surface: classical forensic digital-image-processing pipeline (the target this
build replaces). Entries appended by the CRAM-DF build session, 2026-08-19.

[1] FORCED | a1 | classical-DIP:PCA/ICA blind separation (float substrate) | float inversion of the mixing model leaves residual and is ill-conditioned under non-linearity | → node:a1-defloat (authored: cram_df/unmix.py — Rational-Grid Exact Unmixing, zero residual at rational operator; see [6]) | ARCHITECTURE.md
[2] FORCED | hot-path-reconstruction | classical-RNS/DIP magnitude & banding via positional decode | O(k²) MRC-shaped assumptions; banding done by decoding magnitude | → node:reconstruction-retirement (authored: cram_df/core.py — KELD + tower_k, winding read residue-natively) | ARCHITECTURE.md
[3] FORCED | a1 | float convolution (FFT) in enhancement chains | Gibbs ringing, platform-dependent drift, irreversibility | → node:a1-defloat (authored: cram_df/transforms.py — NTT over CLASS-F P=998244353, exact + check-laned) | ARCHITECTURE.md
[4] CANDIDATE | crt-to-cram-substrate | LSB/bit-plane forensics locked to base 2 | base-2 planes are in-band with binary processing history; out-of-band lanes (7,11,13) decorrelate | → node:crt-to-cram-substrate (authored: core.selective_delta lane comb — CRT alias rejection witnessed: 12≡1 mod 11 decoy rejected) | ARCHITECTURE.md
[5] FORCED | a1 | any float op on evidence (blur/resample) | erases quantization fingerprints and Δ=1 structure irreversibly — witnessed T3/T9 (26/114 edges lost + 682 contaminating fires; 28→0 fingerprint blocks) | → node:a1-defloat (authored: forensics.quant_fingerprint_map + Ledger receipts guarantee original recoverability) | ARCHITECTURE.md
[6] CANDIDATE | sequential-to-heterogeneous | per-pixel sequential enhancement chains | lanewise residue ops apply as one mass application; Phase-2 Rust/NEON port per MANA pattern | → node:sequential-to-heterogeneous (pending — Phase 2) | ARCHITECTURE.md
