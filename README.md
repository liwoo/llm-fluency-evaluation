# LLM Fluency Evaluation for Under-Represented Languages

This project evaluates and compares the fluency of various Large Language Models (LLMs) in under-represented languages, with a primary focus on Kinyarwanda. It helps assess which models perform best for specific languages, enabling better data governance and more inclusive AI applications.

## Project Overview

The global AI landscape often overlooks languages with fewer digital resources. This project addresses this gap by:

1. Evaluating multiple LLMs' ability to understand and generate fluent responses in under-represented languages
2. Providing comparative analysis across different service providers and model sizes
3. Creating a framework for systematic evaluation of language fluency
4. Supporting data governance by identifying the most appropriate models for specific language tasks

## Supported LLM Providers

The project currently supports evaluation across these LLM providers:

- **OpenAI**: GPT-4o, GPT-3.5-Turbo, GPT-4-Turbo
- **Anthropic**: Claude-3-Sonnet, Claude-3-Haiku
- **Groq**: Llama3-70B (via Groq API)
- **Google**: Gemini Flash 2.0
- **Google Translate**: For baseline comparison
- **Digital Umuganda MT**: Locally developed machine translation service for Kinyarwanda
- **Other local MT services**: Can be integrated through the flexible input system

## Dataset

The project uses a dataset of Kinyarwanda questions across various service categories:
- Government services (Irembo)
- Land registration
- Passport services
- Permits and licenses
- National ID and documentation
- Tax services
- Marriage registration
- And more

Each question is evaluated for fluency on a scale of 1-10, with model-generated responses collected and compared.

### Flexible Data Input

The system is designed to work with any language or domain by providing custom data in the `data/input` directory. The input files should follow this format:

```csv
question,language,topic
"What is your question here?",language_code,topic_category
```

For example:
```csv
"Kubera iki mumaze igihe kinini mutaduha uburenganzira bwo gufungura Irembo ryacu?",kinyarwanda,Irembo Services
"How do I apply for a passport?",english,Passport Services
"Comment puis-je payer mes impôts?",french,Taxes
```

This flexible structure allows you to evaluate LLM fluency in any language or domain of interest.

## Setup

1. Clone this repository to your local machine.

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the provided `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Add your API keys for the LLM providers you want to use:
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   - Groq: https://console.groq.com/
   - Google (Gemini): https://aistudio.google.com/
   - RapidAPI: For certain translation services

## Usage

### Evaluating Language Fluency

To evaluate the fluency of questions in Kinyarwanda:

```bash
python evaluate_kinyarwanda_questions.py
```

This script:
1. Processes a set of Kinyarwanda questions
2. Sends them to multiple LLMs for fluency evaluation
3. Collects responses and fluency scores
4. Generates a CSV file with comparative results

### Creating Question Datasets

To create a new dataset of questions:

```bash
python create_questions_csv.py
```

### Comparing LLM Responses

To run a direct comparison of responses across different LLMs:

```bash
python compare_llms.py
```

### Consolidating Question-Answer Pairs

To consolidate question-answer pairs from multiple sources:

```bash
python consolidate_qna.py
```

## Data Governance Implications

This project supports better data governance for under-represented languages by:

1. Identifying which models provide the most fluent and accurate responses
2. Highlighting gaps in language understanding across different LLMs
3. Providing a framework for evaluating AI systems before deployment in multilingual contexts
4. Supporting more inclusive AI development that respects linguistic diversity
5. Benchmarking locally developed MT services against state-of-the-art commercial offerings
6. Enabling data-driven decisions about which language models to deploy for specific communities

## Results and Analysis

The evaluation produces CSV files containing:
- Original questions in the target language
- Topic categorization
- Responses from each LLM
- Fluency scores (1-10 scale)
- Comparative analysis across models

Initial findings show that more advanced models (GPT-4o, Claude-3-Sonnet) typically outperform smaller models, but performance varies significantly by language and topic.

### Comparing Local MT Services

A key feature of this project is the ability to compare locally developed machine translation services (like Digital Umuganda for Kinyarwanda) against global commercial offerings. This comparison helps:

1. Identify strengths and weaknesses of local MT services
2. Provide quantitative evidence of where local services excel or need improvement
3. Support the development of specialized language models for under-represented languages
4. Create a feedback loop for improving local language technologies

The analysis can reveal cases where locally-developed, specialized models outperform larger general-purpose models on specific languages or domains, highlighting the value of targeted language technology development.

## Contributing

Contributions to expand the project to other under-represented languages are welcome. Please feel free to submit pull requests or open issues for discussion.

## License

This project is available under the MIT License.
