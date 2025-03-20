import sys
import os
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI
from file_utils import get_chatgpt_api_key
from cout_log_utils import cout_log, cout_log_action, cout_log_title, cout_log_w_char_limit, cout_log_info


def send_prompt_to_chatgpt(
    prompt, 
    model="gpt-4o-2024-11-20", 
    system_instructions="You are a call analysis system creating useful features to input to a scam detection model.",
    progress_message="Sending prompt to ChatGPT (may take up to 60s)",
    ):
    openai_api_key = None
    
    cout_log_info(1)
    
    # Get ChatGPT API Key
    load_dotenv()  # Correctly load environment variables
    openai_api_key = get_chatgpt_api_key()  # Gets the API key from the .env file
    client = OpenAI(api_key=openai_api_key)

    cout_log_info(2)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    # Combine the streaming response chunks into a single response string
    full_response = ""
    for chunk in response:
        # For chat completions, each chunk's content is in chunk.choices[0].delta.content
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content

    return full_response

    # TODO - multiple high-temperature responses, then come to a consensus (majority, weighted vote, or similar)
    # TODO - research models of emotionspace, intentionspace, etc. Or maybe just have a dataset with labeled emotions, intent, sentiment, and fine tume on it


    """
    If annotated ground truth is available, evaluate the model’s performance using metrics such as accuracy and macro F1 scores. The study used these metrics to compare ChatGPT’s zero-shot and few-shot performance with fine-tuned baselines.
    """





# Commenting out for now as have new main function for testing
"""
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py 'Your prompt here' [model]")
        sys.exit(1)
    
    # first arg is prompt
    prompt = sys.argv[1]
    
    # second arg is model selection - by default - gpt-3.5-turbo
    model = sys.argv[2] if len(sys.argv) >= 3 else "gpt-4o-2024-11-20"
    response = send_prompt_to_chatgpt(prompt, model)
    print(response)
"""


def start_conversation(progress_message, prompt, system_instructions=None, model="gpt-4o-2024-11-20", **extra_params):
    """
    Starts a conversation using the Chat Completions API.
    
    Parameters:
      - prompt (str): The initial user prompt.
      - system_instructions (str, optional): Optional system message to guide the assistant.
      - extra_params: Other optional parameters (like temperature, max_tokens, etc.).
    
    Returns:
      - conversation (list): A list of messages representing the conversation history,
        including the assistant’s response.

    Providing Extra Parameters:
      - just provide them normally like you add the ones that are specified and the function will automatically add them
    """

    cout_log_info(1)

    load_dotenv()  # Correctly load environment variables
    API_KEY = get_chatgpt_api_key()  # Gets the API key from the .env file

    cout_log_info(2)

    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json" # specifies that we are sending json in our request, so it knows how to handle it
    }

    # Initialize conversation as a list of messages.
    conversation = []
    
    # Optionally prepend system message (i.e. giving the chatbot a role) if provided
    if system_instructions:
        conversation.append({"role": "system", "content": system_instructions})
    
    # Append the initial user prompt.
    conversation.append({"role": "user", "content": prompt})
    
    # Prepare request payload.
    payload = {
        "model": model,
        "messages": conversation
    }
    # Merge in any extra parameters (such as temperature, max_tokens, etc.)
    payload.update(extra_params)
    
    # Call the Chat Completions API.
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=HEADERS, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.text}")
    
    result = response.json()
    
    # The assistant's response is usually in the first (and only) choice.
    assistant_message = result["choices"][0]["message"]
    
    # Append the assistant response to the conversation.
    conversation.append(assistant_message)
    
    return conversation

def continue_conversation(progress_message, conversation, prompt, model="gpt-4o-2024-11-20", **extra_params):
    """
    Continues an existing conversation by appending a new user prompt and obtaining
    the assistant's next response.
    
    Parameters:
      - conversation (list): The existing conversation history.
      - prompt (str): The new user prompt to add.
      - extra_params: Other optional parameters for the API call.
    
    Returns:
      - conversation (list): The updated conversation history with the new assistant response appended.

    Providing Extra Parameters:
      - just provide them normally like you add the ones that are specified and the function will automatically add them
    """

    cout_log_info(1)

    load_dotenv()  # Correctly load environment variables
    API_KEY = get_chatgpt_api_key()  # Gets the API key from the .env file

    cout_log_info(2)

    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json" # specifies that we are sending json in our request, so it knows how to handle it
    }

    # Append the new user prompt.
    conversation.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": conversation
    }
    payload.update(extra_params)
    
    max_retries = 5
    for attempt in range(max_retries):
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=HEADERS, json=payload)
        if response.status_code == 200:
            break
        else:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt+1}/{max_retries} failed with status code {response.status_code}. Retrying...")
                time.sleep(1)  # Optionally wait 1 second between attempts
            else:
                raise Exception(f"API request failed after {max_retries} attempts: {response.text}")
    
    result = response.json()
    response_message = result["choices"][0]["message"]
    
    # Append the new response.
    conversation.append(response_message)
    
    return conversation

# Example usage:
if __name__ == "__main__":
    # Start a new conversation.
    conv = start_conversation("Hello, who are you?", system_instructions="You are a helpful assistant.")
    print("Conversation after starting:")
    print(json.dumps(conv, indent=2))
    
    # Continue the conversation.
    conv = continue_conversation(conv, "Can you tell me a fun fact about AI?")
    print("\nConversation after continuing:")
    print(json.dumps(conv, indent=2))
