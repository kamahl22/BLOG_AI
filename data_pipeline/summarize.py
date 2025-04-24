import openai
import os

def summarize_data(merged_data):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Create a simple summary prompt for GPT
    prompt = f"Summarize this sports betting data for a Discord user: {merged_data}"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']