from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import BitsAndBytesConfig
import torch
import gc
import os
class LLM:
    def __init__(
            self, 
            stop_words:list=["<|eot_id|>"],
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
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        # self.tokenizer.add_special_tokens({'cls_token':'NO_OPINION'})
        
        self.terminators = [
            self.tokenizer.eos_token_id,
            self.tokenizer.convert_tokens_to_ids("<|eot_id|>"),
            self.tokenizer.convert_tokens_to_ids("<|eom_id|>"),
            # self.tokenizer.convert_tokens_to_ids("NO_OPINION"),
        ]
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            device_map=self.device,
            quantization_config=quantization_config
        )
        # self.model.resize_token_embeddings(len(self.tokenizer))
        self.model.eval()
    def run_llm(self, prompt: str,stop_words:list,temperature:float) -> str:
        # print(self.tokenizer.convert_tokens_to_ids("[NO_OPINION]"))
        self.model.eval()
        with torch.no_grad():
            model_inputs = self.tokenizer(
                prompt, 
                return_tensors="pt"
            )
            answer = self.model.generate(
                **model_inputs.to(self.device), 
                max_new_tokens=self.max_new_tokens,
                eos_token_id=self.terminators,
                tokenizer=self.tokenizer,
                temperature=temperature,
                do_sample=True
            )
            answer_cpu = answer.cpu()
            del answer
            answer = self.tokenizer.decode(answer_cpu[0][len(model_inputs[0]):], skip_special_tokens=False)
            del model_inputs
            torch.cuda.empty_cache()
            del answer_cpu
            torch.cuda.empty_cache()
            gc.collect()
            return answer