# Glyph form vocabulary — dihedral sector codes

Run: `python3 analysis/dresden_vocab.py`.
Receipts: `data/dresden/vocab_receipts.json`.

**7 exact checks, 0 failures.**

Threshold sweep (permille of NN dist -> threshold, families, largest, edges): 5->423: 1 fam, max 5, 51 e; 10->489: 6 fam, max 15, 128 e; 20->615: 4 fam, max 73, 307 e; 50->990: 4 fam, max 302, 951 e; 100->1410: 15 fam, max 496, 1915 e; 250->2145: 12 fam, max 864, 5015 e
Chosen by rule (largest threshold with max cluster <= 500): permille 100, threshold 1410.
Form vocabulary: 7834 cells, threshold 1410, 15 families (size >= 4), size spectrum [496, 109, 9, 8, 6, 6, 6, 6, 6, 6, 5, 5]...
Contact sheets: data/dresden/derived/clusters/family_NN.png (top 15 families, every member page-labelled).

| Family | Size | Pages reached | Sheet |
|---|---|---|---|
| 1 | 496 | 2,4,5,6,7,8,9,10,11,12,13,14,15,16… | `derived/clusters/family_01.png` |
| 2 | 109 | 1,3,4,6,7,8,10,12,13,14,15,16,17,18… | `derived/clusters/family_02.png` |
| 3 | 9 | 23,51,52,54,59,63,73 | `derived/clusters/family_03.png` |
| 4 | 8 | 6,16,20,33,40,47,63,28* | `derived/clusters/family_04.png` |
| 5 | 6 | 3,9,51,54,58,64 | `derived/clusters/family_05.png` |
| 6 | 6 | 5,10,23,44,45,70 | `derived/clusters/family_06.png` |
| 7 | 6 | 9,56,57,61,69 | `derived/clusters/family_07.png` |
| 8 | 6 | 18,22,23,52,67,70 | `derived/clusters/family_08.png` |
| 9 | 6 | 23,42,45,51,52,73 | `derived/clusters/family_09.png` |
| 10 | 6 | 32,51,52,54,56,70 | `derived/clusters/family_10.png` |
| 11 | 5 | 6,22,47,51,59 | `derived/clusters/family_11.png` |
| 12 | 5 | 10,46,53,62,70 | `derived/clusters/family_12.png` |
| 13 | 5 | 15,37,44,55,70 | `derived/clusters/family_13.png` |
| 14 | 4 | 1,38,45 | `derived/clusters/family_14.png` |
| 15 | 4 | 23,50,62 | `derived/clusters/family_15.png` |
