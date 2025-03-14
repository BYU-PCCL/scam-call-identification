from google import genai
from file_utils import get_gemini_api_key

#run this file from the base of the repository
key = get_gemini_api_key()

client = genai.Client(api_key=key)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="what fruits are most similar to pineapples",
)

output_file = "./outputs/gemini_test_output.txt"

f = open(output_file, "w")
f.write(response.text)
f.close()
