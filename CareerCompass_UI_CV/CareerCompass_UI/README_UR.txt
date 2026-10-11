CAREER COMPASS UI WITH CV UPLOAD

1. Extract ZIP.
2. Open the extracted folder in VS Code.
3. Activate your existing .venv.
4. Install:
   pip install -r requirements.txt
5. Start Ollama desktop and ensure qwen2.5:3b is installed.
6. Run:
   python -m streamlit run app.py

Features:
- CV upload: PDF, DOCX, TXT
- CV text extraction and Ollama-based analysis
- Job matching against the Pakistan jobs CSV, if found in the project folder or uploaded in the Job Recommendations tab
- Local Ollama chatbot

Note:
- The UI currently uses the Ollama qwen2.5:3b model, not the fine-tuned adapter.
- Scanned PDFs may require OCR.
- Model inference still uses RAM, so keep responses short and avoid running test_model.py at the same time.
