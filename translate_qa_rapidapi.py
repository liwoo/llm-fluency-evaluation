import os
import pandas as pd
from dotenv import load_dotenv
import requests
from openai import OpenAI
import time
import json

# --- Configuration ---
CSV_FILE_PATH = "data/digital-umuganda-mt-qna.csv"
SOURCE_LANGUAGE = "rw"
TARGET_LANGUAGE_ENGLISH = "en"
TARGET_LANGUAGE_KINYARWANDA = "rw"
OPENAI_MODEL = "gpt-3.5-turbo"
QUESTION_COLUMN = "Question" # Make sure this matches the header in your CSV
ANSWER_COLUMN = "Answer"
RAPIDAPI_ENDPOINT = "https://du_mt_api.p.rapidapi.com/api/v1/translate"
# Models from API documentation
MODEL_RW_EN = "MULTI-rw-en"
MODEL_EN_RW = "MULTI-en-rw"
REQUEST_TIMEOUT = 30 # Timeout for API requests in seconds

# --- Load Environment Variables ---
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
rapidapi_key = os.getenv("RAPID_API_KEY") # Note: Key name changed in .env

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file.")
if not rapidapi_key:
    raise ValueError("RAPID_API_KEY not found in .env file.")

# --- Initialize Clients ---
openai_client = OpenAI(api_key=openai_api_key)

# --- Helper Functions ---
def translate_digital_umuganda(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translates text using the Digital Umuganda MT API via RapidAPI."""
    if not text or pd.isna(text):
        return ""

    if src_lang == "rw" and tgt_lang == "en":
        model = MODEL_RW_EN
    elif src_lang == "en" and tgt_lang == "rw":
        model = MODEL_EN_RW
    else:
        print(f"Error: Unsupported language pair: {src_lang} -> {tgt_lang}")
        return "[Unsupported Language Pair]"

    payload = {
        "src": src_lang,
        "tgt": tgt_lang,
        "use_multi": model,
        "text": text
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "du_mt_api.p.rapidapi.com"
    }

    try:
        response = requests.post(RAPIDAPI_ENDPOINT, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        response_data = response.json()
        if "translation" in response_data:
            # Add a small delay
            # time.sleep(0.2) # Slightly longer delay might be needed for rate limits
            return response_data["translation"]
        else:
            print(f"Error: Unexpected response format from RapidAPI: {response_data}")
            return "[Translation API Response Format Error]"

    except requests.exceptions.RequestException as e:
        print(f"Error translating '{text[:30]}...' with RapidAPI: {e}")
        # Check if response exists and has content before trying to parse JSON
        error_detail = "Unknown error"
        if e.response is not None:
            try:
                error_detail = e.response.json()
            except json.JSONDecodeError:
                error_detail = e.response.text # Use raw text if not JSON
        return f"[Translation API Request Error: {error_detail}]"
    except Exception as e:
        print(f"Unexpected error during translation: {e}")
        return "[Unexpected Translation Error]"

def get_openai_answer(question_en: str) -> str:
    """Gets an answer from OpenAI based on the English question."""
    if not question_en:
        return ""
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
            temperature=0.5,
            max_tokens=100
        )
        # Add a small delay
        # time.sleep(0.1)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting OpenAI answer for '{question_en[:30]}...': {e}")
        return f"[OpenAI Error: {e}]"

# --- Main Script ---
print(f"Loading questions from {CSV_FILE_PATH}...")
try:
    # Specify encoding, as default might not work for Kinyarwanda characters
    df = pd.read_csv(CSV_FILE_PATH, keep_default_na=False, encoding='utf-8')
    if QUESTION_COLUMN not in df.columns:
         raise ValueError(f"Column '{QUESTION_COLUMN}' not found in {CSV_FILE_PATH}")

except FileNotFoundError:
    print(f"Error: File not found at {CSV_FILE_PATH}")
    exit(1)
except pd.errors.EmptyDataError:
     print(f"Error: Input file {CSV_FILE_PATH} is empty.")
     exit(1)
except Exception as e:
    print(f"Error reading CSV {CSV_FILE_PATH}: {e}")
    exit(1)

print(f"Processing {len(df)} questions...")

results = []
for index, row in df.iterrows():
    question_rw = row[QUESTION_COLUMN]
    print(f"\nProcessing question {index + 1}/{len(df)}: '{question_rw[:50]}...'")

    # --- Step 1: Translate Kinyarwanda Question -> English ---
    print("    Translating RW -> EN using Digital Umuganda API...")
    question_en = translate_digital_umuganda(question_rw, SOURCE_LANGUAGE, TARGET_LANGUAGE_ENGLISH)
    if "[Translation" in question_en or "[Unsupported" in question_en:
         print(f"    Skipping due to RW->EN translation error: {question_en}")
         results.append({'Question': question_rw, 'Answer': '[Processing Error: RW->EN Translation Failed]'})
         continue
    print(f"      English Question: {question_en[:60]}...")

    # --- Step 2: Get English Answer from OpenAI ---
    print("    Getting English answer from OpenAI...")
    answer_en = get_openai_answer(question_en)
    if "[OpenAI Error:" in answer_en:
        print(f"    Skipping due to OpenAI error: {answer_en}")
        results.append({'Question': question_rw, 'Answer': '[Processing Error: OpenAI Failed]'})
        continue
    print(f"      English Answer: {answer_en[:60]}...")

    # --- Step 3: Translate English Answer -> Kinyarwanda ---
    print("    Translating EN -> RW using Digital Umuganda API...")
    answer_rw = translate_digital_umuganda(answer_en, TARGET_LANGUAGE_ENGLISH, TARGET_LANGUAGE_KINYARWANDA)
    if "[Translation" in answer_rw or "[Unsupported" in answer_rw:
         print(f"    Warning: Failed to translate answer EN->RW: {answer_rw}")
         results.append({'Question': question_rw, 'Answer': '[Processing Error: EN->RW Translation Failed]'})
         continue
    print(f"      Kinyarwanda Answer: {answer_rw[:60]}...")


    results.append({'Question': question_rw, 'Answer': answer_rw})
    print("    Done.")


# --- Save Results ---
print(f"\nSaving results to {CSV_FILE_PATH}...")
output_df = pd.DataFrame(results)

# Ensure columns are correctly quoted for CSV standard and specify encoding
output_df.to_csv(CSV_FILE_PATH, index=False, quoting=1, encoding='utf-8') # csv.QUOTE_ALL

print("Script finished successfully!")
