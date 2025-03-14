from google import genai
import pandas as pd
from file_utils import get_gemini_api_key

client = genai.Client(api_key=get_gemini_api_key())

with open("./data/gemini_prompt_edit.txt", "r") as file:
    system_prompt = file.read()


conversations = pd.read_csv('./data/call_data_by_conversation.csv')
conversations_small = conversations[:5]

for index, row in conversations_small.iterrows():

    complete_prompt = system_prompt + "\n\ncall transcript:\n\n" + row['TEXT']

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=complete_prompt,
    )

    output_file = "./outputs/feature_extraction_text_out.txt"

    with open(output_file, "a") as file:
        file.write('\n\n' + row['TEXT'] + "\n\n")
        file.write(response.text)