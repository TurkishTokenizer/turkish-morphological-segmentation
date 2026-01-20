import json
import re
import os
from tqdm import tqdm

# Configuration
INPUT_FILE = "tr-extract.jsonl"
OUTPUT_DIR = "extracted_pos"
ERROR_LOG_FILE = "errors.log"

# Regex for valid Turkish words
VALID_WORD_PATTERN = re.compile(r"^[a-zA-ZçÇğĞıİöÖşŞüÜÂâÎîÛû\s\-\'\’]+$")

def standardize_pos(pos_tag):
    """Standardizes POS tags to capitalized broad categories."""
    if not pos_tag:
        return "OTHER"
    
    pos_lower = pos_tag.lower()
    
    mapping = {
        "noun": "NOUN",
        "verb": "VERB",
        "adj": "ADJ",
        "adjective": "ADJ",
        "adv": "ADV",
        "adverb": "ADV",
        "conj": "CONJ",
        "conjunction": "CONJ",
        "pron": "PRON",
        "pronoun": "PRON",
        "num": "NUM",
        "number": "NUM",
    }
    
    # Return mapped value or OTHER if not found
    return mapping.get(pos_lower, "OTHER")

def is_valid_turkish_word(word):
    """Checks if the word contains only valid Turkish characters."""
    if not word:
        return False
    return bool(VALID_WORD_PATTERN.match(word))

def process_file():
    """Main processing loop."""
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Count lines for tqdm
    print("Counting total lines for progress bar...")
    total_lines = 0
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for _ in f:
            total_lines += 1
    
    # Open file handles for writing
    file_handles = {}

    def get_file_handle(category):
        if category not in file_handles:
            file_handles[category] = open(os.path.join(OUTPUT_DIR, f"{category}.jsonl"), "w", encoding="utf-8")
        return file_handles[category]

    errors_handle = open(ERROR_LOG_FILE, "w", encoding="utf-8")
    
    print("Starting processing...")
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(tqdm(f, total=total_lines, unit="lines")):
            try:
                data = json.loads(line)
                
                # 1. Filter by lang_code
                if data.get("lang_code") != "tr":
                    continue
                
                raw_word = data.get("word", "")
                word = raw_word.strip()
                
                # 2. Data Cleaning: Valid Turkish Chars Only
                if not is_valid_turkish_word(word):
                    continue
                
                # 3. Extract & Standardize
                pos = standardize_pos(data.get("pos"))
                
                # 4. Create Clean Output Object (Minimal)
                output_obj = {
                    "word": word,
                    "pos": pos
                }
                
                # 5. Write to file
                handle = get_file_handle(pos)
                handle.write(json.dumps(output_obj, ensure_ascii=False) + "\n")
                    
            except json.JSONDecodeError as e:
                errors_handle.write(f"Line {line_num}: JSON Error - {str(e)}\n")
            except Exception as e:
                errors_handle.write(f"Line {line_num}: General Error - {str(e)}\n")

    # Cleanup
    for fh in file_handles.values():
        fh.close()
    errors_handle.close()
    
    print(f"\nProcessing complete. Files filtered and saved to '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    process_file()
