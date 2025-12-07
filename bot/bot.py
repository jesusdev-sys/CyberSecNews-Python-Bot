import os
import time
import requests
import feedparser
from datetime import datetime
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')  # Puede ser un ID numérico o @nombre_del_canal

# Lista de URLs de los feeds RSS
FEEDS = [
    "https://krebsonsecurity.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.zerodayinitiative.com/rss.xml",
    "https://packetstormsecurity.com/files/rss.xml",
    "https://www.exploit-db.com/rss.xml",
    "https://blog.talosintelligence.com/rss/",
    "https://securelist.com/feed/",
    "https://www.darkreading.com/rss.xml"
]


# Archivo para guardar los enlaces ya enviados
SEEN_ARTICLES = 'seen.txt'

def cargar_noticias_enviadas():
    """
    Carga del archivo las URLs de noticias ya enviadas.
    Retorna un set para evitar duplicados.
    """
    if os.path.exists(SEEN_ARTICLES):
        with open(SEEN_ARTICLES, "r") as f:
            return set(f.read().splitlines())
    return set()

def guardar_noticias_enviadas(link):
    """
    Guarda una URL de noticia como enviada.
    """
    with open(SEEN_ARTICLES, "a") as f:
        f.write(link + "\n")

def obtener_noticias():
    """
    Obtiene noticias recientes desde los feeds.
    Retorna una lista de tuplas (título, enlace).
    """
    noticias = []
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:2]:
            noticias.append((entry.title, entry.link))
    return noticias

def enviar_mensaje_telegram(mensaje):
    """
    Envía un mensaje al canal o chat de Telegram usando la API.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"❌ Error al enviar: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def enviar_novedades():
    """
    Verifica qué noticias no han sido enviadas y las manda por Telegram.
    """
    noticias_enviadas = cargar_noticias_enviadas()
    noticias = obtener_noticias()

    for titulo, link in noticias:
        if link not in noticias_enviadas:
            hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            mensaje = (
                f"🛡️ <b>[CYBERSEC ALERT]</b>\n"
                f"📅 <i>{hora_actual}</i>\n\n"
                f"<b>{titulo}</b>\n"
                f"🔗 {link}"
            )
            enviar_mensaje_telegram(mensaje)
            guardar_noticias_enviadas(link)

if __name__ == "__main__":
    while True:
        print("⏳ Buscando noticias...")
        enviar_novedades()
        print("✅ Noticias enviadas. Esperando 25 minutos para la próxima búsqueda...")
        time.sleep(1500)
