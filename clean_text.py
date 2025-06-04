import json
import re

# Load your JSON file
with open("tds_lectures_with_content.json", "r", encoding="utf-8") as f:
    data = json.load(f)

clean_texts = []

def clean_markdown(md_content):
    # Remove YAML front matter
    md_content = re.sub(r"^---.*?---\n+", "", md_content, flags=re.DOTALL)
    # Remove markdown image links
    md_content = re.sub(r"!\[.*?\]\(.*?\)", "", md_content)
    # Remove markdown links but keep text: [text](link) → text
    md_content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md_content)
    # Remove markdown headers
    md_content = re.sub(r"^#+\s*", "", md_content, flags=re.MULTILINE)
    # Remove any leftover markdown formatting (like **bold**)
    md_content = re.sub(r"[*_`#~]", "", md_content)
    # Collapse multiple newlines
    md_content = re.sub(r"\n{2,}", "\n\n", md_content)
    return md_content.strip()

for item in data:
    content = item.get("content", "")
    if content:
        clean = clean_markdown(content)
        clean_texts.append({
            "title": item["title"],
            "filename": item["filename"],
            "text": clean
        })

# Save cleaned output for embedding
with open("tds_cleaned_texts.json", "w", encoding="utf-8") as f:
    json.dump(clean_texts, f, indent=2, ensure_ascii=False)

print("✅ Cleaned texts saved to tds_cleaned_texts.json")
