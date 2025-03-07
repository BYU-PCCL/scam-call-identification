from google import genai

#run this file from the base of the repository
f = open("../api_keys/gemini_key.txt", "r")
key = f.read()
f.close()

client = genai.Client(api_key=key)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="What behaviors are most useful to analyze for when classifying phone call scams?",
)

output_file = "./outputs/gemini_output.txt"

f = open(output_file, "w")
f.write(response.text)
f.close()
