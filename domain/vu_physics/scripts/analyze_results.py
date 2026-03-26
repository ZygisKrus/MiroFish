"""
Fizkonspektas Simulation Analysis Framework

Analyzes results from the two-phase scenario runner:
- Phase 1: Ranks 9 marketing/pricing/emphasis combinations
- Phase 2: Compares design variants for the winning combos
- Generates adoption curves, revenue projections, and recommendations
"""

import os
import json
from collections import defaultdict
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../backend/uploads/simulations"))
RESULTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../results"))

# Keywords to track (English + Lithuanian)
KEYWORDS = {
    "fizkonspektas": ["fizkonspektas"],
    "ai_assistant": ["ai", "dirbtinis intelektas", "asistentas", "chatbot", "tutor", "repetitorius"],
    "price": ["price", "kaina", "9.99", "5.99", "4.99", "eur", "kebab"],
    "expensive": ["expensive", "brangu", "per daug", "highway robbery"],
    "cheat": ["cheat", "apgavyste", "sukciavimas", "etika", "ethics"],
    "help": ["help", "pagalba", "padeda", "naudinga", "useful"],
    "exam": ["exam", "egzaminas", "kolis", "sesija", "midterm", "koliokviumas"],
    "trial": ["trial", "free", "nemokam", "bandymas", "7 day"],
    "sharing": ["share", "split", "dalintis", "susimesti", "group buy", "account"],
    "campus": ["sauletekis", "kamciatka", "kampos", "niujorkas", "bendrabutis", "dorm"],
}

# Sentiment words
POS_WORDS = [
    "great", "help", "amazing", "good", "love", "game-changer", "worth",
    "rekomenduoju", "puiku", "nuostabu", "geras", "padeda", "verta", "cool",
    "naudinga", "patinka", "geriau"
]
NEG_WORDS = [
    "bad", "expensive", "cheat", "lazy", "warn", "concern", "waste", "scam",
    "blogas", "brangu", "apgavyste", "tinginys", "neramina", "neverta",
    "per daug", "atsisakau"
]


def analyze_scenario(sim_id, scenario_meta=None):
    """Analyze a single simulation scenario"""
    result = {
        "simulation_id": sim_id,
        "scenario": scenario_meta or {},
        "total_interactions": 0,
        "platforms": defaultdict(int),
        "action_types": defaultdict(int),
        "keywords": {k: 0 for k in KEYWORDS},
        "sentiment": {"positive": 0, "negative": 0, "neutral": 0},
        "engagement_score": 0,
        # New Fizkonspektas-specific metrics
        "awareness_mentions": 0,         # Times product was mentioned
        "trial_mentions": 0,             # Times trial/free was discussed
        "price_debate_count": 0,         # Price discussions
        "sharing_discussion_count": 0,   # Account sharing discussions
        "exam_urgency_count": 0,         # Exam-related urgency
        "ai_interest_count": 0,          # AI assistant discussions
        "adoption_signals": 0,           # Positive adoption indicators
        "resistance_signals": 0,         # Resistance/rejection indicators
    }

    sim_path = os.path.join(SIM_DIR, sim_id)
    if not os.path.exists(sim_path):
        return result

    # Check all platform subdirectories
    for platform in ["instagram", "telegram", "facebook", "physical", "website", "twitter", "reddit"]:
        actions_path = os.path.join(sim_path, platform, "actions.jsonl")
        if not os.path.exists(actions_path):
            continue

        with open(actions_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    action = json.loads(line)
                    if action.get("event_type"):
                        continue

                    result["total_interactions"] += 1
                    result["platforms"][platform] += 1

                    action_type = action.get("action_type", "unknown")
                    result["action_types"][action_type] += 1

                    # Extract content
                    content = ""
                    args = action.get("action_args", {})
                    if action_type == "CREATE_POST":
                        content = args.get("content", "")
                    elif action_type == "CREATE_COMMENT":
                        content = args.get("comment_text", "")
                    elif action_type == "QUOTE_POST":
                        content = args.get("quote_content", "")

                    if content:
                        content_lower = content.lower()

                        # Keyword matching
                        for category, words in KEYWORDS.items():
                            if any(w in content_lower for w in words):
                                result["keywords"][category] += 1

                        # Sentiment
                        is_pos = any(w in content_lower for w in POS_WORDS)
                        is_neg = any(w in content_lower for w in NEG_WORDS)
                        if is_pos and not is_neg:
                            result["sentiment"]["positive"] += 1
                        elif is_neg and not is_pos:
                            result["sentiment"]["negative"] += 1
                        else:
                            result["sentiment"]["neutral"] += 1

                        # Fizkonspektas-specific signal detection
                        if "fizkonspektas" in content_lower:
                            result["awareness_mentions"] += 1
                        if any(w in content_lower for w in ["trial", "free", "nemokam", "bandymas"]):
                            result["trial_mentions"] += 1
                        if any(w in content_lower for w in ["price", "kaina", "brangu", "9.99", "kebab"]):
                            result["price_debate_count"] += 1
                        if any(w in content_lower for w in ["share", "split", "dalintis", "susimesti"]):
                            result["sharing_discussion_count"] += 1
                        if any(w in content_lower for w in ["exam", "egzaminas", "kolis", "sesija"]):
                            result["exam_urgency_count"] += 1
                        if any(w in content_lower for w in ["ai", "asistentas", "tutor", "repetitorius"]):
                            result["ai_interest_count"] += 1

                        # Adoption vs resistance signals
                        adoption_words = ["bought", "subscribed", "pirko", "uzsisakiau", "worth it", "verta", "recommend"]
                        resistance_words = ["cancelled", "refuse", "atsisakau", "neverta", "waste", "scam"]
                        if any(w in content_lower for w in adoption_words):
                            result["adoption_signals"] += 1
                        if any(w in content_lower for w in resistance_words):
                            result["resistance_signals"] += 1

                except Exception:
                    continue

    # Calculate engagement score
    at = result["action_types"]
    result["engagement_score"] = (
        at.get("LIKE_POST", 0) +
        at.get("CREATE_COMMENT", 0) * 2 +
        at.get("CREATE_POST", 0) * 3 +
        at.get("QUOTE_POST", 0) * 2
    )

    return result


def compute_composite_score(result):
    """Compute a composite score for ranking scenarios"""
    if result["total_interactions"] == 0:
        return 0

    total_sent = sum(result["sentiment"].values()) or 1
    sentiment_ratio = result["sentiment"]["positive"] / total_sent

    # Weighted composite score
    score = (
        result["awareness_mentions"] * 3 +
        result["adoption_signals"] * 10 +
        result["trial_mentions"] * 5 +
        result["ai_interest_count"] * 2 +
        sentiment_ratio * 50 +
        result["engagement_score"] * 0.5 -
        result["resistance_signals"] * 5 -
        result["sharing_discussion_count"] * 2  # Sharing hurts revenue
    )
    return round(score, 1)


def print_scenario_report(result, rank=None):
    """Print detailed report for a single scenario"""
    meta = result.get("scenario", {})
    scenario_id = meta.get("id", "?")
    scenario_name = meta.get("name", "Unknown")

    rank_str = f"#{rank} " if rank else ""
    print(f"\n{'='*60}")
    print(f"{rank_str}{scenario_id}: {scenario_name}")
    if meta:
        print(f"Marketing: {meta.get('marketing', '?')} | Pricing: {meta.get('pricing', '?')} | Emphasis: {meta.get('emphasis', '?')} | Design: {meta.get('design', '?')}")
    print(f"{'='*60}")

    if result["total_interactions"] == 0:
        print("  No interactions recorded yet.")
        return

    print(f"Total Interactions: {result['total_interactions']}")
    print(f"Platform Split: {dict(result['platforms'])}")

    total_sent = sum(result["sentiment"].values()) or 1
    print(f"\nSentiment ({total_sent} analyzed):")
    for s in ["positive", "negative", "neutral"]:
        pct = result["sentiment"][s] / total_sent * 100
        bar = "#" * int(pct / 5)
        print(f"  {s:>8}: {result['sentiment'][s]:>4} ({pct:5.1f}%) {bar}")

    print(f"\nFizkonspektas Signals:")
    print(f"  Product awareness mentions: {result['awareness_mentions']}")
    print(f"  Trial/free discussions:     {result['trial_mentions']}")
    print(f"  Price debates:              {result['price_debate_count']}")
    print(f"  Account sharing talks:      {result['sharing_discussion_count']}")
    print(f"  Exam urgency mentions:      {result['exam_urgency_count']}")
    print(f"  AI assistant interest:      {result['ai_interest_count']}")
    print(f"  Adoption signals:           {result['adoption_signals']}")
    print(f"  Resistance signals:         {result['resistance_signals']}")

    score = compute_composite_score(result)
    print(f"\nComposite Score: {score}")
    print(f"Engagement Score: {result['engagement_score']}")


def analyze_phase(phase_name, results_file):
    """Analyze all scenarios in a phase"""
    results_path = os.path.join(RESULTS_DIR, results_file)
    if not os.path.exists(results_path):
        print(f"No results file found: {results_path}")
        return []

    with open(results_path) as f:
        sim_ids = json.load(f)

    print(f"\n{'#'*70}")
    print(f"# {phase_name} Analysis")
    print(f"{'#'*70}")

    all_results = []
    for scenario_id, sim_id in sim_ids.items():
        # Try to load scenario metadata
        meta_path = os.path.join(RESULTS_DIR, f"{scenario_id}_meta.json")
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                meta_data = json.load(f)
                meta = meta_data.get("scenario", {})

        result = analyze_scenario(sim_id, meta)
        result["composite_score"] = compute_composite_score(result)
        all_results.append(result)

    # Sort by composite score
    all_results.sort(key=lambda r: r["composite_score"], reverse=True)

    # Print ranked reports
    for rank, result in enumerate(all_results, 1):
        print_scenario_report(result, rank)

    # Print ranking summary
    print(f"\n{'='*60}")
    print(f"RANKING SUMMARY - {phase_name}")
    print(f"{'='*60}")
    for rank, result in enumerate(all_results, 1):
        meta = result.get("scenario", {})
        sid = meta.get("id", "?")
        name = meta.get("name", "Unknown")
        score = result["composite_score"]
        print(f"  #{rank}: {sid} ({name}) - Score: {score}")

    if all_results:
        winner = all_results[0]
        winner_meta = winner.get("scenario", {})
        print(f"\nWINNER: {winner_meta.get('id', '?')} - {winner_meta.get('name', '?')}")
        print(f"  Marketing: {winner_meta.get('marketing', '?')}")
        print(f"  Pricing: {winner_meta.get('pricing', '?')}")
        print(f"  Emphasis: {winner_meta.get('emphasis', '?')}")
        print(f"  Design: {winner_meta.get('design', '?')}")

    return all_results


def generate_recommendation(phase_1_results, phase_2_results=None):
    """Generate final launch recommendation"""
    print(f"\n{'#'*70}")
    print(f"# FINAL LAUNCH RECOMMENDATION")
    print(f"{'#'*70}")

    if not phase_1_results:
        print("No Phase 1 results available.")
        return

    best_p1 = phase_1_results[0] if phase_1_results else None
    best_p2 = phase_2_results[0] if phase_2_results else None

    best = best_p2 or best_p1
    meta = best.get("scenario", {})

    print(f"\nRecommended Launch Configuration:")
    print(f"  Marketing:  {meta.get('marketing', '?')} - Use this channel strategy")
    print(f"  Pricing:    {meta.get('pricing', '?')} - Use this pricing model")
    print(f"  Emphasis:   {meta.get('emphasis', '?')} - Lead with this message")
    print(f"  Design:     {meta.get('design', '?')} - Use this UI design")

    print(f"\nKey Insights:")
    if best.get("sharing_discussion_count", 0) > best.get("adoption_signals", 0):
        print(f"  WARNING: Account sharing discussions ({best['sharing_discussion_count']}) exceed adoption signals ({best['adoption_signals']})")
        print(f"  -> Consider stronger anti-sharing measures or embrace it with team pricing")

    if best.get("exam_urgency_count", 0) > best.get("awareness_mentions", 0):
        print(f"  INSIGHT: Exam urgency ({best['exam_urgency_count']}) drives more discussion than brand awareness ({best['awareness_mentions']})")
        print(f"  -> Time your launch push around exam periods")

    if best.get("ai_interest_count", 0) > best.get("trial_mentions", 0):
        print(f"  INSIGHT: AI assistant interest ({best['ai_interest_count']}) is high")
        print(f"  -> The AI tutor angle resonates strongly")

    print(f"\nGenerated at: {datetime.now().isoformat()}")


def main():
    print("Fizkonspektas Simulation Analysis Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Analyze Phase 1
    phase_1_results = analyze_phase("PHASE 1: Marketing x Pricing x Emphasis", "phase_1_results.json")

    # Analyze Phase 2 (if available)
    phase_2_results = analyze_phase("PHASE 2: Design Variants", "phase_2_results.json")

    # Generate recommendation
    generate_recommendation(phase_1_results, phase_2_results)

    # Save full analysis
    os.makedirs(RESULTS_DIR, exist_ok=True)
    report = {
        "generated_at": datetime.now().isoformat(),
        "phase_1_ranking": [
            {
                "rank": i + 1,
                "scenario": r.get("scenario", {}),
                "composite_score": r.get("composite_score", 0),
                "total_interactions": r.get("total_interactions", 0),
                "sentiment": dict(r.get("sentiment", {})),
                "adoption_signals": r.get("adoption_signals", 0),
                "resistance_signals": r.get("resistance_signals", 0),
            }
            for i, r in enumerate(phase_1_results)
        ],
        "phase_2_ranking": [
            {
                "rank": i + 1,
                "scenario": r.get("scenario", {}),
                "composite_score": r.get("composite_score", 0),
            }
            for i, r in enumerate(phase_2_results)
        ] if phase_2_results else [],
    }

    report_path = os.path.join(RESULTS_DIR, "analysis_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nFull analysis saved to: {report_path}")


if __name__ == "__main__":
    main()
