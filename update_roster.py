import re

with open("domain/vu_physics/seeds/refined_mega_seed.md", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove hardcoded €9.99
content = re.sub(r"€9\.99/?m?o?", "the subscription fee", content)
content = re.sub(r"9\.99€", "the subscription fee", content)

# 2. Inject Gmail/OAuth friction to specific agent types
# Mantas Kalnietis - the group buyer
content = content.replace(
    "trying to find 4 people to split a 'Fizkonspektas' account to save money for Jammi kebabs.",
    "trying to find 4 people to split an account, but nobody wants to share their personal Gmail password to bypass the OAuth."
)

# Giedrė Labuckaitė
content = content.replace(
    "desperate for the AI tutor but hides it from her strict study group.",
    "desperate for the AI tutor; used her real Gmail for the free trial and is terrified she'll forget to cancel."
)

# Vaida Žitkutė
content = content.replace(
    "wants to organize a 'Fizkonspektas' party where everyone shares one login.",
    "wants to make a shared 'dummy' Gmail so the whole dorm can use one free trial, but finds the Google phone verification annoying."
)

# Marius Grigonis
content = content.replace(
    "thinks the app is a 'VC-funded trap' to collect student data.",
    "thinks the Google OAuth login is a trap to steal personal data and refuses to share his account."
)

# Lukas Lekavičius
content = content.replace(
    "can navigate the KaTeX derivations faster than anyone, but always forgets to pay the subscription fee.",
    "loves the minimal UI, but has ADHD and literally always forgets to cancel free trials before the card gets charged."
)

with open("domain/vu_physics/seeds/refined_mega_seed.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated seed file.")
