import re
import random

# Read existing seed
with open("domain/vu_physics/seeds/refined_mega_seed.md", "r", encoding="utf-8") as f:
    content = f.read()

# Extract existing agent block
match = re.search(r"(# 1\. The Unified Student Roster \(150 Unique Agents\)\n\n)(.*?)\n\n(# 2\. Social Graph)", content, re.DOTALL)
if not match:
    print("Could not find agent roster block.")
    exit(1)

prefix = match.group(1)
existing_agents = match.group(2)
suffix = "\n\n" + match.group(3) + content[match.end(3):]

# Existing names to avoid duplicates
existing_names = set()
for line in existing_agents.strip().split('\n'):
    name_match = re.search(r"- \*\*([^*]+)\*\*", line)
    if name_match:
        existing_names.add(name_match.group(1))

# Lists for generation
first_names_m = ["Kastytis", "Julius", "Aidas", "Deividas", "Benas", "Mykolas", "Kipras", "Jurgis", "Vilius", "Simonas", "Rytis", "Tautvydas", "Gvidas", "Orestas", "Pijus", "Kęstutis", "Giedrius", "Žygimantas", "Evaldas", "Gintaras", "Rimantas", "Valdas", "Dainius", "Artūras", "Saulius", "Tomas", "Andrius", "Darius", "Marius", "Donatas"]
first_names_f = ["Milda", "Ugnė", "Kotryna", "Aistė", "Goda", "Kamilė", "Liepa", "Viltė", "Emilija", "Gabija", "Ieva", "Rasa", "Lina", "Eglė", "Giedrė", "Jolanta", "Daiva", "Vilma", "Neringa", "Jurgita", "Rūta", "Inga", "Aušra", "Agnė", "Gintarė", "Jurga", "Diana", "Edita", "Laura", "Monika"]
last_names = ["Kavaliauskas", "Žukauskas", "Navickas", "Kazlauskas", "Stankevičius", "Petrauskas", "Jankauskas", "Urbonas", "Vasiliauskas", "Pocius", "Paulauskas", "Adomaitis", "Butkus", "Ramanauskas", "Kairys", "Mickevičius", "Šimkus", "Žilinskas", "Rimkus", "Savickas"]
majors = ["Physics", "Economics", "Law", "Communications", "Mathematics", "Computer Science"]
years = ["1st", "2nd", "3rd", "4th", "Master's"]
mbtis = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]

hooks = [
    "Constantly studying at MKIC until 3 AM; needs the 'Rapid Cheatsheet' because long texts put them to sleep.",
    "Paranoid about Google OAuth. Refuses to use their personal Gmail for the trial and spends an hour creating a dummy account.",
    "Loves the 'Industrial Archive' Dark Mode UI. Says it feels like a hacker tool from the 90s, which justifies the subscription fee.",
    "Got caught trying to look at Fizkonspektas under the desk during an NFT lab practical.",
    "Organized a 'study cartel' with 4 others. They share one dummy Gmail account, but now they are fighting over who pays the monthly fee.",
    "Used personal Gmail for the free trial. Intended to cancel, but a sudden 'koliokviumas' panic made them keep it.",
    "Thinks the KaTeX rendering is beautiful, but complains on Discord that the UI lacks a 'Light Mode' for studying outdoors at Saulėtekis.",
    "Saw someone getting straight 10s using Fizkonspektas at MKIC. The FOMO hit hard, and they bought the premium plan instantly.",
    "Always buys kebabs at Jammi, so they calculated the subscription fee in 'kebab currency' and decided it was a fair trade-off for passing.",
    "Set 5 alarms to cancel the trial, but ignored all of them because they were too busy debugging a Python script for physics lab.",
    "Thinks the step-by-step math explanations are exactly what Prof. Vičas fails to provide during lectures.",
    "Tries to sell printed PDFs of Fizkonspektas notes to freshmen outside the 'Didžioji Fizikos Auditorija'.",
    "Uses the app exclusively on their phone while riding the bus from Antakalnis to Saulėtekis.",
    "Complains that sharing passwords is a security risk, so they just pay the full individual price to avoid the hassle.",
    "Believes the platform is a lifesaver, but wishes it had a social feature to see who else from Kamčiatka is currently online studying.",
    "Only signed up for the trial to see what the hype was about, completely forgot to cancel, and now feels forced to use it.",
    "Prefers the 'Deep-Dive Archive' format. Thinks cheat sheets are for weak students who will fail the finals anyway.",
    "Thinks the subscription is a trap, but admits the UI is smoother than the official VU systems.",
    "Shared their personal Gmail with a friend to split the cost, and now their Google search history is ruined by physics queries.",
    "Lives in Niujorkas dorm. Uses the platform to quickly verify homework answers before submitting."
]

new_agents = []
generated_names = set()

while len(new_agents) < 150:
    is_male = random.choice([True, False])
    first_name = random.choice(first_names_m) if is_male else random.choice(first_names_f)
    
    # Adjust last name ending for females in Lithuanian
    raw_last_name = random.choice(last_names)
    if not is_male:
        if raw_last_name.endswith("as"):
            last_name = raw_last_name[:-2] + "aitė"
        elif raw_last_name.endswith("ius"):
            last_name = raw_last_name[:-3] + "iūtė"
        else:
            last_name = raw_last_name + "aitė"
    else:
        last_name = raw_last_name
        
    full_name = f"{first_name} {last_name}"
    
    if full_name in existing_names or full_name in generated_names:
        continue
        
    generated_names.add(full_name)
    
    major = random.choice(majors)
    year = random.choice(years)
    mbti = random.choice(mbtis)
    hook = random.choice(hooks)
    
    # Add some randomness to the hook to make it more unique
    hook_variations = [
        f"{hook} Usually seen near the faculty coffee machine.",
        f"{hook} Stresses over every single 'ataskaita'.",
        f"{hook} Thinks FiDi is the only good thing about studying here.",
        f"{hook} Barely survived the last semester.",
        f"{hook} Considers themselves the smartest person in the dorm."
    ]
    final_hook = random.choice(hook_variations)
    
    agent_line = f"- **{full_name}** ({major}, {year}, {mbti}): {final_hook}"
    new_agents.append(agent_line)

# Combine and update
new_roster_block = existing_agents.strip() + "\n" + "\n".join(new_agents)
new_prefix = prefix.replace("150 Unique Agents", "300 Unique Agents")

final_content = new_prefix + new_roster_block + suffix

with open("domain/vu_physics/seeds/refined_mega_seed.md", "w", encoding="utf-8") as f:
    f.write(final_content)

print(f"✅ Successfully added {len(new_agents)} new agents. Total is now 300.")
