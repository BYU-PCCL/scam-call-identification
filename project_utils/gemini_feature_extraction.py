from google import genai

with open("../api_keys/gemini_key.txt", "r") as file:
    key = file.read()

client = genai.Client(api_key=key)

with open("./data/gemini_prompt_edit.txt", "r") as file:
    system_prompt = file.read()

with open("./data/call_data_chunked.txt", "r") as file:
    conversation = file.read()

complete_prompt = system_prompt + "\n\ncall transcript:\n\n" + conversation

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=complete_prompt,
)

output_file = "./outputs/feature_extraction_text_out.txt"


with open(output_file, "w") as file:
    file.write(complete_prompt + "\n\n\n")
    file.write(response.text)