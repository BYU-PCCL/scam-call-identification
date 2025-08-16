from src.ml_scam_classification.utils.json_utils import is_json

def get_json_from_llm_response(response_text):
    # Validate that the response contains the expected JSON formatting.
    # (In our design, we assume the assistant returns JSON wrapped between ```json\n and \n```.)
    
    if "```json" not in response_text:
            raise ValueError("Critical Error: Could not locate ```json in the response, meaning the response likely contains no valid json. Terminating.")
    # Extract the JSON portion.
    try:
        json_and_rest = response_text.split("```json\n")[1]
        json_only = json_and_rest.split("\n```")[0]
    except IndexError:
        if len(response_text) < 100 and ('done' in response_text or 'Done' in response_text):
            print("WARNING - LLM indicated it was done after only one line. This is fine so long as the current transcript is only one line, but please double check.")

            cont = input("Continue (y/n)?")

            if cont != "Y" and cont != "Y":
                return
            
            print("LLM indicated it was done processing the transcript. Moving to the next transcript.")
            return
        raise ValueError("Critical Error: JSON delimiters not found as expected in the response.")
    if not is_json(json_only):
            raise ValueError("Critical Error: JSON not parsed correctly from LLM response. Terminating.")
    return json_only