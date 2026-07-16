import json
import ollama


def generate_ai_analysis(code, feedback, course, problem=""):

    prompt = f"""
You are CodeCoach AI, an experienced Computer Science Teaching Assistant.

The student is taking:

{course}

Programming problem:

{problem}

Student's code:

{code}

Rule-based feedback already found:

{feedback}

Your job is to help the student learn.

Evaluate the following:

1. Is the code correct?
2. Is it readable?
3. Are the variable names meaningful?
4. What is the time complexity?
5. What is the space complexity?
6. Are there any bugs?
7. What edge cases might fail?
8. How can the code be improved?

Explain mistakes clearly and kindly.

Do not simply praise the student.

Always provide at least one concrete improvement.

Return ONLY valid JSON.

Use EXACTLY this format:

{{
    "explanation": "...",
    "bugs": "...",
    "improved_code": "...",
    "complexity": "...",
    "learning_tips": "..."
}}
"""

    try:

        response = ollama.chat(
            model="llama3.2:3b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        text = response["message"]["content"]

        try:

            return json.loads(text)

        except json.JSONDecodeError:

            return {
                "explanation": text,
                "bugs": "The AI returned an invalid JSON response.",
                "improved_code": "",
                "complexity": "",
                "learning_tips": "Try running the analysis again."
            }

    except Exception as e:

        return {
            "explanation": "AI analysis is currently unavailable.",
            "bugs": f"Unable to connect to Ollama: {str(e)}",
            "improved_code": "",
            "complexity": "",
            "learning_tips": "Make sure Ollama is running and try again."
        }