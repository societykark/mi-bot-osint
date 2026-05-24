import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ⚠️ PON AQUÍ TU NUEVO TOKEN (revoca el viejo y créalo con @BotFather)
TOKEN = '8830759236:AAEK_kVmhJnNTUdbZtFSFI8JYfzMNkOx-Bk'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def search_username(username: str) -> str:
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot funcionando. Usa /username <nombre>")

async def username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /username <nombre>")
        return
    user = context.args[0]
    await update.message.reply_text(f"🔍 Buscando '{user}'...")
    resultado = await search_username(user)
    await update.message.reply_text(resultado[:4000])

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("username", username))
    print("Bot iniciado correctamente")
    app.run_polling()

if __name__ == '__main__':
    main()