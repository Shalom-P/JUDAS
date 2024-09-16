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
    print(conversation_history)
    if len(conversation_history)>max_len_conv:
        conversation_history.pop(0)
    try:
        # query = input("Input: ")
        prompt = get_prompt_decide(query,conv_history=conversation_history)
        model_says_decide = hit_llm(prompt,stop_words,0.3)
        if "@NOT_CONTROL_SONGS@" in model_says_decide:
            decide_tag = "@NOT_CONTROL_SONGS@"
            print("it is conv")
            prompt = get_prompt_conversation(conversation_history,query)
            model_says = hit_llm(prompt,stop_words,0.6)
            start_index = model_says.find('{')
            end_index = model_says.rfind('}')
            
            # Ensure that the braces were found
            if start_index == -1 or end_index == -1:
                raise ValueError("Input string does not contain a valid dictionary.")
            
            # Extract the string between the braces
            model_says = model_says[start_index:end_index + 1].strip()
            model_says = model_says.replace('\n',"")
            model_says = model_says.replace('\\',"")
            # dict_command = ast.literal_eval(model_says)
            # print(dict_command)
            conversation_history.append(
                f"<|start_header_id|>user<|end_header_id|>{query}<|eot_id|><|start_header_id|>judas<|end_header_id|>{str(model_says)}<|eot_id|>"
            )
            # del model_says
        elif "@CONTROL_SONGS@" in model_says_decide:
            decide_tag = "@CONTROL_SONGS@"
            print("it is songs")
            prompt = get_prompt_for_spotify(conversation_history,query)
            model_says = hit_llm(prompt,stop_words,0.2)
            start_index = model_says.find('{')
            end_index = model_says.rfind('}')
            
            # Ensure that the braces were found
            if start_index == -1 or end_index == -1:
                raise ValueError("Input string does not contain a valid dictionary.")
            
            # Extract the string between the braces
            model_says = model_says[start_index:end_index + 1].strip()
            model_says = model_says.replace('\n',"")
            model_says = model_says.replace('\\',"")
            print(model_says)
            # model_says = model_says.replace(")","").replace("(","")
            process_spotify(model_says)
            # print(model_says)
            conversation_history.append(
                f"<|start_header_id|>user<|end_header_id|>{query}<|eot_id|>\
                    <|start_header_id|>judas<|end_header_id|>{model_says}<|eot_id|>"
            )
            # del model_says
        # elif "@SCRIPT@" in model_says_decide:
        #     decide_tag = "@SCRIPT@"
        #     print("it is a script")
        #     prompt = get_prompt_script(query)
        #     model_says = hit_llm(prompt,stop_words,0.1)
        #     model_says = model_says.split("[/INST]")[-1].split("JUDAS:")[-1]
        #     script_output,summarise_flag = exec_script(model_says)
        #     # print(model_says)
            
        #     if summarise_flag:
        #         prompt = get_summarise_prompt(query,script_output)
        #         model_says = hit_llm(prompt,stop_words,0.2)
        #         model_says = model_says.split("[ANS]")[-1].split("[/ANS]")[0]
                
                # del model_says
        else:
            print(model_says_decide,"not proper categorisation")
            decide_tag = "@NOTPRESENT@"
            model_says = "model be tripping bruh".upper()
            
        return decide_tag+"\n"+model_says,[f"user: {query}\njudas: {model_says}"]
    except KeyboardInterrupt:
        # break
        pass
if __name__=='__main__':
    max_len_conv = 4
    stop_words = ["[/OPINION]","[NO_OPINION]","[/ANSWER]","@NOT_CONTROL_SONGS@","@CONTROL_SONGS@","@SCRIPT@","[/SCRIPT]","[/ANS]","@end"]
    # decider_conversation = []
    # spotify_conversation = []
    # script_conversation = []
    # conversation_conversation = []
    conversation_history = []

    def append_item(new_item):
        text_widget.insert(tk.END, new_item + '\n')

    def print_history(history_list):
        for item in history_list:
            text_widget.insert(tk.END, item + '\n')

    # Function to append a new item to the list
        


    def process_input(event=None):
    # Retrieve the input from the entry widget
        user_input = entry.get()
        proceesed_output,history = run(query=user_input)
        # Append some text to the input string
        updated_text = proceesed_output
        # Update the label with the updated text
        display_label.config(text=updated_text)
        print_history(history)
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

    # Create a text widget to display the list
    text_widget = tk.Text(root)
    text_widget.pack(fill=tk.BOTH, expand=True)


    # Start the main event loop
    root.mainloop()
    # process_spotify("ji")
    # play_some_song("hi")
    # get_recommendations(5,['hip-hop'])