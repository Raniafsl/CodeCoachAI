import ollama

response = ollama.chat(
    model="llama3.2:latest",
    messages=[
        {
            "role": "user",
            "content": "Explain recursion in one sentence."
        }
    ]
)

print(response["message"]["content"])