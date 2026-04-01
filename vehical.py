#!/usr/bin/env python3
# C2H Vehicle Info Bot - Flask Version
# Powered by Click 2 Hack vehicle osint

import telebot
import requests
import json
import os
import time
import threading
from flask import Flask
from urllib.parse import urlencode
from datetime import datetime

# --- बॉट और API की जानकारी ---
BOT_TOKEN = "8721553020:AAGUkfdqJsWcHj3yO0u4PPufNj3_b33C_Pc"
API_BASE = "https://vehicleinfobyterabaap.vercel.app/lookup"
CHANNELS = ["@Click2Hackk"]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

bot_running = True
last_activity = datetime.now()

# --- चैनल जॉइन चेक (Number Info वाले जैसा) ---
def is_joined(user_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            print(f"Error checking channel {ch}: {e}")
            return False
    return True

# --- API से डेटा लेना ---
def fetch_vehicle_data(rc):
    params = {"rc": rc}
    url = f"{API_BASE}?{urlencode(params)}"
    try:
        resp = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "FirewallBreaker/PRO (by thakur2309)"},
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            return None, data.get("error")
        return data, None
    except Exception as e:
        return None, str(e)

# --- कमांड हैंडलर (Number Info वाले जैसा) ---
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    global last_activity
    last_activity = datetime.now()
    user_id = message.from_user.id
    
    if not is_joined(user_id):
        text = "🚫 कृपया पहले हमारा चैनल जॉइन करें:\n\n"
        for ch in CHANNELS:
            text += f"👉 https://t.me/{ch.replace('@','')}\n"
        text += "\n✅ जॉइन करने के बाद /start दोबारा भेजें।"
        return bot.reply_to(message, text)
    
    welcome_text = (
        "╔═══════════════════════════╗\n"
        "     🔥 𝗖𝗟𝗜𝗖𝗞 𝟮 𝗛𝗔𝗖𝗞 🔥              \n"
        "    🚗 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧 🚗         \n"
        "╚═══════════════════════════╝\n\n"
        "✅ स्वागत है!\n\n"
        "📱 SEND YOUR VEHICLE NUMBER\n"
        "Example: UP70GB3954"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_vehicle_number(message):
    global last_activity
    last_activity = datetime.now()
    user_id = message.from_user.id
    
    if not is_joined(user_id):
        text = "🚫 पहले चैनल जॉइन करें! /start भेजें"
        return bot.reply_to(message, text)
    
    vehicle_number = message.text.strip().upper()
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    info, error = fetch_vehicle_data(vehicle_number)

    if error:
        bot.reply_to(message, f"❌ ERROR: {error}")
        return

    if info:
        header = (
            "🔥 *ᴄʟɪᴄᴋ 𝟸 ʜᴀᴄᴋ* 🔥\n"
            "╔════════════════════╗\n"
            "     🚗 *ᴠᴇʜɪᴄʟᴇ ɪɴғᴏ* 🚗\n"
            "╚════════════════════╝\n\n"
        )
        
        details_text = "📋 *वाहन डिटेल्स* \n━━━━━━━━━━━━━━━━━━\n"
        
        field_order = [
            ("ownerName", "👤 मालिक का नाम"),
            ("registrationNumber", "🔢 रजिस्ट्रेशन नंबर"),
            ("vehicleClass", "🚗 वाहन का प्रकार"),
            ("chassisNumber", "🔧 चेसिस नंबर"),
            ("engineNumber", "⚙️ इंजन नंबर"),
            ("fuelType", "⛽ ईंधन प्रकार"),
            ("manufacturerModel", "🏭 मॉडल"),
            ("manufacturerYear", "📅 निर्माण वर्ष"),
            ("insuranceValidity", "📝 बीमा वैधता"),
            ("fitnessValidity", "💪 फिटनेस वैधता"),
            ("taxValidity", "💰 टैक्स वैधता"),
            ("pucValidity", "🌿 PUC वैधता"),
            ("state", "📍 राज्य"),
            ("district", "🏘️ जिला"),
            ("city", "🌆 शहर"),
            ("status", "📊 स्थिति")
        ]
        
        for field, display_name in field_order:
            if field in info and info[field] and info[field] != "NA":
                value_str = str(info[field])
                details_text += f"{display_name} : {value_str}\n"
        
        for field, value in info.items():
            if field.lower() == 'copyright':
                continue
            found = False
            for f, _ in field_order:
                if f == field:
                    found = True
                    break
            if not found and value and value != "NA":
                pretty_field = field.replace("_", " ").title()
                details_text += f"📌 {pretty_field} : {value}\n"
        
        details_text += f"\n🔍 *खोजा गया नंबर* : {vehicle_number}\n"
        
        footer = (
            "\n╔════════════════════╗\n"
            "   🔥 *@Click2Hackk* 🔥\n"
            "   👑 *ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʟɪᴄᴋ 𝟸 ʜᴀᴄᴋ* 👑\n"
            "╚════════════════════╝"
        )
        
        full_message = header + details_text + footer
        bot.reply_to(message, full_message, parse_mode='Markdown')
    else:
        bot.reply_to(message, "❌ वाहन नंबर के लिए कोई जानकारी नहीं मिली!")

# --- Flask Routes (Number Info वाले जैसा) ---
@app.route('/')
def home():
    return {
        "status": "Bot is running in polling mode",
        "message": "C2H Vehicle Info Bot is active on Telegram",
        "commands": ["/start", "/hello", "send vehicle number"],
        "channels": CHANNELS
    }, 200

@app.route('/health')
def health():
    return {"status": "healthy", "bot_running": bot_running}, 200

# --- बॉट पोलिंग थ्रेड (Number Info वाले जैसा) ---
def run_bot_polling():
    global bot_running
    while bot_running:
        try:
            print("🔄 Bot polling started...")
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"❌ Polling error: {e}")
            if bot_running:
                print("🔄 Restarting in 10 seconds...")
                time.sleep(10)

# --- बॉट शुरू करें ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    print("="*50)
    print("🚀 C2H Vehicle Info Bot Starting on Render")
    print("="*50)
    print(f"Bot Token: {BOT_TOKEN[:10]}...")
    print(f"Channels: {CHANNELS}")
    print(f"Port: {port}")
    print("="*50)
    
    # बॉट पोलिंग बैकग्राउंड थ्रेड में शुरू करो
    polling_thread = threading.Thread(target=run_bot_polling)
    polling_thread.daemon = True
    polling_thread.start()
    
    # Flask सर्वर शुरू करो
    print("🚀 Starting Flask server...")
    app.run(host="0.0.0.0", port=port)
