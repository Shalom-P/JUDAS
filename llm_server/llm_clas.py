from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import BitsAndBytesConfig
import torch
import gc
import os
class LLM:
    def __init__(
            self, 
            modname:str="mistralai/Mistral-7B-Instruct-v0.3",
            device:str="cuda:0",
            max_new_tokens: int = 512,
        ):
        self.max_new_tokens = max_new_tokens
        model_name = modname
        self.device = device
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            device_map=self.device,
            quantization_config=quantization_config
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        self.model.eval()
    def run_llm(self, prompt: str,stop_words:list,temperature:float) -> str:
        self.model.eval()
        with torch.no_grad():
            model_inputs = self.tokenizer(
                prompt, 
                return_tensors="pt"
            )
            answer = self.model.generate(
                **model_inputs.to(self.device), 
                max_new_tokens=self.max_new_tokens,
                stop_strings=stop_words,#["[/OPINION]","[NO_OPINION]","[/ANSWER]","[/GETREC]"],
                tokenizer=self.tokenizer,
                temperature=temperature,
                do_sample=True
            )
            answer_cpu = answer.cpu()
            del answer
            del model_inputs
            torch.cuda.empty_cache()
            answer = self.tokenizer.decode(answer_cpu[0], skip_special_tokens=False)
            # answer = answer.split("[/INST]")[1].split("[JUDAS]:")[-1].strip()
            del answer_cpu
            torch.cuda.empty_cache()
            gc.collect()
            return answer
        # return "bruh"
