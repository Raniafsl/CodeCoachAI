import json
import os

import ollama


def demo_analysis():
    """
    Used on the public deployed demo because the local Ollama
    model running on the developer's computer is not available online.
    """

    return {
        "explanation": (
            "The public demo is running without the local Llama model. "
            "The rule-based analyzer and scoring system are still active. "
            "Run CodeCoach locally with Ollama for the complete AI analysis."
        ),
        "bugs": (
            "AI-powered bug detection is available in the local version."
        ),
        "improved_code": "",
        "complexity": (
            "AI-generated complexity analysis is available in the local version."
        ),
        "learning_tips": (
            "Clone the GitHub repository and run Ollama with llama3.2:3b "
            "to use the complete AI tutoring features."
        )
    }


def generate_ai_analysis(code, feedback, course, problem=""):

    # Render will have DEMO_MODE set to "true".
    # On your Mac, it will be absent, so local Ollama will still run.
    if os.environ.get("DEMO_MODE", "").lower() == "true":
        return demo_analysis()

    prompt = f"""
You are CodeCoach AI, an experienced Computer Science Teaching Assistant.

The student is taking: {course}

Programming problem:
{problem}

Student code:
{code}

Rule-based feedback:
{feedback}

Analyze the student's code for:

- correctness
- readability
- bugs and edge cases
- variable naming
- time complexity
- space complexity
- possible improvements

Be clear, accurate, and beginner-friendly.

Return a result matching the required JSON structure.
"""

    schema = {
        "type": "object",
        "properties": {
            "explanation": {
                "type": "string"
            },
            "bugs": {
                "type": "string"
            },
            "improved_code": {
                "type": "string"
            },
            "complexity": {
                "type": "string"
            },
            "learning_tips": {
                "type": "string"
            }
        },
        "required": [
            "explanation",
            "bugs",
            "improved_code",
            "complexity",
            "learning_tips"
        ]
    }

    fallback = {
        "explanation": "AI analysis is currently unavailable.",
        "bugs": "No AI bug analysis was generated.",
        "improved_code": "",
        "complexity": "No complexity analysis was generated.",
        "learning_tips": "Make sure Ollama is running and try again."
    }

    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a programming tutor. "
                        "Return only data matching the supplied JSON schema."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format=schema,
            options={
                "temperature": 0
            }
        )

        text = response["message"]["content"]
        result = json.loads(text)

        return {
            "explanation": str(result.get("explanation", "")),
            "bugs": str(result.get("bugs", "")),
            "improved_code": str(result.get("improved_code", "")),
            "complexity": str(result.get("complexity", "")),
            "learning_tips": str(result.get("learning_tips", ""))
        }

    except json.JSONDecodeError:
        fallback["bugs"] = (
            "Ollama returned a response that could not be parsed."
        )
        return fallback

    except Exception as error:
        fallback["bugs"] = (
            f"Unable to connect to Ollama: {error}"
        )
        return fallback