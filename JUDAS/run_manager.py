# from llm_clas import LLM
from utils.spotify_functions import *
from utils.script_functions import *
import requests
from utils.prompt_templates import *
import gc
#############################################################################################
def hit_llm(query:str,stop_words:list,temperature:float)->str:
    # URL of the Flask server
    url = 'http://127.1.1.1:6969/process_text'

    # Data to be sent in the POST request
    data = {
        'prompt': query,
        'stop_words':stop_words,
        'temperature':temperature
    }
    # Sending POST request
    response = requests.post(url, json=data)
    # Printing the response
    if response.status_code == 200:
        return response.json()['output_text']
    else:
        return str(response.status_code)
#############################################################################################
def run():
    while True:
        if len(decider_conversation)>max_len_conv:
            decider_conversation.pop(0)
        if len(conversation_conversation)>max_len_conv:
            conversation_conversation.pop(0)
        if len(spotify_conversation)>max_len_conv:
            spotify_conversation.pop(0)
        if len(script_conversation)>max_len_conv:
            script_conversation.pop(0)
        try:
            query = input("Input: ")
            prompt = get_prompt_decide(query,conv_history=decider_conversation)
            model_says_decide = hit_llm(prompt,stop_words,0.1)
            model_says_decide = model_says_decide.split("JUDAS:")[-1]
            if "@CONV@" in model_says_decide:
                decide_tag = "@CONV@"
                print("it is conv")
                prompt = get_prompt_conversation(conversation_conversation,query)
                model_says_conv = hit_llm(prompt,stop_words,0.6)
                model_says_conv = model_says_conv.split("[/INST]")[-1].split("[JUDAS]:")[-1]
                print(model_says_conv)
                conversation_conversation.append(
                    {
                        "USER":query,
                        "JUDAS":model_says_conv
                    }
                )
                del model_says_conv
            elif "@SONGS@" in model_says_decide:
                decide_tag = "@SONGS@"
                print("it is songs")
                prompt = get_prompt_for_spotify(spotify_conversation,query)
                model_says_spotify = hit_llm(prompt,stop_words,0.2)
                model_says_spotify = model_says_spotify.split("[/INST]")[-1].split("[JUDAS]:")[-1]
                process_spotify(model_says_spotify)
                spotify_conversation.append(
                    {
                        "USER":query,
                        "JUDAS":model_says_spotify
                    }
                )
                del model_says_spotify
            elif "@SCRIPT@" in model_says_decide:
                decide_tag = "@SCRIPT@"
                print("it is a script")
                prompt = get_prompt_script(query)
                model_says_script = hit_llm(prompt,stop_words,0.1)
                model_says_script = model_says_script.split("[/INST]")[-1].split("JUDAS:")[-1]
                script_output,summarise_flag = exec_script(model_says_script)
                print(model_says_script)
                if summarise_flag:
                    prompt = get_summarise_prompt(query,script_output)
                    model_says = hit_llm(prompt,stop_words,0.2)
                    model_says = model_says.split("[ANS]")[-1].split("[/ANS]")[0]
                    print(model_says)
                    del model_says
            else:
                print(model_says_decide)
                print("model be tripping bruh".upper())
            decider_conversation.append(
                {
                    "USER":{query},
                    "JUDAS":{decide_tag}
                }
            )
            del model_says_decide
            del query
            del prompt
            gc.collect()
        except KeyboardInterrupt:
            break
if __name__=='__main__':
    max_len_conv = 4
    stop_words = ["[/OPINION]","[NO_OPINION]","[/ANSWER]","@CONV@","@SONGS@","@SCRIPT@","[/SCRIPT]","[/ANS]","@end"]
    decider_conversation = []
    spotify_conversation = []
    script_conversation = []
    conversation_conversation = []
    run()
    # process_spotify("ji")
    # play_some_song("hi")
    # get_recommendations(5,['hip-hop'])