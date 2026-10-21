# ML Challenge 2026: Business Entity Resolution Solution Template

**Team Name:** TECHNOBLADE  
**Team Members:** Andrick Williams, Dhanasekar S, HARI S, JOHITH R  
**Submission Date:** 2026-09-27  

---

## 1. Executive Summary
We present an end-to-end, high-precision Business Entity Resolution (ER) system engineered to resolve noisy multi-source records (Source 2 and Source 3) against a deduplicated reference dataset (Source 1). Our solution combines country-partitioned lexical prefix-blocking with a 20-feature pairwise comparison space accelerated via native C++ fuzzy string algorithms (`rapidfuzz`) and a dual-model ensemble (LightGBM [MIT] and XGBoost [Apache 2.0]) calibrated specifically for macro $F_{0.5}$ precision optimization. The pipeline processes 1.73 million test entities in streaming chunks with constant memory usage, strictly enforcing all output format rules, singleton handling, and subset integrity constraints.

---

## 2. Methodology

### 2.1 Problem Analysis
Exploratory Data Analysis (EDA) on the multi-source dataset revealed key challenge characteristics:
1. **Legal Suffix Inconsistencies:** Heavy variation between standard business suffixes across sources (e.g., `Corp` vs. `Corporation`, `Pvt Ltd` vs. `Private Limited`, `LLC`, `Inc`).
2. **Address Discrepancies:** Landmark-based descriptions (common in Indian records), municipal address reordering, missing PIN codes/postal codes, and abbreviated street names (e.g., `Rd`, `St`, `Ave`).
3. **Open-World Country Generalization:** While training data covered `US` and `India`, test data includes unseen regions (`France`). The matching model must avoid country-specific bias and rely on universal structural, token, and phonetic similarities.
4. **Precision-Oriented Metric ($F_{0.5}$):** The macro $F_{0.5}$ metric weights precision $2\times$ over recall. Incorrectly linking two different businesses (false positive) causes severe score penalties compared to missed matches, necessitating high decision thresholds and strong negative rejection.

### 2.2 Solution Strategy
**Approach Type:** Country-Partitioned Two-Stage ER (Lexical Candidate Blocking + Gradient Boosted Matching Classifier)  
**Core Innovation:** High-throughput streaming candidate blocker coupled with an ensemble of LightGBM and XGBoost trained on 20 discriminative, country-agnostic similarity features. The candidate generation stage enforces a top-$k$ cap ($k=12$) per query record, pruning over 99.8% of pairwise comparisons while retaining high true match recall.

---

## 3. Candidate Generation (Blocking)
To avoid the intractable $O(N^2)$ comparison space over 1.73M entities, candidate generation employs a multi-tiered indexing scheme:

- **Blocking keys used:**
  1. Country partitioning (separate indexes per normalized country).
  2. Character prefix indexing (prefix length = 4).
  3. Cleaned token-level indexing (minimum token length = 3).
- **Candidate pairs generated:**
  - Lexical blocker indexes candidates from Source 2 and Source 3 once per country partition.
  - Queries are capped at $k=12$ most relevant candidates per Source 1 entity, yielding approximately 11–12 candidate pairs per entity.
- **Ensuring true matches are preserved:**
  - Both prefix and token keys are extracted simultaneously so that entities differing only by prefixes or word order are captured in the candidate set.
  - Candidate pairs are exported directly to `candidate_pairs.tsv` to ensure strict subset compliance with `matching_results.tsv`.

---

## 4. Matching Model

**Features used (20 Pairwise Metrics):**
- **Name features:** Exact string match, C++ native Gestalt sequence ratio (`rapidfuzz.fuzz.ratio`), Jaro-Winkler similarity, normalized Levenshtein distance, token Jaccard similarity, token overlap ratio, 3-character and 5-character prefix matching, length difference ratio.
- **Address features:** Exact address match, address fuzzy sequence ratio, address token Jaccard, token overlap ratio, numeric/street number exact match, numeric overlap ratio, presence indicator for both addresses.
- **Text & Metadata features:** Combined text Jaccard similarity, combined text token overlap, candidate source indicator (`S2` vs. `S3`).

**Model type:**
- Ensemble of **LightGBM** (MIT License) and **XGBoost** (Apache 2.0 License).
- 20 country-agnostic continuous features.
- Trees: 300 estimators, max depth 6, learning rate 0.05, subsample 0.8.

**Threshold selection method:**
- The probability output of the ensemble is thresholded at **$0.55$**.
- This threshold was empirically determined via grid search on held-out validation data to maximize macro $F_{0.5}$, penalizing borderline false positives while maintaining high true positive density.

---

## 5. Results & Error Analysis

- **Macro $F_{0.5}$ Score:** $0.842$ on 20% held-out validation split (441,364 entities).
- **Singletons Handling:** Verified that Source 1 entities with no candidate crossing the $0.55$ threshold are assigned an empty `matched_entity_ids` column, scoring $1.0$ under the challenge evaluation rules.
- **Common false positives (wrong merges):** Common brand names or retail outlets sharing generic prefixes (e.g., "Starbucks Coffee" vs. "Starbucks Drive-Thru") at nearby street numbers. Mitigated by numeric overlap and exact address requirements.
- **Common false negatives (missed matches):** Entities where names underwent severe transliteration differences or where address strings were completely missing in one source.

---

## 6. Conclusion
Our solution for the AWS ML Challenge 2026 delivers a robust, scalable, and highly accurate Business Entity Resolution architecture. By combining C++-accelerated lexical candidate filtering with an ensemble of gradient-boosted decision trees, we achieved high macro $F_{0.5}$ precision while maintaining constant-memory streaming performance across 1.73 million test entities.

---

## Appendix

### A. Code Artefacts
The full codebase is structured in the submission package under `code/business_entity_resolution/`:
```
code/business_entity_resolution/
├── src/
│   ├── blocking/          # Lexical and TF-IDF blocking implementations
│   ├── features/          # C++ accelerated name and address feature extractors
│   ├── inference/         # predict_test.py end-to-end streaming inference pipeline
│   ├── modeling/          # Model training, ensembling, and prediction logic
│   ├── preprocessing/    # Normalization, text cleaning, audit, and splitting
│   └── utils/             # Format and constraint validation utilities
├── models/                # Trained LightGBM + XGBoost model artifacts
├── requirements.txt       # Pinned dependencies
└── README.md              # Reproduction instructions
```

**Entry Point:**
```bash
python -u src/inference/predict_test.py --test-dir test --output-dir output --lexical-only
```
This produces `output/matching_results.tsv` and `output/candidate_pairs.tsv`.
Validation is confirmed with `python src/utils/validate_submission.py`.
