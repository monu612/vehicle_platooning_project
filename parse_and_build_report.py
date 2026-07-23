import re

md_file = "/Users/monu/vehicle_platooning_project/report_source.md"

with open(md_file, "r") as f:
    md_text = f.read()

# Extract sections
sections = re.split(r'\n# SECTION \d+ — [^\n]+', md_text)
titles = re.findall(r'\n# SECTION \d+ — ([^\n]+)', md_text)
titles = ["INTRO"] + titles # section[0] is title/intro

content_by_section = dict(zip(titles, sections))
print("Sections extracted:", titles)
