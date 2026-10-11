# Career Compass — Fine-tuning files

This package contains a reproducible QLoRA training script for the Career Compass chatbot using `Qwen/Qwen2.5-3B-Instruct`.

## Files
- `train_qlora.py`: training script intended for Google Colab with a GPU.
- `CareerCompass_QLoRA.ipynb`: Colab notebook version of the script.
- `requirements-colab.txt`: dependencies.
- `README.md`: setup and important notes.

## Important: original artifacts vs recreated training files
This package does **not** contain your already-trained LoRA adapter or the original 1785-row `CareerCompassDataset.csv`, because those original binary/data files were not attached to this chat. It also does not pretend to reproduce the exact historical training run. It provides the training code/config matching the settings recorded for your run.

Your known saved locations from your project:
- Google Drive output folder: `/content/drive/MyDrive/CareerCompass/qwen-career-compass-final`
- Windows extracted adapter folder: `C:\CareerCompass`
- Existing adapter ZIP noted on your PC: `C:\Users\DELL\OneDrive\Desktop\KNN project\qwen-career-compass-final.zip`

The Windows folder was reported to contain:
- `adapter_model.safetensors`
- `adapter_config.json`
- `tokenizer.json`
- `tokenizer_config.json`
- `chat_template.jinja`
- `training_args.bin`
- `README.md`
- `checkpoint-100/`
- `checkpoint-303/`

Those are the actual trained model artifacts. Keep them safe and do not delete them.

## Run in Colab
1. Open a new Google Colab notebook and enable a GPU runtime (Runtime → Change runtime type → T4 GPU, if available).
2. Mount Google Drive:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
3. Upload/copy your original `CareerCompassDataset.csv` into the Colab working directory, or edit `DATASET_PATH` in `train_qlora.py`.
4. Install:
   ```python
   %pip install -U transformers datasets accelerate peft bitsandbytes pandas
   ```
5. Run the script:
   ```python
   !python train_qlora.py
   ```

The script expects CSV columns exactly named `instruction` and `response`. It uses a 90/10 split, QLoRA 4-bit NF4, LoRA r=16, alpha=32, dropout=0.05, batch size 2, gradient accumulation 8, 3 epochs, and learning rate 2e-4.

## Notes
- Training again will take GPU time and may overwrite/recreate output files in the Drive folder.
- If you only want to use the model you already trained, you do not need to train again. Use the existing `qwen-career-compass-final` adapter folder.
- A PEFT adapter is not a complete standalone base model; it needs the compatible Qwen base model when loaded with Transformers. For Ollama deployment, you generally need a compatible GGUF export/merge workflow; do not rename a `.safetensors` adapter to `.gguf`.
