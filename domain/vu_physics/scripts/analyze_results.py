import os
import json
from collections import defaultdict

# Calculate SIM_DIR relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../../backend/uploads/simulations"))

def analyze_simulations():
    print("📊 Fizkonspektas A/B Testing Analysis Report\n")
    
    simulations = []
    
    # 1. Identify Scenarios
    if not os.path.exists(SIM_DIR):
        print(f"Directory {SIM_DIR} not found.")
        return

    for sim_id in os.listdir(SIM_DIR):
        state_path = os.path.join(SIM_DIR, sim_id, "state.json")
        if not os.path.exists(state_path):
            continue
            
        with open(state_path, "r", encoding="utf-8") as f:
            try:
                state = json.load(f)
            except:
                continue
                
        # To get the scenario name
        config_path = os.path.join(SIM_DIR, sim_id, "simulation_config.json")
        scenario_name = "Unknown"
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                try:
                    config = json.load(f)
                    req = config.get("simulation_requirement", "").lower()
                    if "scenario a" in req:
                        scenario_name = "Scenario A (The Crammer's Exploit)"
                    elif "scenario b" in req:
                        scenario_name = "Scenario B (The Phantom Loophole)"
                    elif "scenario c" in req:
                        scenario_name = "Scenario C (The Premium Cartel)"
                except:
                    pass
        
        # Only analyze completed or running simulations
        if state.get("status") in ["completed", "running", "stopped", "ready", "paused"]:
            simulations.append({
                "id": sim_id,
                "name": scenario_name,
                "status": state.get("status")
            })

    if not simulations:
        print("No simulations found in the target directory.")
        return

    # 2. Analyze Actions
    for sim in sorted(simulations, key=lambda x: x["name"]):
        print(f"==================================================")
        print(f"📈 {sim['name']} (ID: {sim['id']}) - Status: {sim['status']}")
        print(f"==================================================")
        
        total_interactions = 0
        platforms = defaultdict(int)
        action_types = defaultdict(int)
        
        # Keywords (English + Lithuanian)
        keywords = {
            "fizkonspektas": 0, 
            "ai": 0, 
            "price/kaina": 0, 
            "expensive/brangu": 0, 
            "cheat/apgavyste": 0, 
            "help/pagalba": 0, 
            "exam/egzaminas": 0,
            "late x/latex": 0,
            "saulėtekis": 0,
            "kamčiatka": 0
        }
        
        sentiment = {"positive": 0, "negative": 0, "neutral": 0}
        
        # Check both platform subdirectories
        for platform in ["twitter", "reddit"]:
            actions_path = os.path.join(SIM_DIR, sim['id'], platform, "actions.jsonl")
            if not os.path.exists(actions_path):
                continue
                
            with open(actions_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        action = json.loads(line)
                        if action.get("event_type"):
                            continue
                            
                        total_interactions += 1
                        platforms[platform] += 1
                        
                        action_type = action.get("action_type", "unknown")
                        action_types[action_type] += 1
                        
                        # Extract content from various action types
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
                            if "fizkonspektas" in content_lower: keywords["fizkonspektas"] += 1
                            if "ai" in content_lower or "dirbtinis intelektas" in content_lower: keywords["ai"] += 1
                            if "price" in content_lower or "kaina" in content_lower: keywords["price/kaina"] += 1
                            if "expensive" in content_lower or "brangu" in content_lower: keywords["expensive/brangu"] += 1
                            if "cheat" in content_lower or "apgavyste" in content_lower or "sukciavimas" in content_lower: keywords["cheat/apgavyste"] += 1
                            if "help" in content_lower or "pagalba" in content_lower or "padeda" in content_lower: keywords["help/pagalba"] += 1
                            if "exam" in content_lower or "egzaminas" in content_lower or "kolis" in content_lower: keywords["exam/egzaminas"] += 1
                            if "latex" in content_lower: keywords["late x/latex"] += 1
                            if "saulėtekis" in content_lower: keywords["saulėtekis"] += 1
                            if "kamčiatka" in content_lower or "kampos" in content_lower: keywords["kamčiatka"] += 1
                            
                            # Sentiment heuristic (English + Lithuanian)
                            pos_words = ["great", "help", "amazing", "good", "love", "game-changer", "rekomenduoju", "puiku", "nuostabu", "geras", "padeda"]
                            neg_words = ["bad", "expensive", "cheat", "lazy", "warn", "concern", "blogas", "brangu", "apgavyste", "tinginystė", "neramina"]
                            
                            if any(word in content_lower for word in pos_words):
                                sentiment["positive"] += 1
                            elif any(word in content_lower for word in neg_words):
                                sentiment["negative"] += 1
                            else:
                                sentiment["neutral"] += 1
                                    
                    except Exception as e:
                        continue
        
        if total_interactions == 0:
             print("  No actions recorded yet.\n")
             continue
             
        print(f"Total Interactions: {total_interactions}")
        print(f"Platform Split: {dict(platforms)}")
        print(f"Action Types: {dict(action_types)}")
        
        total_sentiment_analyzed = sum(sentiment.values())
        if total_sentiment_analyzed > 0:
            print(f"Sentiment Analysis (based on {total_sentiment_analyzed} posts/comments):")
            print(f"  - Positive: {sentiment['positive']} ({sentiment['positive']/total_sentiment_analyzed*100:.1f}%)")
            print(f"  - Negative: {sentiment['negative']} ({sentiment['negative']/total_sentiment_analyzed*100:.1f}%)")
            print(f"  - Neutral:  {sentiment['neutral']} ({sentiment['neutral']/total_sentiment_analyzed*100:.1f}%)")

        print(f"Keyword Mentions:")
        found_any = False
        for kw, count in keywords.items():
            if count > 0:
                print(f"  - '{kw}': {count} mentions")
                found_any = True
        if not found_any:
            print("  - None detected.")
                
        # Calculate a basic engagement score
        engagement_score = action_types.get("LIKE_POST", 0) + action_types.get("CREATE_COMMENT", 0) * 2 + action_types.get("CREATE_POST", 0) * 3 + action_types.get("QUOTE_POST", 0) * 2
        print(f"Viral Engagement Score: {engagement_score}")
        print("\n")

if __name__ == "__main__":
    analyze_simulations()
