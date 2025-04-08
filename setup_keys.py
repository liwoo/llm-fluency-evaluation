"""
setup_keys.py - A simple script to help the user set up their API keys
"""

import os
import sys
from dotenv import load_dotenv, set_key

def main():
    # Check if .env file exists, if not create it
    env_path = ".env"
    if not os.path.exists(env_path):
        open(env_path, 'w').close()
        print("Created new .env file")
    
    # Load existing environment variables
    load_dotenv(env_path)
    
    # Define the API keys to set up
    api_keys = {
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic (Claude)",
        "GROQ_API_KEY": "Groq"
    }
    
    print("=== LangChain Multi-LLM API Key Setup ===")
    print("This script will help you set up your API keys for different LLM providers.")
    print("You can skip any provider by leaving the input blank.")
    print()
    
    for env_var, provider in api_keys.items():
        current_value = os.getenv(env_var, "")
        masked_value = ""
        
        if current_value:
            # Mask the API key for display
            masked_value = current_value[:4] + "*" * (len(current_value) - 8) + current_value[-4:]
            print(f"Current {provider} API key: {masked_value}")
            update = input(f"Update {provider} API key? (y/n): ").lower()
            
            if update != 'y':
                print(f"Keeping existing {provider} API key")
                continue
        
        new_key = input(f"Enter your {provider} API key (or press Enter to skip): ").strip()
        
        if new_key:
            # Write to .env file
            set_key(env_path, env_var, new_key)
            print(f"{provider} API key updated")
        elif not current_value:
            print(f"{provider} API key not set")
    
    print("\nAPI key setup complete!")
    print("You can now run the sample scripts:")
    print("- python multi_llm.py")
    print("- python advanced_example.py")
    print("- python compare_llms.py")

if __name__ == "__main__":
    main()
