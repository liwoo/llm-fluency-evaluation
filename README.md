# LangChain Multi-LLM Project

This project demonstrates how to use LangChain to run prompts with multiple LLM providers: OpenAI, Claude (Anthropic), and Groq.

## Setup

1. Make sure you have Python 3 installed on your Mac.

2. Clone or download this repository to your local machine.

3. Navigate to the project directory:
   ```
   cd /Users/jeremiahchienda/CascadeProjects/langchain-multi-llm
   ```

4. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

5. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

6. Create a `.env` file from the provided `.env.example`:
   ```
   cp .env.example .env
   ```

7. Edit the `.env` file and add your API keys for the LLM providers you want to use:
   - OpenAI: Get your API key from https://platform.openai.com/api-keys
   - Anthropic (Claude): Get your API key from https://console.anthropic.com/
   - Groq: Get your API key from https://console.groq.com/

## Running the Script

After setting up your environment and API keys, run the script:

```
python multi_llm.py
```

This will:
1. Run a simple direct prompt across all configured LLMs
2. Run a LangChain chain example with a prompt template

## Extending the Project

You can modify the script to:
- Add more LLM providers
- Change the models used for each provider
- Create more sophisticated chains and workflows
- Build applications that leverage multiple LLMs

## Requirements

This project uses the following packages:
- langchain
- langchain-openai
- langchain-anthropic
- langchain-groq
- python-dotenv
