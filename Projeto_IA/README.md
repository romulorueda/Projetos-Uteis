# 🗣️ English Conversation AI  

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)  
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange)](https://docs.python.org/3/library/tkinter.html)  
[![Hugging Face](https://img.shields.io/badge/API-HuggingFace-yellow?logo=huggingface)](https://huggingface.co/)  
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)  

Um aplicativo em **Python + Tkinter** para treinar conversação em inglês com:  
- 🎙️ **Reconhecimento de fala**  
- 🔊 **Síntese de voz** com animação de ondas sonoras  
- 🤖 **Integração com IA** (Hugging Face API ou resposta local simulada)  
- 📖 **Tradução instantânea** de palavras clicadas  
- 🖼️ **Interface gráfica** com GIF animado  

---

## 🚀 Funcionalidades
✔️ Conversa em inglês em tempo real  
✔️ Níveis de aprendizado: **Iniciante → Pós Intermediário**  
✔️ Tradução automática ao clicar em palavras  
✔️ Voz natural usando **gTTS + pygame**  
✔️ Reconhecimento de voz com **SpeechRecognition + Google API**  
✔️ Interface intuitiva feita em **Tkinter**  

---

## 🛠️ Instalação

### 1. Clone este repositório
```bash
git clone https://github.com/romulojuca/Programas_Uteis.git
cd english-conversation-ai
```

### 2. Crie um ambiente virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

---

## ▶️ Como executar
```bash
python main.py
```

---

## 📦 Dependências principais
- `requests` – Comunicação com API Hugging Face  
- `SpeechRecognition` – Reconhecimento de fala  
- `gTTS` – Text-to-Speech (Google)  
- `pygame` – Reproduzir áudio  
- `deep-translator` – Tradução (EN → PT)  
- `numpy` – Processamento de áudio (ondas sonoras)  
- `pyttsx3` – TTS offline (gera `.wav`)  
- `Pillow` – Manipulação de imagens/GIFs  

*(instaladas automaticamente via `requirements.txt`)*  

---

## ⚙️ Configuração extra
Para usar a IA real, configure seu **token do Hugging Face** no código:

```python
API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {"Authorization": "Bearer SEU_TOKEN_AQUI"}
```

Substitua `SEU_TOKEN_AQUI` pelo seu [token da Hugging Face](https://huggingface.co/settings/tokens).  

---

## 📌 Roadmap futuro
- [ ] Melhorar interface (dark mode e responsividade)  
- [ ] Adicionar histórico de conversas  
- [ ] Suporte a mais idiomas além de EN/PT  
- [ ] Deploy em mobile (Kivy / BeeWare)  
