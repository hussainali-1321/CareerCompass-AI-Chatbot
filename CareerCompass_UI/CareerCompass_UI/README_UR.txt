CAREER COMPASS LOCAL UI (Windows)

IMPORTANT:
- Ye UI installed Ollama ke local model qwen2.5:3b ko use karti hai.
- UI khud model load nahi karti; Ollama model run karta hai.
- Is se Transformers wali full-precision loading se bach sakte hain, lekin model run hote waqt RAM phir bhi use hogi.
- Filhal ye Ollama ka base model use karegi, aapka fine-tuned adapter nahi. Adapter ko Ollama-compatible format mein convert karna alag step hai.

RUN:
1. ZIP extract karein.
2. VS Code mein CareerCompass_UI folder open karein.
3. Apna .venv activate karein.
4. Terminal mein one time run karein: pip install -r requirements.txt
5. Ollama app start karein.
6. Terminal mein run karein: python -m streamlit run app.py
7. Terminal mein dikhaya gaya Local URL browser mein open karein.

UI context 2048 tokens aur max response 256 tokens rakhti hai, taake memory usage ko limit karne mein madad mile.
Agar PC phir slow ho, chat stop karein aur Ollama ko close hone dein.
UI band karne ke liye terminal mein Ctrl+C press karein.
