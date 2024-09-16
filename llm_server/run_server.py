from flask import Flask, request, jsonify
from llm_clas import LLM
import gc

app = Flask(__name__)
stop_words = ["[/OPINION]","[NO_OPINION]","[/ANSWER]","@NOT_CONTROL_SONGS@","@CONTROL_SONGS@","@SCRIPT@","[/SCRIPT]","[/ANS]","@end"]
llm = LLM(stop_words=stop_words,modname="meta-llama/Meta-Llama-3.1-8B-Instruct")

@app.route('/process_text', methods=['POST'])
def process_text():
    # Get the input text from the request
    data = request.get_json()
    prompt = data.get('prompt')
    stop_words = data.get('stop_words')
    temperature = data.get('temperature')
    if not prompt:
        return jsonify({"error": "No text provided"}), 400

    # Process the input text 
    model_out = llm.run_llm(prompt,stop_words,temperature)
    # Return the processed text as a JSON response
    del data
    del prompt
    del stop_words
    del temperature
    gc.collect()
    return jsonify({"output_text": model_out})


# if __name__ == '__main__':
