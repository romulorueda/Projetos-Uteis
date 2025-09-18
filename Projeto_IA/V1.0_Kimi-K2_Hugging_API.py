import os
import requests
import speech_recognition as sr
from gtts import gTTS
import re
import pygame
import tempfile
import time

# --- CONFIG HUGGING FACE ---
API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer SEU_TOKEN_AQUI",
    "Accept-Encoding": "identity"  # evita problemas de gzip
}


def query_hf(messages):
    payload = {
        "model": "moonshotai/Kimi-K2-Instruct-0905:together",
        "messages": messages
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Erro ao gerar resposta: {e}]"


# --- LOOP DE CONVERSA COM VOZ E HISTÓRICO ---
print("Fale 'stop the class' a qualquer momento para sair.\n")

history = []  # lista para armazenar o histórico
max_history = 10  # limite de interações no histórico

recognizer = sr.Recognizer()
recognizer.pause_threshold = 5  # espera até &segundos de silêncio

# inicializa pygame mixer
pygame.mixer.init()

english_levels = {
    "number one": "Beginner",
    "number two": "Elementary",
    "number three": "Pre-Intermediate",
    "number four": "Intermediate",
    "number five": "Upper-Intermediate"
}

print("Please choose your English level by saying the number or name:")
for key, level in english_levels.items():
    print(f"{key} - {level}")

recognizer = sr.Recognizer()
user_level = None

while user_level is None:
    with sr.Microphone() as source:
        print("Listening for your choice...")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        audio = recognizer.listen(source)

    try:
        spoken_text = recognizer.recognize_google(audio)
        print(f"You said: {spoken_text}")

        # tenta extrair o número do que o usuário falou
        for key in english_levels:
            if key == spoken_text or english_levels[key].lower() == spoken_text.lower():
                user_level = english_levels[key]
                break

        if user_level is None:
            print("I didn't understand. Please say the number (1-5) or the level name.")
    except sr.UnknownValueError:
        print("Didn't catch that, please try again.")
    except sr.RequestError:
        print("Error with the speech recognition service.")


while True:
    with sr.Microphone() as source:
        print("Listening...")
        # Remove ajuste de ruído rápido, pois pode cortar palavras
        # Ajuste opcional de ruído, usando poucos segundos:
        # recognizer.adjust_for_ambient_noise(source, duration=1)

        # Espera indefinidamente até o usuário começar a falar
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        audio = recognizer.listen(source, phrase_time_limit=15)

    try:
        user_input = recognizer.recognize_google(audio)
        print(f"You (voice): {user_input}")
    except sr.UnknownValueError:
        print("Não entendi o que você disse, tente novamente.")
        continue
    except sr.RequestError:
        print("Erro de conexão com o serviço de reconhecimento de voz.")
        continue

    if user_input.lower() == "close the program":
        break

    # adiciona a pergunta do usuário no histórico
    history.append({"role": "user", "content": user_input})

    # mantém apenas as últimas 'max_history' interações
    recent_history = history[-max_history*2:]  # alterna user/AI

    # adiciona instruções iniciais para a IA
    instructions = {
        "role": "system",
        "content": f"""
        You are an English teacher who helps the user to practice speaking. Always use {user_level} English level.
        Do not correct the punctuation "." "," ";" ":".
        If the user makes any mistakes in vocabulary, grammar, tense or context, correct them carefully.
        Provide a brief explanation of the correction, explain why this mistakes is wrong. 
        After the correction, continue the conversation naturally and always ask a question to keep the user engaged.
        Never use asterisk "*".
        If the user's response does not directly answer your question or seems unrelated, gently ask for clarification, e.g. "Did you mean…?" or "Can you clarify what you meant by that?"
        Always finish your sentences completely.
        Keep your answers short (1-3 sentences).
        Be friendly, patient, and encouraging.
    """
    }

    # cria a lista de mensagens para enviar à API
    messages_payload = [instructions] + recent_history

    # --- GERA RESPOSTA NA NUVEM ---
    response_text = query_hf(messages_payload)
    print("\n=== RESPOSTA DO MODELO ===")
    print(response_text)

    # adiciona a resposta da IA no histórico
    history.append({"role": "assistant", "content": response_text})

    # --- CONVERTE TEXTO PARA VOZ ---
    # Remove aspas antes de passar para o TTS
    clean_text = re.sub(r'["\*-]', '', response_text)

    tts = gTTS(clean_text, lang='en')
    temp_file = os.path.join(tempfile.gettempdir(), "response.mp3")
    tts.save(temp_file)

    # toca o áudio com pygame (libera depois)
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    pygame.mixer.music.unload()

    # remove o arquivo temporário
    os.remove(temp_file)
