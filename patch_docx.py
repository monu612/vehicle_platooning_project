import sys

with open("generate_final_docx.py", "r") as f:
    content = f.read()

content = content.replace("global image_index", "")

with open("generate_final_docx.py", "w") as f:
    f.write(content)
