import pandas as pd
import os
import glob
import re

# --- Configuration ---
DATA_DIR = "data"
QNA_FILE_PATTERN = os.path.join(DATA_DIR, "*-qna.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "answers_comparison.csv")
ANSWER_COLUMN = "Answer"
EXPECTED_ROW_COUNT = 33 # Optional: Set the expected number of rows based on topics.csv

# --- Main Script ---
def get_model_name_from_filename(filename):
    """Extracts the model/service name from the filename."""
    base = os.path.basename(filename)
    name_part = base.replace("-qna.csv", "")
    return name_part

# Find all Q&A files
qna_files = sorted(glob.glob(QNA_FILE_PATTERN)) # Sort for consistent column order

if not qna_files:
    print(f"Warning: No Q&A files found matching pattern '{QNA_FILE_PATTERN}'. Cannot create comparison file.")
    exit(0)

print(f"Found {len(qna_files)} Q&A files to extract answers from:")
for f in qna_files:
    print(f"  - {os.path.basename(f)}")

all_answers = [] # List to hold each model's answer Series

# Iterate through each Q&A file, extract and rename the Answer column
for qna_file in qna_files:
    model_name = get_model_name_from_filename(qna_file)
    print(f"Processing {model_name} answers from {os.path.basename(qna_file)}...")

    try:
        temp_df = pd.read_csv(qna_file, keep_default_na=False, encoding='utf-8')

        if ANSWER_COLUMN not in temp_df.columns:
            print(f"  Warning: Skipping {os.path.basename(qna_file)}. Missing required column '{ANSWER_COLUMN}'.")
            continue

        # Optional: Check if the row count matches expectations
        if EXPECTED_ROW_COUNT is not None and len(temp_df) != EXPECTED_ROW_COUNT:
            print(f"  Warning: File {os.path.basename(qna_file)} has {len(temp_df)} rows, expected {EXPECTED_ROW_COUNT}. Alignment might be incorrect.")

        # Extract the answer column and rename it
        answer_series = temp_df[ANSWER_COLUMN].rename(f"Answer_{model_name}")
        all_answers.append(answer_series)
        print(f"  Extracted answers for {model_name}.")

    except pd.errors.EmptyDataError:
        print(f"  Warning: Skipping empty file {os.path.basename(qna_file)}.")
    except Exception as e:
        print(f"  Warning: Error processing file {os.path.basename(qna_file)}: {e}")

# Concatenate all answer Series horizontally
if not all_answers:
    print("No answer columns were extracted. Output file will be empty.")
    final_df = pd.DataFrame()
else:
    final_df = pd.concat(all_answers, axis=1)
    print(f"\nConcatenated answers from {len(final_df.columns)} sources.")

# --- Save Results ---
print(f"Saving answer comparison results to {OUTPUT_FILE}...")
try:
    final_df.to_csv(OUTPUT_FILE, index=False, quoting=1, encoding='utf-8')
    print(f"Successfully created answer comparison file: {OUTPUT_FILE}")
except Exception as e:
    print(f"Error writing output file {OUTPUT_FILE}: {e}")

print("Consolidation script finished.")
