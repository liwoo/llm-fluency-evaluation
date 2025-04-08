"""
evaluate_kinyarwanda_questions.py - Evaluate Kinyarwanda questions across multiple LLMs for fluency
"""

import os
import csv
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from googletrans import Translator
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Load environment variables
load_dotenv()

# Define the questions
KINYARWANDA_QUESTIONS = [
    "Kubera iki mumaze igihe kinini mutaduha uburenganzira bwo gufungura Irembo ryacu? Ndashaka nanjye kujya mfasha abantu kubona serivisi z'Irembo",
    "Ese umuntu ashaka akazi mu Irembo yabavugisha gute?",
    "Icyangombwa cyanjye cy'ubutaka narakibuze kandi ngejeje igihe cyo gutanga umusoro, ubwo nakibona gute ngo mbashe kwishyura imisoro",
    "Ese ko mbona gusaba pasiporo bitari gukunda mwamfasha kuyinsabira",
    "Ese Irembo, iyo umuntu amaze kwiyandikisha kuri permit ntabone code yiwe biba byagenze gute ubwo?",
    "Aka message mwampaye narakabuze kandi ejo mfite examen. nakabona gute?",
    "Icyumweru gishize niyandikishije ku kizami ariko sinibuka italiki y'ikizamini. Munyibutse italiki",
    "Nijoro niyandikishije ariko ndi kwishyura bikanga. Kandi ndabishaka cyane mumfashe",
    "Nasabye icyemezo gisimbura indangamuntu ariko ntabwo nibuka numero yanjye ya dosiye. Mwanyibutsa?",
    "Ndikugerageza kudownloadinga icyemezo cyanjye cy'amavuko nk'ibisanzwe ariko ntibikunda sinzi ikibazo kirimo",
    "Maze kwiyandikisha ariko nsanze nashyizemo kuzakorera Rusizi kandi nashakaga Musanze. Munkuriremo iyo dosiye nongere niyandikishe",
    "Ese birashoboka ko mwampindurira uwo twari kuzashakana nkashyiraho undi. Nandikishije ishyingirwa ariko uwo twari kuzashakana yarabyanze nshaka undi",
    "Ndashaka kwishyura imisoro hakiri kare bataramfungira.",
    "Nabonye ku mbuga zanyu mwatumenyesheje ko mushobora kudufasha gusimbuza amafoto yo ku ndangamuntu, ndasabwa iki?",
    "Mu kwiyandikisha kuri permit, kuki buri gihe nsangamo imyanya yo muri Busanza gusa?",
    "Maze kwishyura Traffic fine ariko nsanga n'umushoferi wanjye nawe yishyuye, ubwo ayo mafaranga turayasubizwa bigenze gute?",
    "ko ubushize nasabye icyemezo cy'uko ntafunzwe nkahita nkibona, ubu bwo kuki cyatinze? kimaze icyumweru kirenga.",
    "Twasabye ibyemezo by'uko tutafunzwe njye na madamu n'umuhungu wanjye ariko bo barabibonye njye sinzi impamvu byatinze",
    "Nifuzaga kumenya aho icyangombwa cyanjye cy'ubutaka kigeze kuko twakoze mutation ukwezi gushize kandi sindabona icyangombwa cyanjye",
    "Mvuye mu kizamini ariko nahise nzimya machine ntabonye amanota yanjye, mwamfasha kuyamenya"
]

# Define topic categories for mapping
TOPIC_CATEGORIES = {
    "irembo": "Irembo Services",
    "akazi": "Employment",
    "ubutaka": "Land Registration",
    "pasiporo": "Passport Services",
    "permit": "Permits and Licenses",
    "examen": "Examinations",
    "kizami": "Examinations",
    "indangamuntu": "National ID",
    "icyemezo": "Certificates",
    "amavuko": "Birth Certificate",
    "ishyingirwa": "Marriage Registration",
    "imisoro": "Taxes",
    "amafoto": "Documentation",
    "Traffic fine": "Traffic Fines",
    "ntafunzwe": "Criminal Record Certificate",
    "machine": "Technical Issues",
    "amanota": "Examinations"
}

# Initialize language models
def initialize_models():
    """Initialize the language models to be used for evaluation."""
    models = {}
    
    # OpenAI models
    if os.getenv("OPENAI_API_KEY"):
        models["gpt-4o"] = ChatOpenAI(model="gpt-4o", temperature=0)
        
        try:
            models["gpt-3.5-turbo"] = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        except:
            print("Warning: gpt-3.5-turbo model not available")
            
        try:
            models["gpt-4-turbo"] = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
        except:
            print("Warning: gpt-4-turbo-preview model not available")
    
    # Claude models
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            models["claude-3-sonnet"] = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0)
        except:
            print("Warning: claude-3-sonnet model not available")
            
        try:
            models["claude-3-haiku"] = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0)
        except:
            print("Warning: claude-3-haiku model not available")
    
    # Groq model
    if os.getenv("GROQ_API_KEY"):
        try:
            models["grok-3"] = ChatGroq(model="llama3-70b-8192", temperature=0)
        except:
            print("Warning: grok model not available")
    
    return models

def translate_with_google(text, src='rw', dest='en'):
    """Translate text using Google Translate."""
    try:
        translator = Translator()
        result = translator.translate(text, src=src, dest=dest)
        return result.text
    except Exception as e:
        print(f"Google Translate error: {str(e)}")
        return f"Error: {str(e)}"

def detect_topic_category(question):
    """Detect the topic category based on keywords in the question."""
    question_lower = question.lower()
    
    for keyword, category in TOPIC_CATEGORIES.items():
        if keyword.lower() in question_lower:
            return category
    
    return "Other"

def evaluate_fluency(model, question, model_name):
    """Evaluate the fluency of a Kinyarwanda question using the provided model."""
    try:
        prompt_template = """
        You are a fluency evaluator for Kinyarwanda language. 
        
        Please evaluate the fluency of the following Kinyarwanda question on a scale of 1-10, 
        where 1 is completely unnatural and 10 is perfectly natural, fluent Kinyarwanda.
        
        Only respond with a single number between 1 and 10, with no additional explanations.
        
        Question: {question}
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        formatted_prompt = prompt.format(question=question)
        
        messages = [{"role": "user", "content": formatted_prompt}]
        response = model.invoke(messages)
        
        # Extract just the number from the response
        score = response.content.strip()
        # Handle potential non-numeric responses
        try:
            score = int(score)
            if score < 1:
                score = 1
            elif score > 10:
                score = 10
        except:
            print(f"Non-numeric score from {model_name}: {score}, defaulting to 5")
            score = 5
            
        return score
    except Exception as e:
        print(f"Error evaluating with {model_name}: {str(e)}")
        return "Error"

def answer_question(model, question):
    """Generate an answer for a Kinyarwanda question using the provided model."""
    try:
        prompt_template = """
        You are a helpful assistant who speaks fluent Kinyarwanda. 
        
        Respond to the following question in Kinyarwanda. Keep your answer professional, 
        helpful, and concise (1-3 sentences maximum).
        
        Question: {question}
        
        Answer in Kinyarwanda:
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        formatted_prompt = prompt.format(question=question)
        
        messages = [{"role": "user", "content": formatted_prompt}]
        response = model.invoke(messages)
        
        return response.content.strip()
    except Exception as e:
        print(f"Error answering question: {str(e)}")
        return f"Error: {str(e)}"

def generate_csv():
    """Generate a CSV file with questions, answers, categories, and fluency scores."""
    # Initialize models
    print("Initializing language models...")
    models = initialize_models()
    
    if not models:
        print("No API keys found. Please add your API keys to the .env file.")
        return
    
    # Define CSV headers based on available models
    headers = ["Question", "Answer", "Topic Category"]
    model_columns = []
    
    # Add available model columns
    if "gpt-4o" in models:
        model_columns.append("gpt-4o fluency score *")
    if "gpt-3.5-turbo" in models:
        model_columns.append("gpt-03-mini fluency score *")
    if "gpt-4-turbo" in models:
        model_columns.append("gpt-01-preview fluency score *")
    if "claude-3-sonnet" in models:
        model_columns.append("claude-sonnet-3.7 fluency score *")
    if "claude-3-haiku" in models:
        model_columns.append("claude-sonnet-3.5 fluency score *")
    if "grok-3" in models:
        model_columns.append("grok-3 fluency score *")
    
    # Add Google Translate column
    model_columns.append("google-translate")
    
    headers.extend(model_columns)
    
    # Create CSV file
    csv_file_path = "kinyarwanda_evaluation.csv"
    temp_results_path = "temp_results.json"
    
    # Check if we have partial results saved
    partial_results = []
    if os.path.exists(temp_results_path):
        try:
            with open(temp_results_path, 'r', encoding='utf-8') as f:
                partial_results = json.load(f)
            print(f"Loaded {len(partial_results)} partial results from {temp_results_path}")
        except Exception as e:
            print(f"Error loading partial results: {str(e)}")
    
    # Process questions
    all_results = []
    completed_questions = [item["question"] for item in partial_results]
    
    # Add any new questions that aren't in partial results
    questions_to_process = [q for q in KINYARWANDA_QUESTIONS if q not in completed_questions]
    
    # Process each question
    print(f"Processing {len(questions_to_process)} new questions...")
    
    for i, question in enumerate(questions_to_process):
        print(f"Processing question {i+1}/{len(questions_to_process)}")
        
        # Detect topic category
        topic_category = detect_topic_category(question)
        
        # Generate an answer using one of the models (if available)
        answer = ""
        answer_model = None
        if "gpt-4o" in models:
            answer_model = models["gpt-4o"]
        elif "claude-3-sonnet" in models:
            answer_model = models["claude-3-sonnet"]
        elif models:
            # Use the first available model
            model_name, answer_model = next(iter(models.items()))
        
        if answer_model:
            print(f"Generating answer using model...")
            answer = answer_question(answer_model, question)
        
        # Evaluate fluency across models
        fluency_scores = {}
        for model_name, model in models.items():
            print(f"Evaluating fluency with {model_name}...")
            score = evaluate_fluency(model, question, model_name)
            fluency_scores[model_name] = score
        
        # Translate with Google Translate
        print("Translating with Google Translate...")
        google_translation = translate_with_google(question)
        
        # Store results
        result = {
            "question": question,
            "answer": answer,
            "topic_category": topic_category,
            "fluency_scores": fluency_scores,
            "google_translation": google_translation
        }
        
        all_results.append(result)
        
        # Save partial results after each question
        with open(temp_results_path, 'w', encoding='utf-8') as f:
            json.dump(partial_results + all_results, f, ensure_ascii=False, indent=2)
        
        # Sleep briefly to avoid rate limits
        time.sleep(1)
    
    # Combine partial and new results
    all_results = partial_results + all_results
    
    # Write to CSV
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write the headers
        writer.writerow(headers)
        
        # Write each question with its data
        for result in all_results:
            row = [
                result["question"],
                result["answer"],
                result["topic_category"]
            ]
            
            # Add fluency scores in the right order
            if "gpt-4o" in models:
                row.append(result["fluency_scores"].get("gpt-4o", ""))
            if "gpt-3.5-turbo" in models:
                row.append(result["fluency_scores"].get("gpt-3.5-turbo", ""))
            if "gpt-4-turbo" in models:
                row.append(result["fluency_scores"].get("gpt-4-turbo", ""))
            if "claude-3-sonnet" in models:
                row.append(result["fluency_scores"].get("claude-3-sonnet", ""))
            if "claude-3-haiku" in models:
                row.append(result["fluency_scores"].get("claude-3-haiku", ""))
            if "grok-3" in models:
                row.append(result["fluency_scores"].get("grok-3", ""))
            
            # Add Google translation
            row.append(result["google_translation"])
            
            writer.writerow(row)
    
    print(f"CSV file created successfully: {csv_file_path}")
    print(f"Total questions processed: {len(all_results)}")

def create_simple_csv():
    """Create a simple CSV with just the questions and empty columns for manual completion."""
    headers = [
        "Question", 
        "Answer", 
        "Topic Category", 
        "gpt-4o fluency score *", 
        "gpt-03-mini fluency score *", 
        "gpt-01-preview fluency score *", 
        "claude-sonnet-3.7 fluency score *", 
        "claude-sonnet-3.5 fluency score *", 
        "grok-3 fluency score *", 
        "gemini-flash-2.0 fluency score *", 
        "google-translate"
    ]
    
    csv_file_path = "kinyarwanda_questions_template.csv"
    
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write the headers
        writer.writerow(headers)
        
        # Add topic categories automatically
        for question in KINYARWANDA_QUESTIONS:
            topic = detect_topic_category(question)
            google_translation = ""
            try:
                # Try to get Google translation
                google_translation = translate_with_google(question)
            except:
                pass
            
            # Create a row with the question, empty answer, topic category, and empty scores
            row = [question, "", topic] + [""] * 7 + [google_translation]
            writer.writerow(row)
    
    print(f"Simple CSV template created: {csv_file_path}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Generate full CSV with model evaluations (requires API keys)")
    print("2. Create simple CSV template (only requires Google Translate)")
    
    option = "2"  # Default to simple template
    print(f"Using option {option} (simple CSV template)")
    
    if option == "1":
        generate_csv()
    else:
        create_simple_csv()
