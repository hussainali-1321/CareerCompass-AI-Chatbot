
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

base_model = "Qwen/Qwen2.5-3B-Instruct"
adapter_path = r"C:\CareerCompass"

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(base_model)

print("Loading base model...")
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True
)

print("Loading Career Compass adapter...")
model = PeftModel.from_pretrained(model, adapter_path)
model.eval()

print("Career Compass is ready. Type 'exit' to close.")

while True:
    question = input("\nYou: ").strip()

    if question.lower() == "exit":
        break

    messages = [
        {
            "role": "system",
            "content": "You are Career Compass, an AI career guidance assistant."
        },
        {
            "role": "user",
            "content": question
        }
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=False
        )

    answer = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True
    )

    print("\nCareer Compass:", answer)
