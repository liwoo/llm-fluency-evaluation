"""
multi_llm.py - A script to compare responses from different LLM providers using LangChain
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# Load environment variables from .env file
load_dotenv()

# Check if API keys are available
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY not found in environment variables")
    
if not os.getenv("ANTHROPIC_API_KEY"):
    print("Warning: ANTHROPIC_API_KEY not found in environment variables")
    
if not os.getenv("GROQ_API_KEY"):
    print("Warning: GROQ_API_KEY not found in environment variables")

def initialize_models():
    """Initialize LLM models from different providers."""
    models = {}
    
    # Initialize OpenAI
    if os.getenv("OPENAI_API_KEY"):
        models["openai"] = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7
        )
    
    # Initialize Claude
    if os.getenv("ANTHROPIC_API_KEY"):
        models["claude"] = ChatAnthropic(
            model="claude-3-opus-20240229",
            temperature=0.7
        )
    
    # Initialize Groq
    if os.getenv("GROQ_API_KEY"):
        models["groq"] = ChatGroq(
            model="llama3-70b-8192",
            temperature=0.7
        )
    
    return models

def run_prompt(models, prompt):
    """Run the same prompt on all available models and collect responses."""
    results = {}
    
    for model_name, model in models.items():
        try:
            messages = [HumanMessage(content=prompt)]
            response = model.invoke(messages)
            results[model_name] = response.content
            print(f"\n--- {model_name.upper()} RESPONSE ---")
            print(response.content)
        except Exception as e:
            results[model_name] = f"Error: {str(e)}"
            print(f"\n--- {model_name.upper()} ERROR ---")
            print(f"Error: {str(e)}")
    
    return results

def run_chain_example(models):
    """Run a simple LangChain example with a prompt template."""
    print("\n=== RUNNING CHAIN EXAMPLE ===")
    
    # Define a prompt template
    template = """
    You are a helpful assistant that provides concise answers.
    
    Question: {question}
    
    Please provide a brief answer in 2-3 sentences.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    for model_name, model in models.items():
        try:
            # Create a chain
            chain = LLMChain(llm=model, prompt=prompt)
            
            # Run the chain
            result = chain.invoke({"question": "What is the significance of the Fermi Paradox?"})
            
            print(f"\n--- {model_name.upper()} CHAIN RESPONSE ---")
            print(result["text"])
        except Exception as e:
            print(f"\n--- {model_name.upper()} CHAIN ERROR ---")
            print(f"Error: {str(e)}")

def main():
    # Initialize models
    print("Initializing models...")
    models = initialize_models()
    
    if not models:
        print("No API keys found. Please add your API keys to the .env file.")
        return
    
    # Simple direct prompt example
    print("\n=== RUNNING DIRECT PROMPT EXAMPLE ===")
    prompt = "Explain quantum computing to a 10-year-old in 3 sentences."
    run_prompt(models, prompt)
    
    # Run a chain example
    run_chain_example(models)

if __name__ == "__main__":
    main()
