import json
import os

# Path to your existing JSON file
INPUT_JSON = 'metadata_web.json'
# Output enhanced JSON file
OUTPUT_JSON = 'tds_lectures_with_content.json'
# Folder where all .md files are saved
MD_FOLDER = './tds_webpages_md'  # change this if your md files are in another folder

def load_markdown_content(filename):
    filepath = os.path.join(MD_FOLDER, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return None

def enhance_lecture_data():
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        lectures = json.load(f)

    for lecture in lectures:
        content = load_markdown_content(lecture["filename"])
        if content:
            lecture["content"] = content
        else:
            lecture["content"] = "[Missing file: {}]".format(lecture["filename"])

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(lectures, f, ensure_ascii=False, indent=2)

    print(f"✅ Done! Output saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    enhance_lecture_data()
