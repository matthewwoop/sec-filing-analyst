import ollama

response = ollama.chat(
    model="gemma3",
    messages=[{"role": "user", "content": "Reply with the single word: ready"}],
)

print(response.message.content)