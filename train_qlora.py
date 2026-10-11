import os
import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
DATASET_PATH = "CareerCompassDataset.csv"
OUTPUT_DIR = "/content/drive/MyDrive/CareerCompass/qwen-career-compass-final"
MAX_LENGTH = 1024
EPOCHS = 3
LEARNING_RATE = 2e-4

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(
        f"Missing {DATASET_PATH}. Upload your original 1785-row CareerCompassDataset.csv "
        "to the Colab session, or set DATASET_PATH to its full path."
    )

df = pd.read_csv(DATASET_PATH)
required = {"instruction", "response"}
if not required.issubset(df.columns):
    raise ValueError(f"CSV must contain columns: {sorted(required)}. Found: {list(df.columns)}")

df = df[["instruction", "response"]].dropna()
df["instruction"] = df["instruction"].astype(str).str.strip()
df["response"] = df["response"].astype(str).str.strip()
df = df[(df["instruction"] != "") & (df["response"] != "")]
if len(df) < 2:
    raise ValueError("At least two valid instruction/response rows are required.")

dataset = Dataset.from_pandas(df, preserve_index=False)
splits = dataset.train_test_split(test_size=0.1, seed=42)
train_dataset = splits["train"]
eval_dataset = splits["test"]

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

def format_example(example):
    messages = [
        {"role": "system", "content": "You are Career Compass, a helpful career guidance assistant. Give accurate, practical advice about resumes, skills, career paths, learning roadmaps, and job search."},
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["response"]},
    ]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=False
    )
    return {"text": text}

train_dataset = train_dataset.map(format_example)
eval_dataset = eval_dataset.map(format_example)

def tokenize_batch(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        max_length=MAX_LENGTH,
        padding=False,
    )

train_dataset = train_dataset.map(tokenize_batch, batched=True, remove_columns=train_dataset.column_names)
eval_dataset = eval_dataset.map(tokenize_batch, batched=True, remove_columns=eval_dataset.column_names)

os.makedirs(OUTPUT_DIR, exist_ok=True)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16,
)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.float16,
)
model.config.use_cache = False
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=LEARNING_RATE,
    fp16=True,
    logging_steps=25,
    eval_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=2,
    load_best_model_at_end=False,
    report_to="none",
    optim="paged_adamw_8bit",
    gradient_checkpointing=True,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
)

collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=collator,
)

trainer.train()
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Adapter and tokenizer saved to: {OUTPUT_DIR}")
