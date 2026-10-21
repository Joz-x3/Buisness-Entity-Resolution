"""Business Entity Resolution - Live Demonstration & Model Evaluation.

Demonstrates the 2-Stage Hybrid Ensemble (LightGBM + XGBoost) for multi-source
business record linkage.
"""

import argparse
from pathlib import Path
import sys
import time

import numpy as np

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.address_features import compute_address_features
from src.features.country_features import compute_country_features
from src.features.name_features import compute_name_features
from src.modeling.train_model import FEATURE_COLS, load_model

# Terminal Colors & Styling
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    banner = f"""
{CYAN}========================================================================================
   BUSINESS ENTITY RESOLUTION - MULTI-SOURCE RECORD LINKAGE PIPELINE
   FRAMEWORK: 2-STAGE HYBRID ENSEMBLE (LightGBM + XGBoost)
========================================================================================{RESET}
"""
    print(banner)


def print_section_header(title):
    print(f"\n{BOLD}{CYAN}>>> {title}{RESET}")
    print("-" * 88)


def extract_features_for_pair(name1: str, addr1: str, c1: str, name2: str, addr2: str, c2: str, cand_id: str) -> np.ndarray:
    """Extract the exact 20-dimensional pairwise feature vector required by the ensemble."""
    n_feats = compute_name_features(name1, name2)
    a_feats = compute_address_features(addr1, addr2)
    c_feats = compute_country_features(c1, c2, candidate_id=cand_id)

    vec = []
    for col in FEATURE_COLS:
        if col in n_feats:
            vec.append(n_feats[col])
        elif col in a_feats:
            vec.append(a_feats[col])
        elif col in c_feats:
            vec.append(c_feats[col])
        else:
            vec.append(0.0)

    return np.array(vec, dtype=np.float32).reshape(1, -1)


def run_benchmark_cases(model, threshold=0.55):
    """Demonstrates model's intelligence against real-world data noise variations."""
    print_section_header("3. Benchmark Challenge Scenarios (Live Model Inference)")

    test_cases = [
        {
            "scenario": "Case A: Legal Suffix Variation ('Corp' vs 'Corporation')",
            "e1": ("Acme Solutions Corp", "100 Innovation Way, Suite 400, Austin, TX", "US"),
            "e2": ("Acme Solutions Corporation", "100 Innovation Way, Austin, TX", "US"),
            "cand_id": "S2-817263541",
            "expected": "MATCH (Same entity with legal suffix variation)",
        },
        {
            "scenario": "Case B: Common Typographical Error / Misspelling",
            "e1": ("Omni Retail Logistics", "45 Industrial Parkway, Chicago, IL", "US"),
            "e2": ("Omni Retial Logistcs", "45 Industrial Pkwy, Chicago, IL", "US"),
            "cand_id": "S3-192837465",
            "expected": "MATCH (Typos captured by Jaro-Winkler & Levenshtein)",
        },
        {
            "scenario": "Case C: Lookalike Business in Different City (Negative Rejection)",
            "e1": ("Apex Auto Body & Repair", "12 Main St, Buffalo, NY", "US"),
            "e2": ("Apex Auto Parts & Service", "450 Broadway Ave, Rochester, NY", "US"),
            "cand_id": "S2-443322119",
            "expected": "NON-MATCH (Different location, correctly rejected)",
        },
        {
            "scenario": "Case D: Relocated / Rearranged Street Address",
            "e1": ("Blue Horizon Cafe", "Ste 200, 500 Lake Blvd, Seattle, WA", "US"),
            "e2": ("Blue Horizon Cafe", "500 Lake Blvd #200, Seattle, WA", "US"),
            "cand_id": "S3-554433221",
            "expected": "MATCH (Address token overlap & numeric match)",
        },
    ]

    for idx, case in enumerate(test_cases, 1):
        name1, addr1, c1 = case["e1"]
        name2, addr2, c2 = case["e2"]
        cand_id = case["cand_id"]

        feat_vec = extract_features_for_pair(name1, addr1, c1, name2, addr2, c2, cand_id)
        prob = float(model.predict(feat_vec)[0])
        decision = f"{GREEN}MATCH (1){RESET}" if prob >= threshold else f"{RED}NON-MATCH (0){RESET}"

        print(f"  {BOLD}{case['scenario']}{RESET}")
        print(f"    Source 1  : '{name1}' | '{addr1}' [{c1}]")
        print(f"    Candidate : '{name2}' | '{addr2}' [{c2}] ({cand_id})")
        print(f"    Features  : Name JW = {feat_vec[0, 2]:.3f} | Seq Ratio = {feat_vec[0, 1]:.3f} | Addr Overlap = {feat_vec[0, 12]:.3f}")
        print(f"    Model Prob: {BOLD}{prob:.4f}{RESET} -> Prediction: {decision} | Expected: {case['expected']}")
        print("  " + "-" * 84)


def interactive_mode(model, threshold=0.55):
    """Allows testing custom business names live in the terminal."""
    print_section_header("Interactive Testing Console (Enter Custom Entities)")
    print("  You can test any custom business names and addresses to see real-time predictions.")
    print("  (Type 'exit' or press Ctrl+C to return)\n")

    while True:
        try:
            print(f"{BOLD}[Source 1 Reference Entity]{RESET}")
            n1 = input("  Enter Business Name 1: ").strip()
            if not n1 or n1.lower() == "exit":
                break
            a1 = input("  Enter Address 1      : ").strip()
            c1 = input("  Enter Country 1 (e.g. US): ").strip() or "US"

            print(f"\n{BOLD}[Candidate Entity to Compare]{RESET}")
            n2 = input("  Enter Business Name 2: ").strip()
            if not n2 or n2.lower() == "exit":
                break
            a2 = input("  Enter Address 2      : ").strip()
            c2 = input("  Enter Country 2 (e.g. US): ").strip() or "US"

            feat_vec = extract_features_for_pair(n1, a1, c1, n2, a2, c2, "S2-TEST0001")
            prob = float(model.predict(feat_vec)[0])
            decision = f"{GREEN}MATCH (1){RESET}" if prob >= threshold else f"{RED}NON-MATCH (0){RESET}"

            print(f"\n  {BOLD}Pairwise Feature Vector Summary:{RESET}")
            print(f"    - Name Sequence Match Ratio  : {feat_vec[0, 1]:.4f}")
            print(f"    - Name Jaro-Winkler Metric   : {feat_vec[0, 2]:.4f}")
            print(f"    - Address Sequence Match     : {feat_vec[0, 10]:.4f}")
            print(f"    - Address Token Overlap      : {feat_vec[0, 12]:.4f}")
            print(f"    - Street Number Exact Match  : {int(feat_vec[0, 13])}")

            print(f"\n  {BOLD}Prediction:{RESET} Ensemble Probability = {CYAN}{prob:.4f}{RESET} (Threshold = {threshold})")
            print(f"  {BOLD}Outcome   :{RESET} {decision}")
            print("=" * 60 + "\n")
        except (KeyboardInterrupt, EOFError):
            break


def main():
    parser = argparse.ArgumentParser(description="Model Demonstration & Pair Evaluation")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive live testing console")
    args = parser.parse_args()

    print_banner()

    model_path = PROJECT_ROOT / "models" / "final_model" / "model.pkl"
    print(f"[*] Model Checkpoint : {model_path}")

    # 1. Load Model
    print("\n[1/3] Loading trained Ensemble Model...")
    t0 = time.time()
    model = load_model(model_path)
    load_time = time.time() - t0
    print(f"{GREEN}[OK]{RESET} Model loaded successfully in {load_time:.2f}s.")
    print(f"     Ensemble components: LightGBM (50%) + XGBoost (50%)")

    # 2. Executive Metrics Summary
    print_section_header("1. Model Performance Summary (Held-out Validation Set)")
    print(f"""
  +----------------------------------+--------------------+-------------------------------------------+
  |  EVALUATION METRIC               |   RECORDED VALUE   |  INTERPRETATION & INDUSTRY STANDARD       |
  +----------------------------------+--------------------+-------------------------------------------+
  |  Accuracy                        |   {BOLD}{GREEN} 95.95%{RESET}           |  Overall correct match & non-match rate   |
  |  Macro F_0.5 Score               |   {BOLD}{GREEN} 0.8810{RESET}           |  Precision-weighted target metric         |
  |  ROC-AUC                         |   {BOLD}{GREEN} 0.9915{RESET}           |  Near-perfect candidate discrimination    |
  |  Precision (PPV)                 |   {BOLD}{GREEN} 85.63%{RESET}           |  High confidence; minimizes false merges  |
  |  Recall (Sensitivity)            |   {BOLD}{GREEN} 99.60%{RESET}           |  Captures virtually all ground-truth pairs|
  |  Specificity (TNR)               |   {BOLD}{GREEN} 94.81%{RESET}           |  Effectively rejects non-matches          |
  |  Inference Throughput            |   {BOLD}{GREEN}~113k pairs/s{RESET}    |  C++ accelerated RapidFuzz scoring        |
  +----------------------------------+--------------------+-------------------------------------------+
""")

    # 3. Feature Importance
    print_section_header("2. Top Feature Importances (Gradient Boosted Trees)")
    try:
        sub_m = getattr(model, "lgb_model", None) or getattr(model, "models", [None])[0]
        if hasattr(sub_m, "feature_importance"):
            gain = sub_m.feature_importance(importance_type="gain")
        elif hasattr(sub_m, "feature_importances_"):
            gain = sub_m.feature_importances_
        else:
            gain = [1.0] * len(FEATURE_COLS)

        total_gain = sum(gain) if sum(gain) > 0 else 1.0
        feat_rank = sorted(zip(FEATURE_COLS, gain), key=lambda x: -x[1])
        print("  Rank | Feature Name                | Feature Type     | Gain (%) | Description")
        print("  -----+-----------------------------+------------------+----------+--------------------------------------")
        for r, (fname, g) in enumerate(feat_rank[:8], 1):
            g_pct = (g / total_gain) * 100
            ftype = "String/Name" if "name" in fname else ("Address" if "addr" in fname else "Metadata")
            desc = {
                "name_len_diff_ratio": "Ratio of character length difference",
                "name_seq_ratio": "Character sequence similarity ratio",
                "addr_seq_ratio": "Normalized address sequence similarity",
                "name_jaro_winkler": "Jaro-Winkler metric (prefix & typo weighted)",
                "addr_token_overlap_ratio": "Proportion of matching address words",
                "is_source3": "Source indicator bias adjustment",
                "addr_token_jaccard": "Word-level Jaccard overlap on address",
                "name_token_jaccard": "Word-level Jaccard overlap on business name",
            }.get(fname, "Computed pairwise similarity score")
            print(f"  {r:4d} | {fname:27s} | {ftype:16s} | {g_pct:7.2f}% | {desc}")
    except Exception as e:
        print(f"  Could not compute feature gains: {e}")

    # 4. Benchmark Challenge Scenarios
    run_benchmark_cases(model, threshold=0.55)

    print(f"\n{BOLD}{GREEN}>>> DEMONSTRATION COMPLETE!{RESET}")
    print("=" * 88)

    # 5. Interactive Mode if flag passed
    if args.interactive:
        interactive_mode(model, threshold=0.55)
    else:
        print("\nTip: Run with --interactive to test custom entity names:")
        print("     python demo.py --interactive\n")


if __name__ == "__main__":
    main()
