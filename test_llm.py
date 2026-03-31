import os
from adapters.llm_adapter import analyze_text
prompt = "Hello, what is 2+2?"
print("Querying Gemini...")
ans1 = analyze_text(prompt, model="gemini/gemini-2.5-flash")
print("Gemini result:", ans1)

print("Querying Groq directly...")
ans2 = analyze_text(prompt, model="groq/llama-3.1-8b-instant")
print("Groq result:", ans2)
