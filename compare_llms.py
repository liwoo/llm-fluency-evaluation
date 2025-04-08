"""
compare_llms.py - Script to compare responses from different LLMs for the same prompt
"""

import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from prompt_templates import get_template

# Load environment variables from .env file
load_dotenv()

# Initialize models based on available API keys
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

def compare_responses(models, prompt_template, prompt_inputs, save_to_file=None):
    """Run the same prompt on all available models and compare responses."""
    # Format the prompt
    prompt = prompt_template.format(**prompt_inputs)
    
    # Store results
    results = {}
    
    print("\n=== PROMPT ===")
    print(prompt)
    
    # Get responses from each model
    for model_name, model in models.items():
        try:
            messages = [{"role": "user", "content": prompt}]
            response = model.invoke(messages)
            results[model_name] = response.content
            
            print(f"\n=== {model_name.upper()} RESPONSE ===")
            print(response.content)
            
        except Exception as e:
            results[model_name] = f"Error: {str(e)}"
            print(f"\n=== {model_name.upper()} ERROR ===")
            print(f"Error: {str(e)}")
    
    # Save results to a file if requested
    if save_to_file:
        with open(save_to_file, 'w') as f:
            output = {
                "prompt": prompt,
                "responses": results
            }
            json.dump(output, f, indent=2)
            print(f"\nResults saved to {save_to_file}")
    
    return results

def run_comparisons():
    """Run various comparisons between different LLMs."""
    # Initialize models
    models = initialize_models()
    
    if not models:
        print("No API keys found. Please add your API keys to the .env file.")
        return
    
    print(f"Found {len(models)} configured LLM(s): {', '.join(models.keys())}")
    
    # Example 1: Summarization
    print("\n\n=== EXAMPLE 1: SUMMARIZATION ===")
    summarization_template = get_template("summarization")
    summarization_inputs = {
        "content": """
        Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. 
        AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals.
        The term "artificial intelligence" had previously been used to describe machines that mimic and display "human" cognitive skills that are associated with the human mind, such as "learning" and "problem-solving". 
        This definition has since been rejected by major AI researchers who now describe AI in terms of rationality and acting rationally, which does not limit how intelligence can be articulated.
        AI applications include advanced web search engines, recommendation systems, understanding human speech, self-driving cars, automated decision-making, and competing at the highest level in strategic game systems.
        As machines become increasingly capable, tasks considered to require "intelligence" are often removed from the definition of AI, a phenomenon known as the AI effect.
        """,
        "length": "2-3 sentences"
    }
    compare_responses(models, summarization_template, summarization_inputs, "summarization_results.json")
    
    # Example 2: Creative Writing
    print("\n\n=== EXAMPLE 2: CREATIVE WRITING ===")
    creative_template = get_template("creative_writing")
    creative_inputs = {
        "style": "short story",
        "topic": "a world where dreams become reality",
        "tone": "mysterious and thought-provoking",
        "length": "3 paragraphs"
    }
    compare_responses(models, creative_template, creative_inputs, "creative_results.json")
    
    # Example 3: Code Generation
    print("\n\n=== EXAMPLE 3: CODE GENERATION ===")
    code_template = get_template("code_generation")
    code_inputs = {
        "language": "Python",
        "task": "Create a function that calculates the Fibonacci sequence up to n terms using memoization",
        "requirements": "- Include type hints\n- Include docstring\n- Handle edge cases"
    }
    compare_responses(models, code_template, code_inputs, "code_results.json")

if __name__ == "__main__":
    run_comparisons()
