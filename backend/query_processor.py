from langchain_openai import ChatOpenAI
from .config_loader import config
import json

def process_user_query(user_input):
    model_name = config.get('llm', 'model')
    temperature = config.get('llm', 'temperature')
    
    llm = ChatOpenAI(model=model_name, temperature=0.7)
    
    prompt = f"""You are a research paper query optimizer. Analyze the user's requirements and extract:
1. The core research topic for ArXiv search
2. Specific themes/aspects to focus on in the report
3. Report structure preferences
4. Any special requirements

User Input: {user_input}

Return a JSON object with:
- "search_query": optimized search query for ArXiv (concise, keywords-focused)
- "themes": list of specific themes/aspects to emphasize
- "structure": suggested report structure sections
- "special_requirements": any additional constraints or preferences

Example:
{{
    "search_query": "transformer attention mechanisms neural networks",
    "themes": ["efficiency improvements", "architectural innovations", "applications"],
    "structure": ["Introduction", "Methodology Comparison", "Performance Analysis", "Future Directions"],
    "special_requirements": "Focus on papers published after 2020"
}}

Respond ONLY with valid JSON, no additional text."""
    
    response = llm.invoke(prompt)
    
    try:
        parsed = json.loads(response.content)
        return parsed
    except json.JSONDecodeError:
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        return json.loads(content.strip())
