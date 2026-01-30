
import os

file_path = r"backend/static/uploads/4_full.txt"

if not os.path.exists(file_path):
    print("File not found")
    exit()

with open(file_path, "r", encoding="utf-8") as f:
    full_text = f.read()

print(f"File: {file_path}")
print(f"Total Length: {len(full_text)}")
print(f"Count 'fls.': {full_text.count('fls.')}")
print(f"Count '[[PAGINA]]': {full_text.count('[[PAGINA]]')}")
