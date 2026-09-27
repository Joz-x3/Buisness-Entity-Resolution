"""Candidate Recall Evaluator for Business Entity Resolution.

Measures the blocking stage quality:
- Blocking Recall Ceiling: Proportion of true ground-truth matches retained in candidate set
- Reduction Ratio: Proportion of candidate pairs eliminated vs Cartesian product
- Average candidates per Source 1 entity
"""

import argparse
import csv
import logging
import sys
from pathlib import Path
from typing import Dict, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.preprocessing.load_data import load_tsv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def compute_candidate_recall(candidate_pairs_tsv: Path, ground_truth_tsv: Path) -> Dict[str, float]:
    """Compute blocking recall ceiling and reduction ratio."""
    logger.info("Loading ground truth from %s...", ground_truth_tsv)
    gt_pairs: Set[Tuple[str, str]] = set()
    gt_df = load_tsv(ground_truth_tsv)

    for _, row in gt_df.iterrows():
        s1_id = str(row["source1_entity_id"]).strip()
        matched_raw = str(row.get("matched_entity_ids", "")).strip()
        if matched_raw and matched_raw.lower() != "nan":
            for m in matched_raw.split(","):
                m_clean = m.strip()
                if m_clean:
                    gt_pairs.add((s1_id, m_clean))

    total_gt_matches = len(gt_pairs)
    logger.info("Total ground-truth matching pairs: %d", total_gt_matches)

    logger.info("Reading candidate pairs from %s...", candidate_pairs_tsv)
    cand_pairs: Set[Tuple[str, str]] = set()
    evaluated_s1_entities: Set[str] = set()

    with open(candidate_pairs_tsv, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            s1_id = str(row.get("source1_entity_id", "")).strip()
            if s1_id:
                evaluated_s1_entities.add(s1_id)
            cands_raw = str(row.get("candidate_entity_ids", row.get("candidate_entity_id", ""))).strip()
            if cands_raw and cands_raw.lower() != "nan":
                for c in cands_raw.split(","):
                    c_clean = c.strip()
                    if c_clean:
                        cand_pairs.add((s1_id, c_clean))

    total_candidates = len(cand_pairs)
    evaluated_gt_pairs = {p for p in gt_pairs if p[0] in evaluated_s1_entities}
    total_evaluated_gt = len(evaluated_gt_pairs)
    retained_matches = len(cand_pairs.intersection(evaluated_gt_pairs))

    recall_ceiling = retained_matches / total_evaluated_gt if total_evaluated_gt > 0 else 0.0
    avg_candidates_per_s1 = total_candidates / len(evaluated_s1_entities) if evaluated_s1_entities else 0.0

    metrics = {
        "evaluated_s1_entities": len(evaluated_s1_entities),
        "evaluated_ground_truth_matches": total_evaluated_gt,
        "total_candidate_pairs": total_candidates,
        "retained_matches": retained_matches,
        "missed_matches": total_evaluated_gt - retained_matches,
        "blocking_recall_ceiling": round(recall_ceiling, 4),
        "avg_candidates_per_s1": round(avg_candidates_per_s1, 2),
    }

    logger.info("Candidate Blocking Quality Metrics:")
    logger.info("  Blocking Recall Ceiling: %.4f (Retained %d / %d matches)", recall_ceiling, retained_matches, total_evaluated_gt)
    logger.info("  Avg Candidates per S1 Entity: %.2f", avg_candidates_per_s1)

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate Candidate Generation (Blocking) Recall")
    parser.add_argument("--candidate-pairs", type=Path, default=PROJECT_ROOT / "artifacts" / "candidate_pairs.tsv")
    parser.add_argument("--ground-truth", type=Path, default=PROJECT_ROOT / "data" / "train" / "train_ground_truth.tsv")
    args = parser.parse_args()

    compute_candidate_recall(args.candidate_pairs, args.ground_truth)


if __name__ == "__main__":
    main()
