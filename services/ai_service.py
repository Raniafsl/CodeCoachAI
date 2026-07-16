import json
import os

import ollama
from ollama import Client


def get_ollama_client():
    """
    Use Ollama Cloud when an API key exists.
    Otherwise, use the local Ollama server.
    """

    api_key = os.environ.get("OLLAMA_API_KEY")

    if api_key:
        return Client(
            host="https://ollama.com",
            headers={
                "Authorization": f"Bearer {api_key}"
            }
        )

    return ollama.Client()


def get_model_name():
    """
    Use the model set by the hosting platform.
    Default to the local model on this computer.
    """

    return os.environ.get(
        "OLLAMA_MODEL",
        "llama3.2:3b"
    )


def clean_json_response(text):
    """
    Removes common Markdown formatting before parsing JSON.
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def generate_ai_analysis(code, feedback, course, problem=""):

    prompt = f"""
You are CodeCoach AI, an experienced Computer Science Teaching Assistant.

Course:
{course}

Programming problem:
{problem}

Student code:
{code}

Rule-based feedback:
{feedback}

Evaluate:

1. Correctness
2. Readability
3. Bugs and edge cases
4. Variable naming
5. Time complexity
6. Space complexity
7. Possible improvements

Return ONLY valid JSON.

Do not use Markdown.
Do not include text before or after the JSON.

Use exactly these string fields:

{{
    "explanation": "...",
    "bugs": "...",
    "improved_code": "...",
    "complexity": "...",
    "learning_tips": "..."
}}
"""

    fallback = {
        "explanation": "AI analysis is currently unavailable.",
        "bugs": "No AI bug analysis was generated.",
        "improved_code": "",
        "complexity": "No complexity analysis was generated.",
        "learning_tips": "Please try again later."
    }

    try:
        client = get_ollama_client()
        model = get_model_name()

        response = client.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a programming tutor. "
                        "Return only valid JSON with string values."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0
            }
        )

        text = response["message"]["content"]
        cleaned_text = clean_json_response(text)
        result = json.loads(cleaned_text)

        return {
            "explanation": str(result.get("explanation", "")),
            "bugs": str(result.get("bugs", "")),
            "improved_code": str(result.get("improved_code", "")),
            "complexity": str(result.get("complexity", "")),
            "learning_tips": str(result.get("learning_tips", ""))
        }

    except json.JSONDecodeError:
        fallback["bugs"] = (
            "The AI response could not be parsed. Please try again."
        )
        return fallback

    except Exception as error:
        fallback["bugs"] = f"AI connection error: {error}"
        return fallback