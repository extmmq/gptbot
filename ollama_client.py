import requests

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "llama3"

def paraphrase_article(text):
    prompt = f"""Ты — весёлый новостной бот. Преобразуй эту новость с юмором и яркими словами, сохрани суть:
    \n\n{text}\n\n
    Добавь немного сарказма или иронии, не меняя фактов."""

    response = requests.post(OLLAMA_API, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })

    if response.ok:
        return response.json()["response"]
    return "Не удалось перефразировать статью 😢"