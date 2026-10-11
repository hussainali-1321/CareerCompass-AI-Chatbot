import json
import requests
import streamlit as st

OLLAMA_URL = "http://localhost:11434/api/chat"
st.set_page_config(page_title="Career Compass", page_icon="🧭", layout="centered")
st.title("🧭 Career Compass")
st.caption("Local AI Career Assistant")

with st.sidebar:
    st.subheader("Settings")
    model = st.text_input("Ollama model", value="qwen2.5:3b")
    st.info("Your chat is sent only to your local Ollama service.")
    st.caption("The model still uses RAM while generating; the UI itself cannot eliminate model memory use.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Assalam-o-Alaikum! Main Career Compass hoon. CV, skills, career roadmap ya Pakistan mein jobs ke bare mein pooch sakte hain."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Apna career question likhein...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Soch raha hoon…")
        try:
            payload = {
                "model": model.strip(),
                "messages": st.session_state.messages,
                "stream": True,
                "options": {"num_ctx": 2048, "num_predict": 256}
            }
            response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=(10, 600))
            response.raise_for_status()
            answer = ""
            for line in response.iter_lines():
                if not line:
                    continue
                item = json.loads(line.decode("utf-8"))
                answer += item.get("message", {}).get("content", "")
                placeholder.markdown(answer + "▌")
                if item.get("done"):
                    break
            if not answer:
                answer = "Ollama se khaali response mila. Model name check karein."
            placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except requests.exceptions.ConnectionError:
            placeholder.error("Ollama se connection nahi ho raha. Pehle Ollama app start karein.")
        except requests.exceptions.HTTPError as exc:
            placeholder.error(f"Ollama error: {exc}. Model name check karein.")
        except Exception as exc:
            placeholder.error(f"Error: {exc}")

if st.button("New chat"):
    st.session_state.messages = [{"role": "assistant", "content": "Assalam-o-Alaikum! Main Career Compass hoon. Aap kya poochna chahte hain?"}]
    st.rerun()
