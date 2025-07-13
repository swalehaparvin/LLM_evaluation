# main.py (only change these 3 lines)
from transformers import pipeline
chatbot = pipeline("text-generation",
                   model="./cyber-ft",
                   tokenizer="./cyber-ft",
                   max_new_tokens=120,
                   temperature=0.3)
# Existing Gradio UI remains the same