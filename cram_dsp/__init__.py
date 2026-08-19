"""CRAM-DSP — residue-native forensic digital processing engine.

Modules:
  core        — Safe Basis, DualTrack star-family K-Elimination, KELD,
                Shadow-11 probes, lane-comb selective differencing
  transforms  — exact NTT convolution, reversible RCT / ChromaDI / 5-3 wavelet
  unmix       — Rational-Grid Exact Unmixing (recto-verso bleed-through)
  forensics   — provenance ledger (hash-chained receipts), copy-move,
                quantization-fingerprint splice localization
  synth       — deterministic integer evidence generators
  baseline_float — QUARANTINED classical float foils (comparison only)
  a1_lint     — static A1 compliance scanner
"""

from . import core, transforms, unmix, forensics, synth  # noqa: F401
