from google import genai
from src.ml_scam_detector.utils.file_utils import get_gemini_api_key
from dotenv import load_dotenv

def get_gemini_api_key():
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")


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
