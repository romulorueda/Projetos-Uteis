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
import wave
import struct
import numpy as np
import pyttsx3
from PIL import Image, ImageTk, ImageSequence

# --- CONFIG HUGGING FACE ---
API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer SEU_ToKEN_AQUII",
    "Accept-Encoding": "identity"
}

# Inicializa pygame mixer para TTS
pygame.mixer.init()

# --- Funções ---


def query_hf(messages):
    global user_level
    global user_level_ia
    if user_level.get() == "Iniciante":
        user_level_ia = "Begginer"
    elif user_level.get() == "Pós Iniciante":
        user_level_ia = "Elementary"
    elif user_level.get() == "Pré Intermediário":
        user_level_ia = "Pre Intermediate"
    elif user_level.get() == "Intermediário":
        user_level_ia = "Intermediate"
    elif user_level.get() == "Pós Intermediário":
        user_level_ia = "Upper Intermediate"
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


def speak_text(text, canvas):
    # --- WAV temporário para animação ---
    wav_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    engine = pyttsx3.init()
    engine.save_to_file(text, wav_path)
    engine.runAndWait()

    # === criando .mp3 temporário para voz real ===
    clean_text = re.sub(r'["\*-]', '', text)
    tts = gTTS(clean_text, lang='en')
    temp_file = os.path.join(tempfile.gettempdir(),
                             f"response_{int(time.time()*1000)}.mp3")
    tts.save(temp_file)

    # --- Toca o MP3 e espera terminar ---
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    # inicia as waves junto com o áudio
    threading.Thread(target=lambda: animate_waves(
        canvas, wav_path), daemon=True).start()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    # cleanup
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        os.remove(temp_file)
    except:
        pass


# ===== Função de animação de ondas =====
def animate_waves(canvas, wav_path):
    wav = wave.open(wav_path, 'rb')
    frames_per_chunk = 1024
    width = int(canvas['width'])
    height = int(canvas['height'])

    def update():
        while True:
            data = wav.readframes(frames_per_chunk)
            if len(data) == 0:
                break
            count = len(data) // 2
            shorts = struct.unpack("%dh" % count, data)
            amp = np.abs(shorts)
            avg_amp = np.mean(amp) / 32768

            canvas.delete("wave")
            num_bars = 50
            bar_width = width / num_bars
            for i in range(num_bars):
                gain = 4  # aumenta o tamanho das ondas
                bar_height = avg_amp * height * \
                    gain * np.random.uniform(0.5, 1.0)
                x0 = i * bar_width
                y0 = height - bar_height
                x1 = x0 + bar_width * 0.8
                y1 = height
                canvas.create_rectangle(
                    x0, y0, x1, y1, fill="#010911", tag="wave")
            canvas.update()
            time.sleep(0.03)
        canvas.delete("wave")
        wav.close()

    threading.Thread(target=update, daemon=True).start()


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
        chat_log.insert("end", "🎤 Fale...\n")
        chat_log.see("end")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, phrase_time_limit=10)
    try:
        user_input = recognizer.recognize_google(audio)
        chat_log.insert("end", "Você: ", "user_color")
        chat_log.insert("end", f" {user_input}\n")
        chat_log.tag_config(
            "user_color", background="#75A5CA")
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
        You are an English teacher helping a user practice English.
        Always use {user_level_ia} English level.
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
        chat_log.insert("end", "AI: ", "ai_color")
        chat_log.insert("end", f" {response}\n")
        chat_log.tag_config(
            "ai_color", background="#75A5CA")
        chat_log.see("end")
        display_words(response)
        speak_text(response, wave_canvas)


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


def animate_gif(frame_index=0):
    frame = frames[frame_index]
    label.config(image=frame)
    root.after(100, lambda: animate_gif((frame_index+1) % len(frames)))


# --- GUI ---
root = tk.Tk()
root.title("English Conversation AI")
# Tamanho fixo
root.geometry("950x700")
# Desabilita maximizar e redimensionar
root.resizable(False, False)
root.configure(bg="#75A5CA")  # fundo da janela

# Nível de inglês
user_level = tk.StringVar(value="Iniciante")
tk.Label(root, text="Escolha o nível de Inglês:",
         font=("Arial", 14, "bold"), bg="#75A5CA").place(x=310, y=20, width=250, height=25)
levels = ["Iniciante", "Pós Iniciante", "Pré Intermediário",
          "Intermediário", "Pós Intermediário"]
level_menu = tk.OptionMenu(root, user_level, *levels)
level_menu.config(bg="#75A5CA", fg="black", activeforeground="black", activebackground="#75A5CA", font=(
    "Arial", 12, "bold"), bd=0, highlightthickness=0)  # botão principal
level_menu["menu"].config(bg="#75A5CA", fg="black",
                          font=("Arial", 12, "bold"))  # dropdown
level_menu.place(x=560, y=20, width=165, height=25)

# Adiciona trace para disparar conversa automaticamente ao escolher nível
user_level.trace_add("write", on_level_selected)
user_level_ia = user_level.get()

# Chat log
chat_log = tk.scrolledtext.ScrolledText(
    root,
    width=110,     # largura em caracteres
    height=15,    # altura em linhas
    wrap="word",
    font=("Arial", 12),
    bg="#92B9D6"
)
chat_log.place(x=130, y=100, width=700, height=300)

wave_canvas = tk.Canvas(root, width=200, height=50,
                        bg="#75A5CA", bd=0, highlightthickness=0)
wave_canvas.place(x=380, y=420, width=200, height=50)

# Carrega o GIF
robot_img = Image.open("ia.gif")
frames = [ImageTk.PhotoImage(frame.copy().resize(
    (50, 50))) for frame in ImageSequence.Iterator(robot_img)]

label = tk.Label(root, bd=0, highlightthickness=0)
label.place(x=330, y=420)

# Palavras clicáveis com quebra de linha automática
words_text = tk.Text(
    root,
    width=55,     # largura em caracteres
    height=8,     # altura em linhas (ajustável dinamicamente depois)
    wrap="word",
    font=("Arial", 13, "bold"),
    bg="#92B9D6",
    bd=0,
    highlightthickness=0
)
words_text.place(x=180, y=490, width=600, height=150)
words_text.config(state="disabled")


# Tradução
translation_label = tk.Label(
    root, text="Clique na palavra para traduzir.", font=("Arial", 14), fg="black", bg="#75A5CA")
translation_label.place(x=280, y=650, width=400, height=25)

tk.Button(root, text="Close Program", bg="#C5E5FD", font=("Arial", 10, "bold"), command=close_program).place(
    x=820, y=660, width=120, height=30)

animate_gif()
root.mainloop()
