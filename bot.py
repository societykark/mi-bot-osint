import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# ⚠️ Coloca aquí tu NUEVO token (revoca el viejo con @BotFather)
TOKEN = '8830759236:AAEK_kVmhJnNTUdbZtFSFI8JYfzMNkOx-Bk'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def search_username(username: str) -> str:
    url = f"https://whatsmyname.app/api/v1/username?username={username}"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        if 'sites' in data and data['sites']:
            lines = [f"✅ {site['name']}: {site['uri']}" for site in data['sites']]
            return "\n".join(lines) if lines else "No se encontraron resultados."
        else:
            return "No se encontraron resultados o la API no devolvió datos."
    except Exception as e:
        return f"Error: {e}"

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Bot OSINT funcionando. Usa /username <nombre>")

def username(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("Uso: /username <nombre>")
        return
    user = context.args[0]
    update.message.reply_text(f"🔍 Buscando '{user}'...")
    resultado = search_username(user)
    update.message.reply_text(resultado[:4000])

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("username", username))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()