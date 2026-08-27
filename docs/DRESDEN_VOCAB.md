# Glyph form vocabulary — dihedral sector codes

Run: `python3 analysis/dresden_vocab.py`.
Receipts: `data/dresden/vocab_receipts.json`.

**7 exact checks, 1 failures.**

Threshold sweep (permille of NN dist -> threshold, families, largest, edges): 5->423: 1 fam, max 5, 51 e; 10->489: 6 fam, max 15, 128 e; 20->615: 4 fam, max 73, 307 e; 50->990: 4 fam, max 302, 951 e; 100->1410: 15 fam, max 496, 1915 e; 250->2145: 12 fam, max 864, 5015 e
Chosen by rule (largest threshold with max cluster <= 200): permille 20, threshold 615.
  FAIL — vocabulary has multiple families
Form vocabulary: 7834 cells, threshold 615, 4 families (size >= 4), size spectrum [73, 26, 5, 5]...
Contact sheets: data/dresden/derived/clusters/family_NN.png (top 4 families, every member page-labelled).

| Family | Size | Pages reached | Sheet |
|---|---|---|---|
| 1 | 73 | 2,5,6,7,8,9,10,12,13,14,15,18,20,21… | `derived/clusters/family_01.png` |
| 2 | 26 | 7,9,21,22,24,44,48,51,52,53,54,56,57,62… | `derived/clusters/family_02.png` |
| 3 | 5 | 7,9,41,53 | `derived/clusters/family_03.png` |
| 4 | 5 | 9,51,55 | `derived/clusters/family_04.png` |
