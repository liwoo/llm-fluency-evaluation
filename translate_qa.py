\
import os
import pandas as pd
from dotenv import load_dotenv
from google.cloud import translate_v2 as translate
from openai import OpenAI
import time # Import time for potential rate limiting delays

# --- Configuration ---
INPUT_CSV_PATH = "data/google-analytics-qna.csv"
OUTPUT_CSV_PATH = "data/google-analytics-qna.csv" # Overwrite the input file
SOURCE_LANGUAGE = "rw" # Kinyarwanda ISO 639-1 code
TARGET_LANGUAGE_ENGLISH = "en"
TARGET_LANGUAGE_KINYARWANDA = "rw"
OPENAI_MODEL = "gpt-3.5-turbo" # Or choose another model like gpt-4o if preferred
QUESTION_COLUMN = "Question" # Assuming this is the header in your CSV
ANSWER_COLUMN = "Answer"

# --- Load Environment Variables ---
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
# GOOGLE_APPLICATION_CREDENTIALS is automatically used by the library
# if the environment variable is set.

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file.")
# No explicit check for GOOGLE_APPLICATION_CREDENTIALS needed here,
# the library handles it. If it's not set or invalid, an error will occur later.

# --- Initialize Clients ---
translate_client = translate.Client()
openai_client = OpenAI(api_key=openai_api_key)

# --- Helper Functions ---
def translate_text(text: str, target_language: str, source_language: str = None) -> str:
    """Translates text using Google Cloud Translation API."""
    if not text or pd.isna(text):
        return "" # Handle empty or NaN inputs
    try:
        result = translate_client.translate(
            text,
            target_language=target_language,
            source_language=source_language # Optional, let Google detect if None
        )
        # Add a small delay to potentially avoid hitting rate limits
        # time.sleep(0.1)
        return result['translatedText']
    except Exception as e:
        print(f"Error translating '{text}': {e}")
        return f"[Translation Error: {e}]"

def get_openai_answer(question_en: str) -> str:
    """Gets an answer from OpenAI based on the English question."""
    if not question_en:
        return "" # Handle empty input
    try:
        prompt = f"""
        You are an assistant providing information about Irembo services in Rwanda.
        Answer the following question concisely and helpfully in English (1-3 sentences).
        Question: {question_en}
        Answer:
        """
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an assistant for Irembo services."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5, # Adjust for creativity vs consistency
            max_tokens=100
        )
        # Add a small delay
        # time.sleep(0.1)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting OpenAI answer for '{question_en}': {e}")
        return f"[OpenAI Error: {e}]"

# --- Main Script ---
print(f"Loading questions from {INPUT_CSV_PATH}...")
try:
    df = pd.read_csv(INPUT_CSV_PATH, keep_default_na=False) # Avoid interpreting 'NA' as NaN
    if QUESTION_COLUMN not in df.columns:
         raise ValueError(f"Column '{QUESTION_COLUMN}' not found in {INPUT_CSV_PATH}")

except FileNotFoundError:
    print(f"Error: Input file not found at {INPUT_CSV_PATH}")
    exit(1)
except pd.errors.EmptyDataError:
     print(f"Error: Input file {INPUT_CSV_PATH} is empty.")
     exit(1)
except Exception as e:
    print(f"Error reading CSV {INPUT_CSV_PATH}: {e}")
    exit(1)


print(f"Processing {len(df)} questions...")

results = []
for index, row in df.iterrows():
    question_rw = row[QUESTION_COLUMN]
    print(f"  Processing question {index + 1}/{len(df)}: '{question_rw[:50]}...'")

    # 1. Translate Kinyarwanda Question -> English
    print("    Translating to English...")
    question_en = translate_text(question_rw, TARGET_LANGUAGE_ENGLISH, SOURCE_LANGUAGE)
    if "[Translation Error:" in question_en:
         print(f"    Skipping due to translation error.")
         results.append({'Question': question_rw, 'Answer': '[Processing Error]'})
         continue # Skip to next question if translation failed

    # 2. Get English Answer from OpenAI
    print("    Getting English answer from OpenAI...")
    answer_en = get_openai_answer(question_en)
    if "[OpenAI Error:" in answer_en:
        print(f"    Skipping due to OpenAI error.")
        results.append({'Question': question_rw, 'Answer': '[Processing Error]'})
        continue # Skip to next question if OpenAI failed

    # 3. Translate English Answer -> Kinyarwanda
    print("    Translating answer back to Kinyarwanda...")
    answer_rw = translate_text(answer_en, TARGET_LANGUAGE_KINYARWANDA, TARGET_LANGUAGE_ENGLISH)
    if "[Translation Error:" in answer_rw:
         print(f"    Warning: Failed to translate answer back to Kinyarwanda.")
         # Store the English answer or an error message? Storing error for now.
         results.append({'Question': question_rw, 'Answer': '[Answer Translation Error]'})
         continue


    results.append({'Question': question_rw, 'Answer': answer_rw})
    print("    Done.")


# --- Save Results ---
print(f"\nSaving results to {OUTPUT_CSV_PATH}...")
output_df = pd.DataFrame(results)

# Ensure columns are correctly quoted for CSV standard
output_df.to_csv(OUTPUT_CSV_PATH, index=False, quoting=1) # quoting=1 corresponds to csv.QUOTE_ALL

print("Script finished successfully!")
