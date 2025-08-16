import os
import re
import sys
import time
import numpy as np
import pandas as pd
from google import genai
from google.genai import types
from src.ml_scam_classification.utils.file_utils import get_gemini_api_key, ensure_file_versioning_ok
from src.ml_scam_classification.utils.llm_utils import get_json_from_llm_response

def run_gemini_behavioral_analysis(
    prompt_filepath=None, 
    response_writepath=None # Set defaults to None so paths must be specified to avoid need for default paths and keeping that updated
    ):

    if not (None == None):
        print("We have a problem...")
    if prompt_filepath == None or response_writepath == None:
        raise ValueError("ERROR - Attmepted to run Gemini behavioral analysis without providing path to prompt and/or for writing out response")

    # Set up Google Gemini
    key = get_gemini_api_key() # Gets api key from .env file
    client = genai.Client(api_key=key)  # Configure the global API key
    client = genai.Client()

    with open(prompt_filepath, "r") as file:
        system_prompt = file.read()

    conversations = pd.read_csv('src/ml_scam_classification/data/call_data_by_conversation/processed/call_data_by_conversation.csv')
    conversations_small = conversations[:2]

    for index, row in conversations_small.iterrows():
        complete_prompt = system_prompt + "\n\ncall transcript:\n\n" + row['TEXT']
        print("complete prompt:")
        print(complete_prompt)

        response = client.models.generate_content(
            model="gemini-2.5-pro", contents=complete_prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=32768)
            )
        )
        print(response)

        json = get_json_from_llm_response(response.text)

        output_file = response_writepath

        with open(output_file, "a") as file:
            # file.write('\n\n' + row['TEXT'] + "\n\n")
            file.write(json)
        
        print("(!!!) - WARNING - Rate limits not configured... waiting 1 min to be safe.")
        print("Configure rate limits before removing this warning and the exit() statement!")
        import time
        time.sleep(61)
        exit()
