## TEST
import sys
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
OpenAI.api_key = openai_api_key

client = OpenAI()

stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say this is a test"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")



# TODO - multiple high-temperature responses, then come to a consensus (majority, weighted vote, or similar)
# TODO - research models of emotionspace, intentionspace, etc. Or maybe just have a dataset with labeled emotions, intent, sentiment, and fine tume on it


"""
If annotated ground truth is available, evaluate the model’s performance using metrics such as accuracy and macro F1 scores. The study used these metrics to compare ChatGPT’s zero-shot and few-shot performance with fine-tuned baselines.
"""