# Glyph form vocabulary — dihedral sector codes

Run: `python3 analysis/dresden_vocab.py`.
Receipts: `data/dresden/vocab_receipts.json`.

**7 exact checks, 2 failures.**

  FAIL — sector code invariant to rot90 under dihedral matching
  FAIL — sector code invariant to mirror under dihedral matching
Threshold sweep (permille of NN dist -> threshold, families, largest, edges): 5->553: 1 fam, max 4, 46 e; 10->655: 2 fam, max 7, 98 e; 20->796: 11 fam, max 11, 236 e; 50->1036: 22 fam, max 73, 732 e; 100->1350: 14 fam, max 231, 1874 e; 250->2069: 9 fam, max 974, 5068 e
Chosen by rule (largest threshold with max cluster <= 200): permille 50, threshold 1036.
Form vocabulary: 7834 cells, threshold 1036, 22 families (size >= 4), size spectrum [73, 40, 39, 15, 15, 11, 10, 9, 9, 6, 6, 5]...
Contact sheets: data/dresden/derived/clusters/family_NN.png (top 22 families, every member page-labelled).

| Family | Size | Pages reached | Sheet |
|---|---|---|---|
| 1 | 73 | 5,8,9,10,11,13,18,22,23,24,30,32,40,42… | `derived/clusters/family_01.png` |
| 2 | 40 | 2,6,7,9,10,18,20,21,22,24,34,40,44,45… | `derived/clusters/family_02.png` |
| 3 | 39 | 7,9,10,15,24,39,41,44,51,52,53,54,55,56… | `derived/clusters/family_03.png` |
| 4 | 15 | 4,12,15,16,17,29,33,35,42,44,56,60,28*** | `derived/clusters/family_04.png` |
| 5 | 15 | 5,10,11,15,17,18,19,22,23,42,52,53,55,56 | `derived/clusters/family_05.png` |
| 6 | 11 | 8,10,13,15,40,51,52 | `derived/clusters/family_06.png` |
| 7 | 10 | 9,11,52,54,55,61,66 | `derived/clusters/family_07.png` |
| 8 | 9 | 9,10,12,39,44,51,54,57 | `derived/clusters/family_08.png` |
| 9 | 9 | 51,53,55,56,57,58 | `derived/clusters/family_09.png` |
| 10 | 6 | 8,31,38,43,59,61 | `derived/clusters/family_10.png` |
| 11 | 6 | 56,59,66,73,74 | `derived/clusters/family_11.png` |
| 12 | 5 | 1,50,56,58,63 | `derived/clusters/family_12.png` |
| 13 | 5 | 9,18,51,52 | `derived/clusters/family_13.png` |
| 14 | 5 | 18,51,54,58 | `derived/clusters/family_14.png` |
| 15 | 5 | 24,39,45,51,54 | `derived/clusters/family_15.png` |
| 16 | 4 | 3,22,23,52 | `derived/clusters/family_16.png` |
| 17 | 4 | 6,18,51,53 | `derived/clusters/family_17.png` |
| 18 | 4 | 13,24,38,67 | `derived/clusters/family_18.png` |
| 19 | 4 | 38,42,51,52 | `derived/clusters/family_19.png` |
| 20 | 4 | 42,52,53,65 | `derived/clusters/family_20.png` |
| 21 | 4 | 46,56,58,69 | `derived/clusters/family_21.png` |
| 22 | 4 | 52,53,54,61 | `derived/clusters/family_22.png` |
