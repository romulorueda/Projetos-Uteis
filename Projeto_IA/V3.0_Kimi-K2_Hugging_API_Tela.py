import os
import re
import time
import threading
import tempfile
import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import speech_recognition as sr
from gtts import gTTS
import pygame
from deep_translator import GoogleTranslator


# --- CONFIG HUGGING FACE ---
API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer SEU_TOKEN_AQUI",
    "Accept-Encoding": "identity"
}

# Inicializa pygame mixer para TTS
pygame.mixer.init()

# --- Funções ---


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


def speak_text(text):
    clean_text = re.sub(r'["\*-]', '', text)
    tts = gTTS(clean_text, lang='en')
    temp_file = os.path.join(tempfile.gettempdir(),
                             f"response_{int(time.time()*1000)}.mp3")
    tts.save(temp_file)
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    try:
        pygame.mixer.music.stop()
    except:
        pass
    try:
        pygame.mixer.music.unload()
    except:
        pass
    try:
        os.remove(temp_file)
    except:
        pass


def show_translation(word):
    try:
        # Traduz apenas quando o usuário clicar
        translation = GoogleTranslator(
            source='en', target='pt').translate(word)
        translation_label.config(text=f"{word} -> {translation}")
    except Exception as e:
        translation_label.config(text=f"{word} -> [Erro de tradução]")


def display_words(sentence):
    words_text.config(state="normal")
    words_text.delete("1.0", tk.END)

    for word in sentence.split():
        start_index = words_text.index(tk.INSERT)
        words_text.insert(tk.INSERT, word + " ")
        end_index = words_text.index(tk.INSERT)

        # Cria tag para cada palavra
        words_text.tag_add(word, start_index, end_index)
        words_text.tag_config(word, foreground="black")
        words_text.tag_bind(word, "<Button-1>", lambda e,
                            w=word: show_translation(w))
        words_text.tag_bind(
            word, "<Enter>", lambda e: words_text.config(cursor="hand2"))
        words_text.tag_bind(
            word, "<Leave>", lambda e: words_text.config(cursor="xterm"))

    words_text.config(state="disabled")


def listen_user():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 2.0
    recognizer.dynamic_energy_threshold = True
    with sr.Microphone() as source:
        chat_log.insert("end", "🎤 Listening...\n")
        chat_log.see("end")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, phrase_time_limit=10)
    try:
        user_input = recognizer.recognize_google(audio)
        chat_log.insert("end", f"You: {user_input}\n")
        chat_log.see("end")
        return user_input
    except sr.UnknownValueError:
        chat_log.insert("end", "Didn't catch that, try again.\n")
        chat_log.see("end")
        return None
    except sr.RequestError:
        chat_log.insert("end", "Speech recognition service error.\n")
        chat_log.see("end")
        return None


stop_event = threading.Event()
conversation_started = False


def conversation_loop():
    while not stop_event.is_set():
        user_input = listen_user()
        if not user_input:
            continue
        messages = [
            {"role": "system", "content": f"""
        Always use {user_level.get()} English level.
        Do not correct the punctuation "." "," ";" ":". 
        If the user makes any mistakes in vocabulary, grammar, tense or context, correct them carefully.
        Provide a brief explanation of the correction, explain why this is wrong. 
        After the correction, continue the conversation naturally and always ask a question to keep the user engaged.
        Never use asterisk "*".
        If the user's response doesn't directly answer your question or seems unrelated, ask if they really meant that: "Did you really mean this?"
        Always finish your sentences completely.
        Keep your answers short (1-3 sentences).
        Be friendly, patient, and encouraging.
            """},
            {"role": "user", "content": user_input}
        ]
        response = query_hf(messages)
        chat_log.insert("end", f"AI: {response}\n")
        chat_log.see("end")
        display_words(response)
        speak_text(response)


def start_conversation():
    global conversation_started
    if not conversation_started:
        threading.Thread(target=conversation_loop, daemon=True).start()
        conversation_started = True


def on_level_selected(*args):
    start_conversation()


def close_program():
    if messagebox.askokcancel("Quit", "Do you really want to exit?"):
        stop_event.set()
        root.destroy()


# --- GUI ---
root = tk.Tk()
root.title("English Conversation AI")
root.state("zoomed")  # abre maximizada
root.configure(bg="#75A5CA")  # fundo da janela

# Título centralizado visualmente
title_label = tk.Label(
    root, text="English Conversation AI", font=("Arial", 18, "bold"), bg="#75A5CA")
title_label.pack(padx=450, pady=10, anchor="w")

# Nível de inglês
user_level = tk.StringVar(value="Beginner")
level_frame = tk.Frame(root, bg="#75A5CA")
level_frame.pack(padx=400, pady=20, anchor="w")
tk.Label(level_frame, text="Choose your English level:",
         font=("Arial", 15, "bold"), bg="#75A5CA").pack(side="left")
levels = ["Beginner", "Elementary", "Pre-Intermediate",
          "Intermediate", "Upper-Intermediate"]
level_menu = tk.OptionMenu(level_frame, user_level, *levels)
level_menu.config(bg="#75A5CA", fg="black", font=(
    "Arial", 12, "bold"), bd=0, highlightthickness=0)  # botão principal
level_menu["menu"].config(bg="#75A5CA", fg="black",
                          font=("Arial", 12, "bold"))  # dropdown
level_menu.pack(side="left", padx=5)

# Adiciona trace para disparar conversa automaticamente ao escolher nível
user_level.trace_add("write", on_level_selected)

# Chat log
chat_log = tk.scrolledtext.ScrolledText(
    root,
    width=110,     # largura em caracteres
    height=25,    # altura em linhas
    wrap="word",
    font=("Arial", 12),
    bg="#92B9D6"
)
chat_log.pack(padx=30, pady=5, anchor="w")  # alinhada à esquerda

# Palavras clicáveis com quebra de linha automática
words_text = tk.Text(
    root,
    width=55,     # largura em caracteres
    height=12,     # altura em linhas (ajustável dinamicamente depois)
    wrap="word",
    font=("Arial", 13, "bold"),
    bg="#92B9D6",
    bd=0,
    highlightthickness=0
)
words_text.pack(padx=250, pady=20, anchor="w")  # alinhada à esquerda
words_text.config(state="disabled")


# Tradução
translation_label = tk.Label(
    root, text="Click a word to translation", font=("Arial", 14), fg="black", bg="#75A5CA")
translation_label.pack(padx=250, pady=10, anchor="w")

# Botões
buttons_frame = tk.Frame(root, bg="#75A5CA")
buttons_frame.pack(padx=250, pady=10, anchor="w")
tk.Button(buttons_frame, text="Start Conversation",
          command=start_conversation).pack(side="left", padx=5)
tk.Button(buttons_frame, text="Close Program",
          command=close_program).pack(side="left", padx=5)

root.mainloop()
