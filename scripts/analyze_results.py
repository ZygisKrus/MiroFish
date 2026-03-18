import os
import json
from collections import defaultdict

SIM_DIR = "MiroFish/backend/uploads/simulations"

def analyze_simulations():
    print("📊 Fizkonspektas A/B Testing Analysis Report\n")
    
    simulations = []
    
    # 1. Identify Scenarios
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
                    req = config.get("simulation_requirement", "")
                    if "organic word-of-mouth" in req.lower():
                        scenario_name = "Scenario A (Organic Launch)"
                    elif "sticker campaign" in req.lower():
                        scenario_name = "Scenario B (Guerrilla Marketing)"
                except:
                    pass
        
        # Only analyze completed or running simulations that are part of our test
        if scenario_name != "Unknown" and state.get("status") in ["completed", "running", "stopped"]:
            simulations.append({
                "id": sim_id,
                "name": scenario_name,
                "status": state.get("status")
            })

    if not simulations:
        print("No A/B test simulations found. They might still be generating personas.")
        return

    # 2. Analyze Actions
    for sim in sorted(simulations, key=lambda x: x["name"]):
        print(f"==================================================")
        print(f"📈 {sim['name']} (ID: {sim['id']}) - Status: {sim['status']}")
        print(f"==================================================")
        
        total_actions = 0
        platforms = defaultdict(int)
        action_types = defaultdict(int)
        keywords = {"fizkonspektas": 0, "ai": 0, "price": 0, "expensive": 0, "cheat": 0, "help": 0, "exam": 0}
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
                        total_actions += 1
                        
                        # Fix platform counting
                        platforms[platform] += 1
                        
                        action_type = action.get("action_type", "unknown")
                        action_types[action_type] += 1
                        
                        # Sentiment/Keyword proxy
                        result_text = str(action.get("result", "")).lower()
                        if result_text and action_type in ["CREATE_POST", "CREATE_COMMENT"]:
                            for kw in keywords:
                                if kw in result_text:
                                    keywords[kw] += 1
                            
                            # Simple heuristic for sentiment
                            if any(word in result_text for word in ["great", "help", "revolution", "amazing", "good", "love", "game-changer"]):
                                sentiment["positive"] += 1
                            elif any(word in result_text for word in ["bad", "expensive", "cheat", "lazy", "warn", "concern"]):
                                sentiment["negative"] += 1
                            else:
                                sentiment["neutral"] += 1
                                    
                    except:
                        continue
        
        if total_actions == 0:
             print("  No actions recorded yet.\n")
             continue
             
        print(f"Total Interactions: {total_actions}")
        print(f"Platform Split: {dict(platforms)}")
        print(f"Action Types: {dict(action_types)}")
        
        total_sentiment_analyzed = sum(sentiment.values())
        if total_sentiment_analyzed > 0:
            print(f"Sentiment Analysis (based on {total_sentiment_analyzed} posts/comments):")
            print(f"  - Positive: {sentiment['positive']} ({sentiment['positive']/total_sentiment_analyzed*100:.1f}%)")
            print(f"  - Negative: {sentiment['negative']} ({sentiment['negative']/total_sentiment_analyzed*100:.1f}%)")
            print(f"  - Neutral:  {sentiment['neutral']} ({sentiment['neutral']/total_sentiment_analyzed*100:.1f}%)")

        print(f"Keyword Mentions:")
        for kw, count in keywords.items():
            if count > 0:
                print(f"  - '{kw}': {count} mentions")
                
        # Calculate a basic engagement score
        engagement_score = action_types.get("LIKE_POST", 0) + action_types.get("CREATE_COMMENT", 0) * 2 + action_types.get("CREATE_POST", 0) * 3
        print(f"Viral Engagement Score: {engagement_score}")
        print("\n")

if __name__ == "__main__":
    analyze_simulations()
