"""Spectral-axis leverage pass (history-search directed).

Sources recovered from session history:
- spectral-hidden-art skill (2026-06-25 eclipse session): channel-arithmetic
  transform family T-00/T-03/T-05/T-09 — exact per-channel gain/shift
  transforms that activate hidden layers.
- Canonical-spectral law (2026-04-29 executioner session): spectral computed
  once in canonical integers, then encoded; corridor |value| < P/2.

Applied here as: (1) exact fluorescence-quench axis 617*s365 - 365*s617,
(2) ink-difference matched filter d.y with d = e_over - e_under (projection —
the ill-posedness certificate killed INVERSION, not projection), plus the
decisive population check of whether the projection separates the two inks.
Result recorded in docs/SEPARABILITY_CERTIFICATE.md addendum: it does not —
separation 6,363 vs IQR 122,068 (5.2%). The strokes visible on the axis are
ink-vs-parchment re-detected through the correlated component.
"""
# (executable form of the session's heredoc; see git log for the run record)
