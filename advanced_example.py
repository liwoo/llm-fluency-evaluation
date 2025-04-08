"""
advanced_example.py - Demonstrates more advanced LangChain usage with multiple LLMs
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.chains import SequentialChain, LLMChain
from langchain.memory import ConversationBufferMemory

# Load environment variables from .env file
load_dotenv()

# Check for required API keys
required_keys = {
    "OpenAI": os.getenv("OPENAI_API_KEY"),
    "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "Groq": os.getenv("GROQ_API_KEY")
}

# Initialize models based on available API keys
models = {}
if required_keys["OpenAI"]:
    models["openai"] = ChatOpenAI(model="gpt-4o", temperature=0.7)
if required_keys["Anthropic"]:
    models["claude"] = ChatAnthropic(model="claude-3-opus-20240229", temperature=0.7)
if required_keys["Groq"]:
    models["groq"] = ChatGroq(model="llama3-70b-8192", temperature=0.7)

def run_structured_output_example():
    """Example of using structured output parsing with different LLMs."""
    print("\n=== STRUCTURED OUTPUT PARSING EXAMPLE ===")

    # Define the output schemas
    movie_review_schema = ResponseSchema(
        name="movie_review",
        description="A brief review of the movie."
    )
    rating_schema = ResponseSchema(
        name="rating",
        description="A rating of the movie from 1-10."
    )
    key_moments_schema = ResponseSchema(
        name="key_moments",
        description="List of 3 key moments or scenes from the movie."
    )

    # Create the output parser
    output_parser = StructuredOutputParser.from_response_schemas(
        [movie_review_schema, rating_schema, key_moments_schema]
    )

    # Create the prompt template
    prompt_template = """
    You are a film critic. Please analyze the following movie:
    
    Movie: {movie_title}
    
    {format_instructions}
    """

    # Create the prompt with format instructions
    prompt = ChatPromptTemplate.from_template(
        template=prompt_template
    )
    
    for model_name, model in models.items():
        try:
            # Format the prompt with the output parser instructions
            formatted_prompt = prompt.format(
                movie_title="Inception",
                format_instructions=output_parser.get_format_instructions()
            )
            
            # Get the response
            messages = [{"role": "user", "content": formatted_prompt}]
            response = model.invoke(messages)
            
            # Parse the response
            parsed_response = output_parser.parse(response.content)
            
            print(f"\n--- {model_name.upper()} STRUCTURED RESPONSE ---")
            print(f"Review: {parsed_response['movie_review']}")
            print(f"Rating: {parsed_response['rating']}")
            print(f"Key Moments: {parsed_response['key_moments']}")
            
        except Exception as e:
            print(f"\n--- {model_name.upper()} ERROR ---")
            print(f"Error: {str(e)}")

def run_multi_chain_example():
    """Example of using multiple chains with memory."""
    print("\n=== MULTI-CHAIN WITH MEMORY EXAMPLE ===")
    
    # Select the first available model
    if not models:
        print("No API keys found. Please add your API keys to the .env file.")
        return
    
    model_name, model = next(iter(models.items()))
    print(f"Using {model_name} for this example")
    
    # First chain: Generate a story concept
    concept_template = """
    Generate a short story concept about {topic}. 
    The concept should include a main character and a central conflict.
    """
    concept_prompt = ChatPromptTemplate.from_template(concept_template)
    concept_memory = ConversationBufferMemory(input_key="topic", memory_key="chat_history")
    concept_chain = LLMChain(
        llm=model,
        prompt=concept_prompt,
        output_key="concept",
        memory=concept_memory,
        verbose=True
    )
    
    # Second chain: Expand the concept into a story
    story_template = """
    Based on the following concept:
    
    {concept}
    
    Write a short story (about 3-4 paragraphs) that develops this concept.
    """
    story_prompt = ChatPromptTemplate.from_template(story_template)
    story_memory = ConversationBufferMemory(input_key="concept", memory_key="chat_history")
    story_chain = LLMChain(
        llm=model,
        prompt=story_prompt,
        output_key="story",
        memory=story_memory,
        verbose=True
    )
    
    # Chain them together
    sequential_chain = SequentialChain(
        chains=[concept_chain, story_chain],
        input_variables=["topic"],
        output_variables=["concept", "story"],
        verbose=True
    )
    
    # Run the chain
    result = sequential_chain.invoke({"topic": "a time traveler who accidentally changes history"})
    
    print("\n--- STORY CONCEPT ---")
    print(result["concept"])
    print("\n--- FULL STORY ---")
    print(result["story"])

def main():
    if not models:
        print("No API keys found. Please add your API keys to the .env file.")
        return
    
    print(f"Found {len(models)} configured LLM(s): {', '.join(models.keys())}")
    
    # Run examples
    run_structured_output_example()
    run_multi_chain_example()

if __name__ == "__main__":
    main()
