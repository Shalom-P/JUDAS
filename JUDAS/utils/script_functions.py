import os
def exec_script(model_out:str):
    script = model_out.split("[SCRIPT]")[-1].split("[/SCRIPT]")[0]
    if "ffplay" in script or "ffmpeg" in script:
        summarise_flag = False
    else:
        summarise_flag = True
    result = os.popen(script).read()
    return result,summarise_flag

def get_summarise_prompt(query:str,script_output:str):
    prompt_template = f"""[INST]<<SYS>>
        The query {query} was given by the user and a script was written and executed that gave,\
        the output {script_output} summarise an answer based the above details and only give the answer within the tag [ANS][/ANS]\
    <</SYS>>[/INST]"""
    return prompt_template