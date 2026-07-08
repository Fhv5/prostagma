# Prostagma? (Πρόσταγμα;)

My favorite game of all time, Age of Mythology, inspired me to learn Greek. I've always heard that the best way to learn a new language is to "immerse" yourself in it; expose yourself to its vocabulary and sentence structure throughout your daily life.

That's why I decided to set AoM's UI language to Greek. To enhance my learning, I built a tool that displays both the literal and contextual meaning in English of any word, sentence or paragraph I come across in the game. All this without directly intervening in it (...and without the game thinking I'm cheating, hahaha).

Thus, "Prostagma?" (Πρόσταγμα;) was born.

## Features:
- Overlay window that stays on top of other windows
- OCR to extract Greek text from screenshot in the clipboard
- Translation using Ollama LLM and Google Translate
- Audio playback of pronunciation
- Configurable hotkeys

## How to run:

### 1. Server

```bash
mvn clean install
mvn spring-boot:run
```

### 2. Client

```bash
python client/main.py
```
