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
    #we have different conversation history
    print(conversation_history)
    if len(conversation_history)>max_len_conv:
        conversation_history.pop(0)
    if len(decider_conversation)>max_len_conv:
        decider_conversation.pop(0)

    try:
        # query = input("Input: ")
        prompt = get_prompt_decide(query,conv_history=decider_conversation)
        model_says_decide = hit_llm(prompt,stop_words,0.3)
        if "@NOT_CONTROL_SONGS@" in model_says_decide:
            decide_tag = "@NOT_CONTROL_SONGS@"
            decider_conversation.append(
                f"<|start_header_id|>user<|end_header_id|>{query}<|eot_id|><|start_header_id|>judas<|end_header_id|>{str(decide_tag)}<|eot_id|>"
            )
            print("it is conv")
            prompt = get_prompt_conversation(conversation_history,query)
            model_says = hit_llm(prompt,stop_words,0.6)
            # print(model_says)
            start_index = model_says.find('{')
            end_index = model_says.rfind('}')
            
            # Ensure that the braces were found
            if start_index == -1 or end_index == -1:
                raise ValueError("Input string does not contain a valid dictionary.")
            
            # Extract the string between the braces
            model_says = model_says[start_index:end_index + 1].strip()
            model_says = model_says.replace('\n',"")
            model_says = model_says.replace('\\',"")
            model_says = model_says.replace('\\\\','')
            # model_says = ast.literal_eval(model_says)
            # print(dict_command)
            conversation_history.append(
                f"<|start_header_id|>user<|end_header_id|>{query}<|eot_id|><|start_header_id|>judas<|end_header_id|>{str(model_says)}<|eot_id|>"
            )
            # del model_says
        elif "@CONTROL_SONGS@" in model_says_decide:
            decide_tag = "@CONTROL_SONGS@"
            decider_conversation.append(
                f"<|start_header_id|>user<|end_header_id|>{query}<|eot_id|><|start_header_id|>judas<|end_header_id|>{str(decide_tag)}<|eot_id|>"
            )
            print("it is songs")
            prompt = get_prompt_for_spotify(conversation_history,query)
            model_says = hit_llm(prompt,stop_words,0.9)
            print(model_says)
            start_index = model_says.find('{')
            end_index = model_says.rfind('}')
            
            # Ensure that the braces were found
            if start_index == -1 or end_index == -1:
                raise ValueError("Input string does not contain a valid dictionary.")
            
            # Extract the string between the braces
            model_says = model_says[start_index:end_index + 1].strip()
            model_says = model_says.replace('\n','')
            model_says = model_says.replace('\\','')
            model_says = model_says.replace('\\\\','')
            model_says = f"{model_says}"
            # model_says = model_says.replace(")","").replace("(","")
            model_says = process_spotify(model_says)
            # print(model_says)
            conversation_history.append(
                f"<|start_header_id|>user<|end_header_id|>{query}<|eot_id|><|start_header_id|>judas<|end_header_id|>{model_says}<|eot_id|>"
            )
           
        else:
            print(model_says_decide,"not proper categorisation")
            decide_tag = "@NOTPRESENT@"
            model_says = "model be tripping bruh".upper()
            
        return model_says,[f"user: {query}\njudas: {model_says}"]
    except KeyboardInterrupt:
        # break
        pass
if __name__=='__main__':
    SPOTIFY_GREEN = "#1DB954"
    WHITE = "#FFFFFF"
    BLACK = "#191414"
    LIGHT_GREY = "#B3B3B3"
    DARK_GREY = "#282828"
    LIGHTER_SPOTIFY_GREEN = "#3DDC84"

    max_len_conv = 4
    stop_words = ["[/OPINION]","[NO_OPINION]","[/ANSWER]","@NOT_CONTROL_SONGS@","@CONTROL_SONGS@","@SCRIPT@","[/SCRIPT]","[/ANS]","@end"]
    decider_conversation = []
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
        text_widget.config(state=tk.NORMAL)
        text_widget.insert("-1.0", f"USER: {user_input} \n",'left-align')
        entry.delete(0, tk.END)
        # Update the UI to reflect the first insert immediately
        text_widget.update_idletasks()
        proceesed_output,history = run(query=user_input)
        # key = [key for key in proceesed_output.keys()][0]
        # if key == "NO_OPINION":
        #     updated_text = key
        # Append some text to the input string
        updated_text = str(proceesed_output)
        # Update the label with the updated text
        # display_label.config(text=updated_text)
        
        text_widget.insert("-2.0", f"JUDAS: {updated_text}\n",'right-align')
        text_widget.config(state=tk.DISABLED)
        

    # Create the main window
    root = tk.Tk()
    root.title("JUDAS")

    # Create a container (frame) for the widgets
    frame = tk.Frame(root,bg=BLACK)
    frame.pack(padx=0, pady=0,fill=tk.X, expand=True)

    # Create an Entry widget for user input
    entry = tk.Entry(frame)
    entry.pack(pady=0,padx=0,fill=tk.X, expand=True)

    # Bind the Enter key to the process_input function
    root.bind('<Return>', process_input)

    # Create a Button widget to trigger the display action
    submit_button = tk.Button(frame, text="ENTER", command=process_input,background=SPOTIFY_GREEN)
    submit_button.pack(pady=0,padx=0)

    # Create a Label widget to display the user input
    # display_label = tk.Label(frame, text="",fg=WHITE,bg=DARK_GREY,font=("Arial", 14),width=50)
    # display_label.pack(pady=5)

    # Create a text widget to display the list
    text_widget = tk.Text(root,font=("Circular", 14),background=BLACK)
    text_widget.pack(fill=tk.BOTH, expand=True,pady=0,padx=0)
    # Styles for text alignment
    text_widget.tag_configure('left-align', justify='left',background=BLACK,wrap="word",foreground=WHITE)
    text_widget.tag_configure('right-align', justify='right',background=SPOTIFY_GREEN,wrap="word",foreground=BLACK)

    # Start the main event loop
    root.mainloop()
    # process_spotify("ji")
    # play_some_song("hi")
    # get_recommendations(5,['hip-hop'])