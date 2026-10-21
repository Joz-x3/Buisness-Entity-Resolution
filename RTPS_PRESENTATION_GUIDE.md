# RTPS REVIEW & VIVA PRESENTATION GUIDE
## AWS ML Challenge 2026: Multi-Source Business Entity Resolution
**Team**: TECHNOBLADE  
**Model Architecture**: 2-Stage Hybrid Architecture (Candidate Blocker + LightGBM/XGBoost Ensemble)

---

## 1. Quick Start: How to Run the Live Demo for Review Staff

In your terminal / PowerShell prompt, run:
```bash
python rtps_review_demo.py
```
> **What this does:**
> - Loads the trained LightGBM + XGBoost Ensemble model (`models/final_model/model.pkl`).
> - Evaluates 14,750 validation candidate pairs across 20 similarity features.
> - Prints an **Executive Performance Table** with Accuracy (95.95%), Precision (85.63%), Recall (99.60%), F1 (0.9209), Macro F0.5 (0.8810), and ROC-AUC (0.9915).
> - Displays a **Formatted Confusion Matrix** with TN, FP, FN, TP breakdowns.
> - Ranks the **Top 8 Feature Importances** (Length differences, Jaro-Winkler, Levenshtein, Address token overlap).
> - Runs **4 Live Benchmark Scenarios** showing the model solving typos, suffix differences, and rejecting false matches.
> - Automatically generates 4 publication-quality 300 DPI PNG charts into `rtps_presentation_assets/` for PPT slides!

---

### If the Staff Asks for an Interactive Demo (Custom Input):
Run:
```bash
python rtps_review_demo.py --interactive
```
*Allows the staff to type any two business names, street addresses, and countries to see the model compute features and predict match probability live!*

---

## 2. Summary of Key Performance Metrics

| Evaluation Metric | Recorded Value | Plain-English Explanation for Staff |
| :--- | :---: | :--- |
| **Accuracy** | **95.95%** | Percentage of all candidate pairs correctly classified as matches or non-matches. |
| **Macro F0.5 Score** | **0.8810** | **The official competition metric.** Weights Precision 2x heavier than Recall to heavily penalize incorrect mergers. |
| **ROC-AUC** | **0.9915** | Near-perfect ranking capability; indicates the model separates true matches from false candidates with 99.1% probability. |
| **Precision** | **85.63%** | Out of all predicted matches, 85.6% are genuine ground-truth matches (minimizes false company mergers). |
| **Recall (Sensitivity)** | **99.60%** | The pipeline captures almost all true matching entities across disparate sources (only 14 missed out of 3,493). |
| **F1-Score** | **0.9209** | Standard harmonic mean of Precision and Recall. |
| **Specificity (TNR)** | **94.81%** | True Negative Rate — accurately recognizes distinct businesses and singletons. |
| **Inference Speed** | **~113,000 pairs/sec** | High-throughput C++ accelerated RapidFuzz feature extraction + vectorized tree evaluation. |

---

## 3. Confusion Matrix Breakdown (Auditing Predictions)

| Confusion Matrix Metric | Count | Percentage | Real-World Impact |
| :--- | :---: | :---: | :--- |
| **True Negatives (TN)** | **10,673** | **72.4%** | Accurately rejected non-matching business candidate pairs. |
| **True Positives (TP)** | **3,479** | **23.6%** | Successfully identified and linked matching business entities across sources. |
| **False Positives (FP)** | **584** | **4.0%** | False linkages (kept low via our 0.55 threshold optimization). |
| **False Negatives (FN)** | **14** | **0.1%** | Only 14 true matches were missed out of 3,493. |

---

## 4. Visual Presentation Assets (Located in `rtps_presentation_assets/`)

Insert these charts into your PPT presentation slides or lab record:
- **`rtps_master_dashboard.png`**: **Unified 4-in-1 Master Dashboard** (combines Confusion Matrix, ROC, Features, and Optimization in one view).
- **`1_confusion_matrix.png`**: High-resolution heatmap of True/False Positives/Negatives.
- **`2_roc_curve.png`**: Clean ROC curve showing AUC = 0.9915 against diagonal random guessing.
- **`3_feature_importance.png`**: Horizontal bar chart of top predictive features by split gain.
- **`4_threshold_optimization.png`**: Optimization curve demonstrating why threshold **0.55** was selected to maximize the F0.5 objective.

*Note: When you run `python rtps_review_demo.py`, this master 4-in-1 window automatically pops up on your screen live for the lab staff to inspect!*

---

## 5. Frequently Asked Questions (Viva / Review Defense)

### Q1: "Why did you optimize for Macro F0.5 instead of Standard Accuracy or F1?"
> **Answer**:  
> In business record linkage and entity resolution, merging two completely different companies into one entity (False Positive) is catastrophic for financial and legal records. Conversely, missing a match (False Negative) is much less harmful. F0.5 assigns **double the weight to Precision** compared to Recall ($F_\beta$ with $\beta=0.5$). Simple accuracy is misleading here because negative pairs vastly outnumber positive pairs (class imbalance).

### Q2: "How does the pipeline handle 12+ Million records without running out of RAM?"
> **Answer**:  
> A naive Cartesian product ($1.73 \times 10^6 \times 10 \times 10^6$) yields over **17 Trillion comparisons**. We solved this through:
> 1. **Country Partitioning**: Processing each country in independent memory partitions.
> 2. **Candidate Blocking (Stage 1)**: Using lexical 4-character prefix hashing and word inverted index lookups. This discards **>99.8% of non-matches** before feature engineering, keeping only the top 12 most probable candidates per entity.
> 3. **Streaming TSV Chunks**: Generator pipelines with 250,000-row chunks ensure memory remains strictly under 4 GB.

### Q3: "Why did you use an Ensemble of LightGBM and XGBoost?"
> **Answer**:  
> - **LightGBM** uses fast histogram-based tree splitting and handles sparse token similarities exceptionally well with minimal latency.
> - **XGBoost** applies exact second-order gradient Hessian regularization, preventing tree overfitting on rare lexical combinations.
> - Combining their probability predictions via **50/50 soft voting** provides smoother decision boundaries and improved our validation score by ~2.5% over any single model.

### Q4: "What features contribute the most to identifying matching records?"
> **Answer**:  
> As shown in our Feature Importance analysis:
> 1. `name_len_diff_ratio`: Character length difference ratio (detects abbreviations vs full titles).
> 2. `name_seq_ratio`: Sequence similarity ratio.
> 3. `addr_seq_ratio`: Normalized address sequence similarity.
> 4. `name_jaro_winkler`: Jaro-Winkler distance, which assigns higher weight to matching prefixes and compensates for human spelling typos.
> 5. `addr_token_overlap_ratio`: Overlap of address street names and postal numbers.
