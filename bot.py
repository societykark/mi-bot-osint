import logging
import requests
import asyncio
import subprocess
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv('8830759236:AAHUoBC211ELrbCmT-rPO2DKame6xSEdkXo')
if not TOKEN:
    raise ValueError("BOT_TOKEN no está configurado en las variables de entorno")

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
    except requests.Timeout:
        return "⏰ La consulta tardó demasiado. Intenta más tarde."
    except Exception as e:
        return f"Error: {e}"

async def search_email(email: str) -> str:
    try:
        process = await asyncio.create_subprocess_exec(
            'holehe', email,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        output = stdout.decode()
        return output if output else "No se encontraron resultados o hubo un error."
    except Exception as e:
        return f"Error al ejecutar holehe: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Bot OSINT mejorado*\n\n"
        "Comandos:\n"
        "/username <nombre> - Busca usuario\n"
        "/email <correo> - Verifica correo",
        parse_mode='Markdown'
    )

async def username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /username <nombre>\nEj: /username juanito")
        return
    user = context.args[0]
    await update.message.reply_text(f"🔍 Buscando '{user}'...")
    resultado = await search_username(user)
    if len(resultado) > 4000:
        resultado = resultado[:4000] + "\n...(truncado)"
    await update.message.reply_text(resultado)

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /email <correo>\nEj: /email prueba@gmail.com")
        return
    mail = context.args[0]
    await update.message.reply_text(f"📧 Analizando '{mail}'...")
    resultado = await search_email(mail)
    if len(resultado) > 4000:
        resultado = resultado[:4000] + "\n...(truncado)"
    await update.message.reply_text(resultado)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("username", username))
    app.add_handler(CommandHandler("email", email))
    print("🤖 Bot OSINT funcionando...")
    app.run_polling()

if __name__ == '__main__':
    main()
