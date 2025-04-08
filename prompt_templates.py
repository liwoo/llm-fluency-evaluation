"""
prompt_templates.py - A collection of reusable prompt templates for different tasks
"""

from langchain.prompts import ChatPromptTemplate

# Basic templates for common tasks

SUMMARIZATION_TEMPLATE = ChatPromptTemplate.from_template("""
You are an AI assistant that specializes in summarizing content.

Content to summarize:
{content}

Please provide a {length} summary of the above content.
Focus on the most important points and key takeaways.
""")

CREATIVE_WRITING_TEMPLATE = ChatPromptTemplate.from_template("""
You are a creative writing assistant.

Please write a {style} about {topic}.
The tone should be {tone} and it should be approximately {length} long.
""")

COMPARISON_TEMPLATE = ChatPromptTemplate.from_template("""
You are an analytical assistant that specializes in comparing items.

Item 1: {item1}
Item 2: {item2}

Please compare these items based on the following criteria:
{criteria}

Provide a balanced analysis highlighting similarities and differences.
""")

CODE_GENERATION_TEMPLATE = ChatPromptTemplate.from_template("""
You are a coding assistant.

Please write {language} code that accomplishes the following task:
{task}

The code should be:
- Well-commented
- Efficient
- Follow best practices for {language}

Additional requirements:
{requirements}
""")

QA_TEMPLATE = ChatPromptTemplate.from_template("""
You are a knowledgeable assistant.

Context information:
{context}

Based on the context above, please answer the following question:
{question}

If the answer is not in the context, please say "I don't have enough information to answer this question."
""")

# Function to get a template by name
def get_template(template_name):
    """Get a prompt template by name."""
    templates = {
        "summarization": SUMMARIZATION_TEMPLATE,
        "creative_writing": CREATIVE_WRITING_TEMPLATE,
        "comparison": COMPARISON_TEMPLATE,
        "code_generation": CODE_GENERATION_TEMPLATE,
        "qa": QA_TEMPLATE,
    }
    
    return templates.get(template_name.lower())
