import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import re
import subprocess
import json
import os

# ================= CONFIGURACIÓN =================
# Todas las claves se leen de variables de entorno (SEGURO)
TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise ValueError("❌ La variable de entorno TOKEN no está configurada.")

NUMVERIFY_KEY = os.environ.get('NUMVERIFY_KEY', '')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================= FUNCIÓN PARA BUSCAR USUARIO (SHERLOCK) =================
async def search_username(username: str) -> str:
    try:
        # Ejecutar Sherlock y guardar resultado en JSON
        result = subprocess.run(
            ["sherlock", username, "--output", "json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        json_file = f"{username}.json"
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
            os.remove(json_file)
            lines = []
            for site, info in data.items():
                if info.get("url"):
                    lines.append(f"• [{site}]({info['url']})")
            return "\n".join(lines[:20]) if lines else "No se encontraron resultados."
        else:
            return "No se encontraron resultados o hubo un error."
    except Exception as e:
        return f"❌ Error: {e}"

# ================= FUNCIÓN PARA ESCANEAR IP =================
async def scan_ip(ip: str) -> str:
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,timezone,isp,org,as,mobile,proxy,hosting,query,lat,lon"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('status') == 'success':
            mensaje = f"🌐 *Información de la IP* `{ip}`\n━━━━━━━━━━━━━━━━\n"
            mensaje += f"📍 *Ubicación:*\n• País: {data.get('country', 'N/A')}\n• Región: {data.get('regionName', 'N/A')}\n• Ciudad: {data.get('city', 'N/A')}\n• Código Postal: {data.get('zip', 'N/A')}\n• Zona Horaria: {data.get('timezone', 'N/A')}\n\n"
            mensaje += f"🖥️ *Red:*\n• ISP: {data.get('isp', 'N/A')}\n• Organización: {data.get('org', 'N/A')}\n• AS: {data.get('as', 'N/A')}\n\n"
            mensaje += f"📡 *Detalles:*\n• Móvil: {'Sí' if data.get('mobile') else 'No'}\n• Proxy: {'Sí' if data.get('proxy') else 'No'}\n• Hosting: {'Sí' if data.get('hosting') else 'No'}\n\n"
            mensaje += f"🗺️ *Coordenadas:*\n• Latitud: {data.get('lat', 'N/A')}\n• Longitud: {data.get('lon', 'N/A')}\n• [Google Maps](https://www.google.com/maps?q={data.get('lat', 'N/A')},{data.get('lon', 'N/A')})"
            return mensaje
        else:
            return f"❌ Error: {data.get('message', 'IP inválida')}"
    except Exception as e:
        return f"❌ Error: {e}"

# ================= FUNCIÓN PARA RASTREAR NÚMERO =================
async def scan_number(number: str) -> str:
    if not NUMVERIFY_KEY:
        return "❌ API key de Numverify no configurada."
    try:
        numero_limpio = re.sub(r'[^0-9+]', '', number)
        url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_KEY}&number={numero_limpio}&format=1"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('valid'):
            mensaje = f"📞 *Información del Número*\n━━━━━━━━━━━━━━━━\n"
            mensaje += f"• Número: {data.get('international_format', 'N/A')}\n"
            mensaje += f"• País: {data.get('country_name', 'N/A')}\n"
            mensaje += f"• Código de País: +{data.get('country_code', 'N/A')}\n"
            mensaje += f"• Prefijo: {data.get('country_prefix', 'N/A')}\n"
            mensaje += f"• Operador: {data.get('carrier', 'No disponible')}\n"
            mensaje += f"• Tipo: {data.get('line_type', 'N/A')}\n"
            mensaje += f"• Ubicación: {data.get('location', 'N/A')}"
            return mensaje
        else:
            return f"❌ Número inválido: {data.get('error', {}).get('info', 'Desconocido')}"
    except Exception as e:
        return f"❌ Error: {e}"

# ================= COMANDOS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """🔐 *OSINT BOT v2.0*
━━━━━━━━━━━━━━━━
$ root@system: Access Granted ~

Bienvenido al bot de inteligencia de fuentes abiertas.

*Comandos disponibles:*
/username <nombre> → Buscar usuario en redes
/ip <IP> → Escanear IP
/numero <número> → Rastrear número
/menu → Menú interactivo
/help → Ayuda"""
    await update.message.reply_text(msg, parse_mode='Markdown')

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 Buscar Usuario", callback_data='username')],
        [InlineKeyboardButton("🌐 Escanear IP", callback_data='ip')],
        [InlineKeyboardButton("📞 Rastrear Número", callback_data='numero')],
        [InlineKeyboardButton("❓ Ayuda", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎯 *Selecciona una opción:*", reply_markup=reply_markup, parse_mode='Markdown')

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """🤖 *Ayuda - Comandos*
━━━━━━━━━━━━━━━━
/username <nombre> → Busca el usuario en redes sociales.
/ip <IP> → Geolocaliza y analiza una IP.
/numero <número> → Obtén información de un número telefónico.
/menu → Menú interactivo.
/help → Esta ayuda.

*Ejemplos:*
/username kaliboy
/ip 8.8.8.8
/numero +521234567890"""
    await update.message.reply_text(msg, parse_mode='Markdown')

async def username_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Uso: /username <nombre>")
        return
    user = context.args[0]
    msg = await update.message.reply_text(f"🔍 Buscando '{user}'...")
    resultado = await search_username(user)
    if len(resultado) > 4000:
        for i in range(0, len(resultado), 4000):
            await update.message.reply_text(resultado[i:i+4000], parse_mode='Markdown')
    else:
        await msg.edit_text(resultado, parse_mode='Markdown')

async def ip_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Uso: /ip <dirección IP>")
        return
    ip = context.args[0]
    partes = ip.split('.')
    if not (len(partes) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in partes)):
        await update.message.reply_text("❌ IP inválida. Formato: xxx.xxx.xxx.xxx")
        return
    msg = await update.message.reply_text(f"🌐 Escaneando IP `{ip}`...")
    resultado = await scan_ip(ip)
    await msg.edit_text(resultado, parse_mode='Markdown')

async def numero_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Uso: /numero <número internacional>")
        return
    numero = context.args[0]
    msg = await update.message.reply_text(f"📞 Rastreando número `{numero}`...")
    resultado = await scan_number(numero)
    await msg.edit_text(resultado, parse_mode='Markdown')

# ================= CALLBACKS =================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'username':
        await query.edit_message_text("🔍 *Buscar Usuario*\n\nEnvía el nombre de usuario con el comando:\n`/username <nombre>`", parse_mode='Markdown')
    elif data == 'ip':
        await query.edit_message_text("🌐 *Escanear IP*\n\nEnvía la IP con el comando:\n`/ip <IP>`", parse_mode='Markdown')
    elif data == 'numero':
        await query.edit_message_text("📞 *Rastrear Número*\n\nEnvía el número con el comando:\n`/numero <número>`", parse_mode='Markdown')
    elif data == 'help':
        await query.edit_message_text("🤖 *Ayuda*\n\n/username <nombre>\n/ip <IP>\n/numero <número>\n/menu\n/help", parse_mode='Markdown')

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("username", username_cmd))
    app.add_handler(CommandHandler("ip", ip_cmd))
    app.add_handler(CommandHandler("numero", numero_cmd))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("🚀 Bot OSINT iniciado correctamente")
    app.run_polling()

if __name__ == '__main__':
    main()