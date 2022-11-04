import gradio as gr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
import time
from datetime import datetime

#this model was loaded from https://hf.co/models
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
device = 0 if torch.cuda.is_available() else -1
LANGS = ["eng_Latn", "fra_Latn", "deu_Latn", "spa_Latn", "jpn_Jpan", "zho_Hans"]

def translate(text, src_lang, tgt_lang, carbon_rate):
    
    start_time = time.time()

    translation_pipeline = pipeline("translation", model=model, tokenizer=tokenizer, src_lang=src_lang, tgt_lang=tgt_lang, max_length=400, device=device)
    result = translation_pipeline(text)
    # The measured CPU utilziation rate when running the nllb model is around 50%
    cpu_util = 50
    exe_time = time.time() - start_time
    # We use a trained machine learning model to estimate the power consumption
    power_est = round(1.37 * cpu_util + 41.32, 3)
    #energy in kwh
    energy_est = power_est * exe_time/1000/3600
    carbon_est = energy_est * carbon_rate

    return {"translation": result[0]['translation_text'], "energy": str(energy_est), "carbon": str(carbon_est)}

demo = gr.Interface(
    fn=translate,
    inputs=[
        gr.components.Textbox(label="Text"),
        gr.components.Dropdown(label="Source Language", choices=LANGS),
        gr.components.Dropdown(label="Target Language", choices=LANGS),
        gr.Number(label = 'Carbon Rate')
        ],
    outputs=[gr.JSON()],
    examples=[["Your translation request will be sent to the nearest server when Eco mode is off and the lowest carbon server when the Eco Mode is on.", "eng_Latn", "spa_Latn"]],
    cache_examples=False,
    title="IntellEco Translation",
    description="Language translation is one of the most poplular AI applications. This demo shows how carbon-aware translation can be implemented (credits to the authors of the original NLLB-Translator Model)"
)

demo.launch(debug=True, share=True)

