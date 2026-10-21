"""Generate Clean, Simple 6-Slide RTPS Presentation using the Video Screenshots.

Slides:
1. Problem Statement (with 3-source vendor screenshot)
2. How We Are Going to Solve It (with true match vs look-alike screenshot)
3. What Models Used (Machine Learning Ensemble - LightGBM + XGBoost)
4. Evaluation Metric & Objective (with F0.5 precision-weighted formula screenshot)
5. What Will Be the Output (Format & Performance Results)
6. Evaluation Graphs & 'Why This Graph?' (with 4-in-1 Master Dashboard)
"""

import os
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "rtps_presentation_assets"
OUTPUT_PPTX = PROJECT_ROOT / "Business_Entity_Resolution_RTPS_Review.pptx"

# Screenshots from the video
IMG_PROBLEM = ASSETS_DIR / "WhatsApp Image 2026-10-14 at 10.52.30 AM.jpeg"        # 3 source cards
IMG_MATCHING = ASSETS_DIR / "WhatsApp Image 2026-10-14 at 10.52.30 AM (2).jpeg"    # Linkage to S2, S3, reject look-alike
IMG_METRIC = ASSETS_DIR / "WhatsApp Image 2026-10-14 at 10.52.31 AM.jpeg"          # Macro F0.5 formula & tips
IMG_DASHBOARD = ASSETS_DIR / "rtps_master_dashboard.png"                           # 4-in-1 master graph

# Clean Academic Color Palette
NAVY = RGBColor(20, 35, 65)          # Deep Navy
BLUE = RGBColor(25, 110, 200)        # Primary Accent Blue
LIGHT_BG = RGBColor(246, 249, 252)   # Card Fill
WHITE = RGBColor(255, 255, 255)
TEXT_DARK = RGBColor(35, 45, 60)     # Body Text
MUTED = RGBColor(100, 115, 130)      # Secondary
GREEN = RGBColor(16, 140, 75)        # Metric Green
BORDER = RGBColor(218, 228, 240)     # Card Border


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_slide_header(slide, title, category="REAL-TIME PROJECT SEMINAR (RTPS) | MACHINE LEARNING REVIEW"):
        box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_sub = tf.paragraphs[0]
        p_sub.text = category.upper()
        p_sub.font.size = Pt(10)
        p_sub.font.bold = True
        p_sub.font.color.rgb = BLUE

        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY

    def add_card(slide, left, top, width, height, bg_color=WHITE, border_color=BORDER):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1)
        else:
            shape.line.fill.background()
        return shape

    # =========================================================================
    # SLIDE 1: PROBLEM STATEMENT (with 3-source vendor screenshot)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_slide_header(s1, "Problem Statement: Multi-Source Business Entity Resolution")

    # Left: Concise Problem Points
    card_l1 = add_card(s1, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.4))
    tf1 = card_l1.text_frame
    tf1.word_wrap = True
    tf1.margin_left = tf1.margin_right = Inches(0.35)
    tf1.margin_top = Inches(0.25)

    p = tf1.paragraphs[0]
    p.text = "The Core Problem"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    points1 = [
        ("Objective: ", "Determine which business records from multiple independent databases refer to the exact same real-world business entity."),
        ("Heterogeneous Formats: ", "Source 1 has clean reference records. Source 2 and Source 3 come from secondary vendors with noisy, unstandardized formats."),
        ("No Shared Primary Keys: ", "Databases have no common unique ID or registration number, making simple database joins impossible."),
        ("Real-World Noise: ", "Variations in business names (e.g. 'Inc' vs 'Incorporated', missing words) and rearranged street addresses."),
        ("The Goal: ", "Link each Source 1 business to its exact matching entries in Source 2 and Source 3 automatically using Machine Learning."),
    ]
    for b_title, b_desc in points1:
        p = tf1.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = BLUE
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_DARK

    # Right: Embedded Screenshot from Video (Source 1, 2, 3 representations)
    if IMG_PROBLEM.exists():
        s1.shapes.add_picture(str(IMG_PROBLEM), Inches(6.7), Inches(1.7), Inches(5.8), Inches(4.5))
        # Caption Card
        cap1 = add_card(s1, Inches(6.7), Inches(6.3), Inches(5.8), Inches(0.7), bg_color=LIGHT_BG)
        tf_cap1 = cap1.text_frame
        tf_cap1.word_wrap = True
        tf_cap1.margin_left = Inches(0.2)
        tf_cap1.margin_top = Inches(0.1)
        p = tf_cap1.paragraphs[0]
        p.text = "Illustration: One business entity, three representations, each from a different vendor with NO shared ID."
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY

    # =========================================================================
    # SLIDE 2: HOW WE ARE GOING TO SOLVE IT (Solution Architecture)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_header(s2, "How We Are Going to Solve It: 2-Stage Architecture")

    # Left: Embedded Screenshot from Video (Entity resolution diagram with look-alike rejection)
    if IMG_MATCHING.exists():
        s2.shapes.add_picture(str(IMG_MATCHING), Inches(0.8), Inches(1.7), Inches(5.8), Inches(4.5))
        # Caption Card
        cap2 = add_card(s2, Inches(0.8), Inches(6.3), Inches(5.8), Inches(0.7), bg_color=LIGHT_BG)
        tf_cap2 = cap2.text_frame
        tf_cap2.word_wrap = True
        tf_cap2.margin_left = Inches(0.2)
        tf_cap2.margin_top = Inches(0.1)
        p = tf_cap2.paragraphs[0]
        p.text = "Illustration: Link every Source 1 entity to true matches, and strictly reject similar look-alikes."
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY

    # Right: The 2-Stage Strategy
    card_r2 = add_card(s2, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.4))
    tf2 = card_r2.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_right = Inches(0.35)
    tf2.margin_top = Inches(0.25)

    p = tf2.paragraphs[0]
    p.text = "Our 2-Stage Solution Strategy"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    points2 = [
        ("The Scale Problem: ", "Comparing 1.7M records directly with 10M records produces 17 Trillion pairs (computationally impossible)."),
        ("Stage 1 — Candidate Blocker: ", "Uses fast 4-character prefix hashing and word-token indexing to quickly discard >99.8% of obvious non-matches in constant RAM."),
        ("Stage 2 — ML Classification: ", "Extracts 20 deep similarity features and runs an ML Ensemble on only the top candidate pairs."),
        ("Rejecting Look-Alikes: ", "As shown in the diagram, our model links genuine matches (Acme Robotics Inc -> Acme Robotics) but rejects look-alikes (Acme Bakery LLC)."),
        ("Singletons: ", "Handles entities with zero matches, correctly producing empty match lists without false merges."),
    ]
    for b_title, b_desc in points2:
        p = tf2.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "✔ " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = GREEN
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 3: WHAT MODELS USED (Machine Learning Ensemble)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_header(s3, "What Models Are Used: Machine Learning Ensemble")

    # Left Card: The Ensemble Architecture
    card_m1 = add_card(s3, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.4))
    tf3_l = card_m1.text_frame
    tf3_l.word_wrap = True
    tf3_l.margin_left = tf3_l.margin_right = Inches(0.35)
    tf3_l.margin_top = Inches(0.25)

    p = tf3_l.paragraphs[0]
    p.text = "ML Ensemble: LightGBM + XGBoost"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    m_bullets = [
        ("Why Ensemble? ", "Combining two distinct tree architectures prevents overfitting on noisy spelling patterns and boosts prediction stability."),
        ("Model 1 - LightGBM: ", "Histogram-based gradient boosted decision trees. Extremely fast, memory efficient, and optimized for unbalanced match/non-match data."),
        ("Model 2 - XGBoost: ", "Second-order gradient boosted trees with strict L1/L2 regularization to guard against false merges."),
        ("Soft Voting Formula: ", "Final Match Probability = (0.5 × LightGBM) + (0.5 × XGBoost)"),
        ("Decision Cutoff: ", "If Probability ≥ 0.55 → TRUE MATCH\nIf Probability < 0.55 → REJECT / SINGLETON"),
    ]
    for b_title, b_desc in m_bullets:
        p = tf3_l.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = BLUE
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_DARK

    # Right Card: The 20 Extracted Features
    card_m2 = add_card(s3, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.4))
    tf3_r = card_m2.text_frame
    tf3_r.word_wrap = True
    tf3_r.margin_left = tf3_r.margin_right = Inches(0.35)
    tf3_r.margin_top = Inches(0.25)

    p = tf3_r.paragraphs[0]
    p.text = "20 Pairwise Similarity Features"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    feat_bullets = [
        ("Business Name Features (9):", [
            "Jaro-Winkler Similarity (prefix & typo weighted)",
            "Levenshtein Distance (character edit distance)",
            "Character Sequence Ratio (fuzzy string similarity)",
            "Token Jaccard & Word Overlap Ratio",
            "Name Length Difference Ratio (detects abbreviations)",
        ]),
        ("Address & Street Features (7):", [
            "Street Address Sequence Similarity",
            "Address Word Token Jaccard",
            "Street / Building Number Match (numeric digits)",
            "Postal & Numeric Digit Overlap",
        ]),
        ("Compatibility Features (4):", [
            "Generic Country Match / Mismatch",
            "Source Origin Indicators (Source 2 vs Source 3)",
        ]),
    ]
    for cat_t, items in feat_bullets:
        p = tf3_r.add_paragraph()
        p.space_before = Pt(6)
        p.text = cat_t
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = GREEN
        for it in items:
            p_i = tf3_r.add_paragraph()
            p_i.text = "  ✔ " + it
            p_i.font.size = Pt(10)
            p_i.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 4: EVALUATION METRIC (with Video F0.5 Formula Screenshot)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_header(s4, "Evaluation Metric: Precision-Weighted Macro F0.5")

    # Left: Embedded Screenshot from Video (Macro F0.5 Formula & Guidelines)
    if IMG_METRIC.exists():
        s4.shapes.add_picture(str(IMG_METRIC), Inches(0.8), Inches(1.7), Inches(5.8), Inches(4.5))
        # Caption Card
        cap4 = add_card(s4, Inches(0.8), Inches(6.3), Inches(5.8), Inches(0.7), bg_color=LIGHT_BG)
        tf_cap4 = cap4.text_frame
        tf_cap4.word_wrap = True
        tf_cap4.margin_left = Inches(0.2)
        tf_cap4.margin_top = Inches(0.1)
        p = tf_cap4.paragraphs[0]
        p.text = "Core Rule: A false merge costs about twice as much as a miss, so when unsure, do not merge."
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = NAVY

    # Right: Plain-English Strategy
    card_r4 = add_card(s4, Inches(6.9), Inches(1.6), Inches(5.6), Inches(5.4))
    tf4 = card_r4.text_frame
    tf4.word_wrap = True
    tf4.margin_left = tf4.margin_right = Inches(0.35)
    tf4.margin_top = Inches(0.25)

    p = tf4.paragraphs[0]
    p.text = "Why Macro F0.5 & Our Strategy"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    points4 = [
        ("Precision-Weighted (F0.5): ", "Unlike standard F1-score which treats precision and recall equally, F0.5 weights Precision 2x heavier than Recall."),
        ("Real-World Impact: ", "Falsely merging two different businesses into one entity causes severe compliance and financial errors. Missing a link is far less damaging."),
        ("Singletons: ", "Source 1 entities with NO match earn a full 1.0 score when predicted as an empty list, but score 0 if any false match is predicted."),
        ("Our Decision Threshold: ", "We set our probability cutoff at 0.55 (rather than standard 0.50). This slightly conservative threshold eliminates false merges and maximizes the F0.5 score."),
        ("Recall Ceiling: ", "Stage 1 candidate blocking achieves 99.6% recall ceiling, ensuring genuine matches are rarely missed."),
    ]
    for b_title, b_desc in points4:
        p = tf4.add_paragraph()
        p.space_before = Pt(8)
        r1 = p.add_run()
        r1.text = "• " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11.5)
        r1.font.color.rgb = BLUE
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 5: WHAT WILL BE THE OUTPUT (Results & Output Format)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_header(s5, "What Will Be the Output: Format & Final Results")

    # Left: Output Format & Example
    card_out = add_card(s5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.4))
    tf5_l = card_out.text_frame
    tf5_l.word_wrap = True
    tf5_l.margin_left = tf5_l.margin_right = Inches(0.35)
    tf5_l.margin_top = Inches(0.25)

    p = tf5_l.paragraphs[0]
    p.text = "Output Format & Structure"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    out_points = [
        ("Output File 1 — matching_results.tsv: ", "Contains two columns: source1_entity_id and matched_entity_ids (comma-separated list of matching S2/S3 IDs)."),
        ("Output File 2 — candidate_pairs.tsv: ", "Audit file containing all candidate IDs evaluated per Source 1 entity."),
        ("1-to-1 Entity Alignment: ", "Every Source 1 entity has exactly one row in the output file."),
        ("Sample Match Output: ", "\n  • S1-773889195 -> S2-374107005, S3-189140669\n  (Linked to verified matches in both secondary sources)"),
        ("Sample Singleton Output: ", "\n  • S1-925783039 -> \"\" (Empty string)\n  (No match found; correctly left empty)"),
    ]
    for b_title, b_desc in out_points:
        p = tf5_l.add_paragraph()
        p.space_before = Pt(6)
        r1 = p.add_run()
        r1.text = "✔ " + b_title
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = BLUE
        r2 = p.add_run()
        r2.text = b_desc
        r2.font.size = Pt(11)
        r2.font.color.rgb = TEXT_DARK

    # Right: Recorded Results & Metrics Cards
    card_res = add_card(s5, Inches(6.833), Inches(1.6), Inches(5.7), Inches(5.4))
    tf5_r = card_res.text_frame
    tf5_r.word_wrap = True
    tf5_r.margin_left = tf5_r.margin_right = Inches(0.35)
    tf5_r.margin_top = Inches(0.25)

    p = tf5_r.paragraphs[0]
    p.text = "Model Performance Metrics"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY

    res_metrics = [
        ("Overall Accuracy: 95.95%", "High accuracy across both matches and non-matching candidate pairs."),
        ("Macro F0.5 Score: 0.8810", "Strong precision-weighted score fulfilling the target objective."),
        ("ROC-AUC Score: 0.9915", "Near-perfect ranking capability separating true from false links."),
        ("Precision: 85.63%", "Strict protection against false company mergers."),
        ("Recall: 99.60%", "Captures 3,479 out of 3,493 true matches (only 14 missed)."),
        ("Inference Speed: 113,000 pairs/sec", "High-throughput execution enabled by C++ RapidFuzz."),
    ]
    for m_t, m_d in res_metrics:
        p = tf5_r.add_paragraph()
        p.space_before = Pt(6)
        r1 = p.add_run()
        r1.text = "★ " + m_t + "\n"
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = GREEN
        r2 = p.add_run()
        r2.text = "   " + m_d
        r2.font.size = Pt(10)
        r2.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 6: EVALUATION GRAPHS & 'WHY THIS GRAPH?'
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_header(s6, "Evaluation Graphs & 'Why This Graph?'")

    # Left: Embedded 4-in-1 Master Dashboard Plot
    if IMG_DASHBOARD.exists():
        s6.shapes.add_picture(str(IMG_DASHBOARD), Inches(0.8), Inches(1.6), Inches(7.1), Inches(5.4))

    # Right: 'Why This Graph?' Plain-English Explanation
    card_why = add_card(s6, Inches(8.15), Inches(1.6), Inches(4.383), Inches(5.4))
    tf6 = card_why.text_frame
    tf6.word_wrap = True
    tf6.margin_left = tf6.margin_right = Inches(0.25)
    tf6.margin_top = Inches(0.2)

    p = tf6.paragraphs[0]
    p.text = "Why These 4 Graphs?"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = NAVY

    why_bullets = [
        ("1. Confusion Matrix (Top-Left):",
         "Why: Shows exact prediction counts. Proves 10,673 non-matches were rejected and only 14 true matches missed (99.6% recall)."),
        ("2. ROC Curve (Top-Right):",
         "Why: Evaluates ranking power across all cutoffs. An AUC of 0.9915 confirms the model separates true from false pairs with 99.1% reliability."),
        ("3. Feature Importance (Bottom-Left):",
         "Why: Explains model decisions. Shows that name length difference (33.9%) and sequence similarity (18.9%) are the top predictive features."),
        ("4. Threshold Optimization (Bottom-Right):",
         "Why: Justifies our 0.55 decision cutoff. Demonstrates how 0.55 strictly penalizes false mergers while maximizing Macro F0.5."),
    ]
    for w_t, w_d in why_bullets:
        p = tf6.add_paragraph()
        p.space_before = Pt(6)
        r1 = p.add_run()
        r1.text = w_t + "\n"
        r1.font.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = BLUE
        r2 = p.add_run()
        r2.text = w_d
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = TEXT_DARK

    # Safe Save Handling (handles file locks if user has it open in PowerPoint)
    save_success = False
    target_path = OUTPUT_PPTX
    try:
        prs.save(str(target_path))
        save_success = True
    except PermissionError:
        alt_path = PROJECT_ROOT / "RTPS_Business_Entity_Resolution_Final.pptx"
        try:
            prs.save(str(alt_path))
            target_path = alt_path
            save_success = True
        except Exception as e:
            print(f"[ERROR] Could not save presentation: {e}")

    if save_success:
        print(f"[SUCCESS] Presentation generated: {target_path}")
        print(f"Total Slides: {len(prs.slides)}")


if __name__ == "__main__":
    create_presentation()
