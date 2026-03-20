import re

with open("domain/vu_physics/seeds/refined_mega_seed.md", "r", encoding="utf-8") as f:
    content = f.read()

# --- 1. UX/UI & Format Preferences ---

# Rokas Giedraitis (ESTP) - Wants short cheatsheets
content = content.replace(
    "wants the app to just 'give the formula' so he can go back to the lab.",
    "hates the 'Medium-Detailed' format; explicitly demands a 'Rapid Cheatsheet' mode with just formulas and no long text to read before a kolis."
)

# Eglė Šventickienė (INFJ) - Wants deep-dive
content = content.replace(
    "worried that KaTeX step-by-step solutions will rot the brains of first-years.",
    "prefers the 'Deep-Dive Archive' format; thinks short cheatsheets are useless for truly understanding Prof. Vičas's complex proofs."
)

# Gabija Petraitytė (ISFP) - UI/Dark mode focused
content = content.replace(
    "Artist; loves the app's UI design but finds the content too 'dry'.",
    "Artist; obsessed with the 'Industrial Archive' Dark Mode and JetBrains Mono font. Refuses to use Moodle because it's 'ugly'."
)


# --- 2. FOMO & Status ---

# Tomas Dimša (ENFJ) - Status
content = content.replace(
    "Influencer wannabe; trying to get a 'brand deal' from Fizkonspektas to promote it to VU students.",
    "Influencer wannabe; bought the premium plan immediately just to flex on his study group that he doesn't need to 'hack' the system."
)

# Arnas Butkevičius (ISFJ) - FOMO
content = content.replace(
    "Nervous wreck; thinks the subscription fee is a 'protection fee' to keep prof. Vičas from failing him.",
    "Nervous wreck; sees his roommates chilling before the exam using the app, gets extreme FOMO, and panic-subscribes 3 hours before the kolis."
)


# --- 3. Locations (MKIC, NFT) ---

# Liepa Martinaitytė (INTP) - MKIC
content = content.replace(
    "Theoretical physicist who 'lives' in the Saulėtekis library; uses the app to find loopholes in exam questions.",
    "Theoretical physicist who 'lives' in MKIC; saw someone at the next table using Fizkonspektas on their iPad and secretly Googled it."
)

# Gintarė Petronytė (ISTJ) - NFT
content = content.replace(
    "Lab manager; bans phones in her lab to prevent 'Fizkonspektas' usage during experiments.",
    "Lab manager at NFT (Nacionalinis Fizinių ir Technologijos Mokslų Centras); actively hunts for students using Fizkonspektas under the desks during her practicals."
)


# --- 4. The "Subscription Trap" / Cancellation Friction ---

# Eimantas Bendžius (ESTJ) - The Calendar Guy who fails
content = content.replace(
    "Disciplined; sets a timer for app usage to ensure he doesn't 'become a slave to the AI'.",
    "Disciplined; set 3 Google Calendar reminders to cancel the free trial, but got completely overwhelmed by an 'ataskaita' deadline and got charged anyway."
)

# Simona Lukauskaitė (ESFJ) - The Apathetic trap victim
content = content.replace(
    "Movie night; trying to find a physics documentary on the app.",
    "Saw the -€9.99 charge on her Revolut after the trial ended, but thought 'ai, tingiu atšaukti, vis tiek reikės prieš finalinį', becoming the perfect trap victim."
)


# --- 5. Add MKIC and NFT to the Environment Description ---
env_addition = """
The **MKIC (Mokslinės komunikacijos ir informacijos centras)** is the 24/7 battleground. It's where students silently judge each other's study methods. Seeing someone smoothly scrolling through Fizkonspektas's dark mode on an iPad here creates immense FOMO. Meanwhile, the **NFT (Nacionalinis Fizinių ir Technologijos Mokslų Centras)** labs are where the real stress happens, and where the app's quick-reference capabilities are most desperately needed under the table.
"""

content = content.replace(
    "If you haven't cried in the 'Didžioji Fizikos Auditorija', you aren't a real VU physicist yet.",
    "If you haven't cried in the 'Didžioji Fizikos Auditorija', you aren't a real VU physicist yet.\n\n" + env_addition
)

with open("domain/vu_physics/seeds/refined_mega_seed.md", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Added UX preferences, MKIC/NFT locations, FOMO, and Subscription Trap behaviors to the seed.")
