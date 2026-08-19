# Forensic Standards Reference (dsp-analyst)

Collected 2026-08-19 from primary sources. This file is the compliance layer:
what the established forensic-imaging world requires, where its methods are
strong, and where their documented limits are.

## 1. SWGDE document registry (the governing best practices)

The Scientific Working Group on Digital Evidence maintains the de facto US
standards. Current imaging set (versions as published):

| Document | ID / version | What it governs |
|---|---|---|
| Guidelines for Forensic Image Analysis | 16-I-002-2.0 (2025-03) | The umbrella: tasks split into Photographic Comparison, Content Analysis, and Image Authentication |
| Best Practices for Image Authentication | 18-I-001-2.0 (2025-03) | Manipulation, creation, and consistency examinations; includes the examination flowchart and reporting form |
| Best Practices for Maintaining the Integrity of Imagery | 17-I-001-1.1 (2025-03) | Integrity vs authentication distinction; hashing; original preservation |
| Best Practices for Image Content Analysis | 16-I-001-1.2 (2024-08) | Content-based interpretation |
| Digital Image Compression and File Format Guidelines | 16-M-001-3.0 (2024-03) | Compression handling |
| Forensic Use of Photogrammetry / Reverse Projection Photogrammetry | 2022 pair | Measurement from imagery |
| Technical Overview for Forensic Image Comparison | 2019 | Comparison methodology |
| Best Practices for Digital Video Authentication | 23-V-001-1.2 | Video-specific authentication |

Key doctrinal points to carry:

- **Definitions.** Integrity = complete and unaltered since acquisition.
  Authentication = the content is an accurate representation of what it
  purports to be. Provenance = time, place, manner of creation. These are
  distinct findings; never blur them.
- **Original preservation is absolute** — processing applies only to working
  copies; document every step so a competent third party can reproduce it.
- **Chain of custody + hashing** are expected as documented procedure, not
  an optional extra. (CRAM-DSP's ledger exceeds this: the hash chain covers
  every operation, not just files at rest.)
- **Metadata is never trusted in isolation** — susceptible to alteration
  without affecting playback; use multiple validated extraction tools and
  corroborate against structure and content.
- **Authentication conclusions are asymmetric.** A thorough negative exam
  supports "unlikely manipulated," never proves it; detected alteration can
  be definitive the other way. Phrase findings as supporting / inconsistent
  with propositions.
- **Manipulation taxonomy** used by 18-I-001: alteration, compositing,
  morphing, and image generation. For generated-human detection the document
  points at hard-to-synthesize physical detail (skin-to-skin and
  skin-to-object contact, fine hair/skin structure, translucency, pore-level
  texture, anatomical counts) — and warns these can be masked by luminance
  changes and reprocessing.

## 2. Examination structure (house-adapted)

SWGDE-shaped, CRAM-hardened:

1. **Intake & integrity**: hash originals; ledger receipt; work on copies.
2. **Structure**: format, quantization tables, EXIF/XMP, encoder traces.
3. **Global**: lattice/fingerprint characterization (exact), compression
   history, noise character.
4. **Local**: exact copy-move; splice fingerprint discontinuities; geometry
   and lighting consistency; region-wise sensor-noise consistency where a
   reference exists.
5. **Generation screening**: §4 below.
6. **Report**: findings + limitations + reproducibility package.

## 3. PRNU / sensor attribution — capability and caveats

Photo-Response Non-Uniformity is sensor-level pattern noise from wafer
imperfections; it acts as a device fingerprint for (a) source camera
identification, (b) image-region integrity (a spliced region's PRNU won't
match), (c) device linkage.

Carry these caveats whenever PRNU is invoked:

- **Error rates are condition-dependent.** The court-approved algorithm's
  error rates were established on large sets without distinguishing image
  brightness; dark/bright images shift false-positive behavior, and one
  large Flickr-based study reported false-positive rates as high as 99.2%
  under adverse conditions. Never quote a global error rate without
  conditions.
- **Modern smartphones destabilize PRNU.** Computational photography and
  in-camera processing introduce Non-Unique Artifacts (NUA) shared across
  devices; same-model interclass similarity raises false positives; recent
  vendor-side processing can leak or distort fingerprints.
- **PRNU is spoofable.** 2025 work demonstrates *transfer attacks* injecting
  one device's PRNU into another source's images (including AI-generated),
  defeating commercial authentication tooling at an ~85% average compromise
  rate. Treat a PRNU match as one signal in a fused examination, never
  sufficient alone — and treat PRNU *mismatch* on heavily processed
  smartphone imagery gently.
- Extraction is sensitive to scene content, compression, resizing,
  denoising, and reference-set size.

House note: CRAM-DSP's exact per-block statistics (requantization gcd, class
maps) are complementary evidence — different physical origin (processing
history vs sensor), exactly computable, and immune to the float-pipeline
degradation that plagues PRNU workflows.

## 4. AI-generation screening (state of play, 2026)

Layered doctrine — no single layer decides:

1. **Provenance layer (C2PA / Content Credentials).** Open standard
   (spec v2.x, 2025–26) with broad coalition adoption: Adobe, Microsoft,
   Google, OpenAI (DALL-E/Sora), camera vendors shipping capture-time
   signing. EU AI Act Article 50 transparency obligations apply from
   2026-08-02, which C2PA assertions can satisfy. **Limits, stated
   plainly:** the manifest certifies *history, not truth*; absence of a
   manifest proves nothing (re-encoding and screenshots strip it; major
   generators like Midjourney still don't embed as of early 2026); and
   real photos routinely lose valid credentials to platform re-encoding.
   Firmware-level signing vulnerabilities have been documented — a valid
   signature is strong but not absolute.
2. **Watermark layer.** SynthID (Google) and comparable schemes detect only
   their own ecosystems' outputs. Coverage gaps are structural, and 2026
   research shows the provenance and watermark layers can even be
   desynchronized against each other.
3. **Artifact layer.** Statistical/frequency/noise inconsistencies; trained
   classifiers run roughly 70–90% true-positive with 5–15% false-positive
   on real photos in the wild, degrade under crop/resize/compress (the
   NTIRE 2026 robust-detection challenge exists precisely because this is
   unsolved), and current-generation models add synthetic sensor noise
   adversarially.
4. **Physical-consistency layer.** SWGDE's human-depiction criteria;
   lighting/shadow/geometry coherence; scene physics.

Verdict language: report which layers were checked, what each showed, and
the confidence asymmetry. "No AI indicators found" ≠ "not generated."

House note: for CRAM-DSP *outputs* the question inverts — reviewers ask
"how do we know your recovery is real?" The answer of record: nothing is
generated; every value is an exact function of measured input; the pipeline
is receipt-chained and bit-reproducible. That statement is stronger than any
detector and should be made verbatim.

## 5. Admissibility posture

- Methods should be validated, documented, reproducible by a competent
  third party, with known limitations stated — the practical shape of
  Daubert-style scrutiny (testability, known error characteristics,
  standards, general acceptance).
- Tool validation: use validated tools; corroborate across independent
  tools where interpretation matters (SWGDE's metadata rule generalizes).
- The CRAM-DSP reproducibility certificate (identical chain hash across
  independent runs) directly serves the "can another examiner reproduce it"
  question; cite it in the tool-validation section of reports.
- Never offer legal conclusions; offer technical findings in
  supports / inconsistent-with form.
