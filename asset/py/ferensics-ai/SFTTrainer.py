import torch
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import Dataset

# 1. Model & Quantization Configuration
MAX_SEQ_LENGTH = 2048  # Context window for tool schemas and forensic prompts
MODEL_NAME = "unsloth/Qwen2.5-7B-Instruct-bnb-4bit"  # Pre-quantized 4-bit base SLM

print("[1/5] Loading 4-bit base model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,             # Automatic GPU detection (Float16 or Bfloat16)
    load_in_4bit=True,      # QLoRA 4-bit base weight loading
)

# 2. Attach PEFT (LoRA) Adapters
print("[2/5] Configuring QLoRA Adapters...")
model = FastLanguageModel.get_peft_model(
    model,
    r=16,                   # Rank matrix dimension
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ],
    lora_alpha=16,
    lora_dropout=0,         # Optimized at 0 in Unsloth for speed/VRAM
    bias="none",
    use_gradient_checkpointing="unsloth",  # Memory preservation
    random_state=3407,
)

# 3. Create Forensic Tool-Calling Dataset
# Uses Qwen 2.5 / OpenAI Tool-Calling Chat Markup Structure
sample_forensic_dataset = [
    {
        "messages": [
            {
                "role": "system",
                "content": "You are a specialized Forensic Science Assistant. Always offload numerical, ballistic, and thermodynamic calculations to tool calls."
            },
            {
                "role": "user",
                "content": "A 0.308 round (168 grains, drag coeff 0.22, area 0.074 sq in) was fired at 2600 fps at a 2-degree elevation. Calculate its trajectory."
            },
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "calculate_ballistic_trajectory",
                            "arguments": {
                                "velocity_fps": 2600.0,
                                "angle_degrees": 2.0,
                                "bullet_mass_grains": 168.0,
                                "drag_coefficient": 0.22,
                                "cross_sectional_area_sq_in": 0.074
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "calculate_ballistic_trajectory",
                "content": '{"total_distance_feet": 3240.5, "max_elevation_feet": 42.1, "flight_time_seconds": 1.82, "impact_velocity_fps": 1412.3}'
            },
            {
                "role": "assistant",
                "content": "Based on the numerical trajectory simulation:\n- **Total Range:** 3,240.5 feet (~1,080 yards)\n- **Max Apex:** 42.1 feet\n- **Flight Time:** 1.82 seconds\n- **Impact Velocity:** 1,412.3 fps"
            }
        ]
    },
    {
        "messages": [
            {
                "role": "system",
                "content": "You are a specialized Forensic Science Assistant. Always offload numerical, ballistic, and thermodynamic calculations to tool calls."
            },
            {
                "role": "user",
                "content": "Determine the flashover heat release rate required for a room measuring 5m by 4m with a 1m wide by 2m high vent."
            },
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "calculate_compartment_flashover",
                            "arguments": {
                                "room_length_m": 5.0,
                                "room_width_m": 4.0,
                                "vent_width_m": 1.0,
                                "vent_height_m": 2.0
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "calculate_compartment_flashover",
                "content": '{"critical_hrr_kw": 9768.21, "critical_hrr_mw": 9.77, "minimum_temp_celsius": 500}'
            },
            {
                "role": "assistant",
                "content": "According to Thomas' Flashover Correlation for this compartment geometry, the minimum critical Heat Release Rate (HRR) required to trigger flashover is **9.77 MW** (9,768 kW)."
            }
        ]
    }
]

# 4. Format Dataset using Tokenizer Chat Template
def format_chat_template(examples):
    texts = []
    for messages in examples["messages"]:
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False
        )
        texts.append(text)
    return {"text": texts}

print("[3/5] Formatting dataset using chat template...")
raw_dataset = Dataset.from_list(sample_forensic_dataset)
formatted_dataset = raw_dataset.map(format_chat_template, batched=True)

# 5. Execute Training Loop
print("[4/5] Initializing SFT Trainer...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=formatted_dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,                   # Increase for full production datasets
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",             # 8-bit optimizer reduces VRAM footprint
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="forensic_slm_checkpoints",
    ),
)

print("[5/5] Starting QLoRA Fine-Tuning...")
trainer.train()

# 6. Save & Export Directly to GGUF Format for Ollama/vLLM
GGUF_OUTPUT_DIR = "forensic_qwen2.5_7b_gguf"
print(f"\n[EXPORT] Saving fine-tuned model as GGUF (4-bit) to '{GGUF_OUTPUT_DIR}'...")
model.save_pretrained_gguf(
    GGUF_OUTPUT_DIR, 
    tokenizer, 
    quantization_method="q4_k_m"
)
print("[COMPLETE] GGUF exported successfully!")
