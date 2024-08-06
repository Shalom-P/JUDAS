# from llm_clas import LLM
from utils.spotify_functions import *
from utils.script_functions import *
import requests
from utils.prompt_templates import *
import gc
import tkinter as tk
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

#############################################################################################
def run(query):
    # while True:
    if len(decider_conversation)>max_len_conv:
        decider_conversation.pop(0)
    if len(conversation_conversation)>max_len_conv:
        conversation_conversation.pop(0)
    if len(spotify_conversation)>max_len_conv:
        spotify_conversation.pop(0)
    if len(script_conversation)>max_len_conv:
        script_conversation.pop(0)
    try:
        # query = input("Input: ")
        prompt = get_prompt_decide(query,conv_history=decider_conversation)
        model_says_decide = hit_llm(prompt,stop_words,0.1)
        model_says_decide = model_says_decide.split("JUDAS:")[-1]
        if "@CONV@" in model_says_decide:
            decide_tag = "@CONV@"
            print("it is conv")
            prompt = get_prompt_conversation(conversation_conversation,query)
            model_says = hit_llm(prompt,stop_words,0.6)
            model_says = model_says.split("[/INST]")[-1].split("[JUDAS]:")[-1]
            # print(model_says)
            conversation_conversation.append(
                {
                    "USER":query,
                    "JUDAS":model_says
                }
            )
            # del model_says
        elif "@SONGS@" in model_says_decide:
            decide_tag = "@SONGS@"
            print("it is songs")
            prompt = get_prompt_for_spotify(spotify_conversation,query)
            model_says = hit_llm(prompt,stop_words,0.2)
            model_says = model_says.split("[/INST]")[-1].split("[JUDAS]:")[-1]
            process_spotify(model_says)
            spotify_conversation.append(
                {
                    "USER": query,
                    "JUDAS": model_says
                }
            )
            # del model_says
        elif "@SCRIPT@" in model_says_decide:
            decide_tag = "@SCRIPT@"
            print("it is a script")
            prompt = get_prompt_script(query)
            model_says = hit_llm(prompt,stop_words,0.1)
            model_says = model_says.split("[/INST]")[-1].split("JUDAS:")[-1]
            script_output,summarise_flag = exec_script(model_says)
            # print(model_says)
            
            if summarise_flag:
                prompt = get_summarise_prompt(query,script_output)
                model_says = hit_llm(prompt,stop_words,0.2)
                model_says = model_says.split("[ANS]")[-1].split("[/ANS]")[0]
                
                # del model_says
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
        return decide_tag+"\n"+model_says
    except KeyboardInterrupt:
        # break
        pass
if __name__=='__main__':
    max_len_conv = 4
    stop_words = ["[/OPINION]","[NO_OPINION]","[/ANSWER]","@CONV@","@SONGS@","@SCRIPT@","[/SCRIPT]","[/ANS]","@end"]
    decider_conversation = []
    spotify_conversation = []
    script_conversation = []
    conversation_conversation = []
    def process_input(event=None):
    # Retrieve the input from the entry widget
        user_input = entry.get()
        proceesed_output = run(query=user_input)
        # Append some text to the input string
        updated_text = proceesed_output
        # Update the label with the updated text
        display_label.config(text=updated_text)
        # Optionally clear the entry widget
        entry.delete(0, tk.END)

    # Create the main window
    root = tk.Tk()
    root.title("JUDAS")

    # Create a container (frame) for the widgets
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    # Create an Entry widget for user input
    entry = tk.Entry(frame, width=300)
    entry.pack(pady=5)

    # Bind the Enter key to the process_input function
    root.bind('<Return>', process_input)

    # Create a Button widget to trigger the display action
    submit_button = tk.Button(frame, text="ENTER", command=process_input)
    submit_button.pack(pady=5)

    # Create a Label widget to display the user input
    display_label = tk.Label(frame, text="")
    display_label.pack(pady=5)

    # Start the main event loop
    root.mainloop()
    # process_spotify("ji")
    # play_some_song("hi")
    # get_recommendations(5,['hip-hop'])