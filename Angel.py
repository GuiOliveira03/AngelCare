import streamlit as st
import pdfplumber
import openai
import os
import random
import time
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(pdf_path):
    """Extrai o texto de um arquivo PDF usando pdfplumber."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return text

def ask_openai(messages, pdf_text):
    """Envia uma pergunta para a OpenAI garantindo que a resposta seja baseada apenas no PDF."""
    client = openai.OpenAI()
    system_prompt = (
        "Você é um assistente virtual de uma distribuidora master de medical devices chamada Angel Care que fornece materiais inovadores para os tratamentos da coluna vertebral em todo território nacional. Seu usuário principal será o time comerial, que fará perguntas técnicas sobre os produtos.:\n\n"
        f"{pdf_text}\n\n"
        "Se a informação solicitada não estiver no PDF, diga 'Não encontrei essa informação.'"
    )
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages[-5:]  # Limita o histórico para evitar duplicação
    response = client.chat.completions.create(
        model="gpt-4",
        messages=full_messages,
        temperature=0,  # Temperatura zero para evitar alucinações
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

def get_random_greeting():
    """Retorna uma saudação aleatória para tornar a conversa mais dinâmica."""
    greetings = [
        "Oi! Como posso te ajudar hoje? 😊",
        "Olá! O que você gostaria de saber? 😃",
        ]
    return random.choice(greetings)

def typewriter_effect(text, delay=0.02):
    """Animação simulando digitação da resposta."""
    response_container = st.empty()
    full_text = ""
    for char in text:
        full_text += char
        response_container.markdown(f"**Angel:** {full_text}")
        time.sleep(delay)

# Caminho do PDF pré-carregado
pdf_path = "BoneAnax.pdf"  # Substitua pelo caminho correto do seu PDF
pdf_text = extract_text_from_pdf(pdf_path)

# Interface do Streamlit
st.title("Angel IA 🧑‍🔬")

# Inicializa a sessão de histórico
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": get_random_greeting()}  # Primeira resposta mais natural
    ]

# Exibir histórico de conversa antes da caixa de entrada
chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.write(f"**Você:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.write(f"**Angel:** {msg['content']}")

# Caixa de input sempre no final, fixada na parte inferior
def user_input():
    question = st.text_area("Digite sua pergunta:", key="input_box")
    if st.button("Perguntar") and question:
        with st.spinner(random.choice(["Pensando na melhor resposta... 🤔", "Só um momento... 🤖"])):
            st.session_state.chat_history.append({"role": "user", "content": question})
            answer = ask_openai(st.session_state.chat_history, pdf_text)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.session_state["last_answer"] = answer
            st.rerun()
    elif "last_answer" in st.session_state and st.session_state["last_answer"] != st.session_state.chat_history[-1]["content"]:
        typewriter_effect(st.session_state["last_answer"])

user_input()