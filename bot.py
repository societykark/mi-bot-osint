import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ⚠️ Coloca AQUÍ tu token NUEVO (revoca el viejo con @BotFather)
TOKEN = '8830759236:AAEK_kVmhJnNTUdbZtFSFI8JYfzMNkOx-Bk'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Bot funcionando correctamente!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot iniciado...")
    app.run_polling()

if __name__ == '__main__':
    main()