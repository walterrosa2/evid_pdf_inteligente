
import os

file_path = r"backend/static/uploads/3_full.txt"
marker = "fls."

if not os.path.exists(file_path):
    print("File not found")
    exit()

with open(file_path, "r", encoding="utf-8") as f:
    full_text = f.read()

print(f"Total Text Length: {len(full_text)}")
print(f"Marker found count: {full_text.count(marker)}")

pages = full_text.split(marker)
print(f"Raw split count: {len(pages)}")

# The logic in text_service
pages = [p for p in pages if p.strip()]
print(f"Filtered pages count: {len(pages)}")

target_page = 59
if 1 <= target_page <= len(pages):
    print(f"Page {target_page} found.")
    content = pages[target_page - 1].strip()
    print(f"Content length: {len(content)}")
    print(f"Content preview: {content[:100]}")
else:
    print(f"Page {target_page} NOT found. Max page: {len(pages)}")
