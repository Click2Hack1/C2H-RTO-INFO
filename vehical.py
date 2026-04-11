#!/usr/bin/env python3
# C2H Vehicle Info Bot - WITH BOTH CHANNELS (FIXED)
# Powered by Click 2 Hack

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
BOT_TOKEN = "8692231051:AAGwosn7l4LcFauTlM63OTrMhC8HojgmUtE"   # अपना टोकन
API_BASE = "https://vehicleinfobyterabaap.vercel.app/lookup"

# 📢 दोनों चैनल – पुराना + Backup
CHANNELS = ["@Click2Hackk", "@c2hget"]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

bot_running = True
last_activity = datetime.now()

# --- चैनल जॉइन चेक ---
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

# --- API से डेटा लेना (DEBUG ENABLED) ---
def fetch_vehicle_data(rc):
    params = {"rc": rc}
    url = f"{API_BASE}?{urlencode(params)}"
    print(f"[DEBUG] Request URL: {url}")
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "FirewallBreaker/PRO"})
        print(f"[DEBUG] Status Code: {resp.status_code}")
        print(f"[DEBUG] Response Text: {resp.text[:500]}")
        resp.raise_for_status()
        data = resp.json()
        print(f"[DEBUG] JSON Data: {json.dumps(data, indent=2)[:1000]}")
        if "error" in data:
            return None, data.get("error")
        if not data or len(data) == 0:
            return None, "No data found for this vehicle number"
        return data, None
    except Exception as e:
        print(f"[DEBUG] Exception: {e}")
        return None, str(e)

# --- कमांड हैंडलर ---
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    global last_activity
    last_activity = datetime.now()
    user_id = message.from_user.id
    
    if not is_joined(user_id):
        text = "🚫 कृपया *दोनों* चैनल जॉइन करें:\n\n"
        for ch in CHANNELS:
            text += f"👉 https://t.me/{ch.replace('@','')}\n"
        text += "\n✅ दोनों जॉइन करने के बाद /start दोबारा भेजें।"
        return bot.reply_to(message, text, parse_mode='Markdown')
    
    welcome_text = (
        "╔═══════════════════════════╗\n"
        "     🔥 𝗖𝗟𝗜𝗖𝗞 𝟮 𝗛𝗔𝗖𝗞 🔥              \n"
        "    🚗 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧 🚗         \n"
        "╚═══════════════════════════╝\n\n"
        "✅ स्वागत है!\n\n"
        "📱 SEND YOUR VEHICLE NUMBER\n"
        "Example: UP70GD5514"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_vehicle_number(message):
    global last_activity
    last_activity = datetime.now()
    user_id = message.from_user.id
    
    # Agar command hai to ignore karo
    if message.text.startswith('/'):
        return
    
    if not is_joined(user_id):
        text = "🚫 पहले *दोनों* चैनल जॉइन करें! /start भेजें"
        return bot.reply_to(message, text, parse_mode='Markdown')
    
    vehicle_number = message.text.strip().upper()
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Sending "processing" message
    status_msg = bot.reply_to(message, "⏳ Fetching vehicle information...")
    
    info, error = fetch_vehicle_data(vehicle_number)

    if error:
        bot.edit_message_text(f"❌ ERROR: {error}\n\nPlease try again with a valid vehicle number.", 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id)
        return

    if info and isinstance(info, dict):
        header = "🔥 *ᴄʟɪᴄᴋ 𝟸 ʜᴀᴄᴋ* 🔥\n╔════════════════════╗\n     🚗 *ᴠᴇʜɪᴄʟᴇ ɪɴғᴏ* 🚗\n╚════════════════════╝\n\n"
        details = "📋 *वाहन डिटेल्स* \n━━━━━━━━━━━━━━━━━━\n"
        
        # Field mapping - display name : API field name
        fields = [
            ("👤 मालिक का नाम", "ownerName"),
            ("🔢 रजिस्ट्रेशन नंबर", "registrationNumber"),
            ("🚗 वाहन का प्रकार", "vehicleClass"),
            ("🔧 चेसिस नंबर", "chassisNumber"),
            ("⚙️ इंजन नंबर", "engineNumber"),
            ("⛽ ईंधन प्रकार", "fuelType"),
            ("🏭 मॉडल", "manufacturerModel"),
            ("📅 निर्माण वर्ष", "manufacturerYear"),
            ("📝 बीमा वैधता", "insuranceValidity"),
            ("💪 फिटनेस वैधता", "fitnessValidity"),
            ("💰 टैक्स वैधता", "taxValidity"),
            ("🌿 PUC वैधता", "pucValidity"),
            ("📍 राज्य", "state"),
            ("🏘️ जिला", "district"),
            ("🌆 शहर", "city"),
            ("📊 स्थिति", "status")
        ]
        
        count = 0
        for display_name, field_name in fields:
            value = info.get(field_name)
            if value and value != "NA" and str(value).strip():
                details += f"{display_name} : {value}\n"
                count += 1
        
        # Agar koi field nahi mili to saara raw data dikhao
        if count == 0:
            details += "⚠️ *No detailed fields found. Raw data:* ⚠️\n"
            for key, val in info.items():
                if val and val != "NA" and key.lower() != "copyright":
                    details += f"📌 {key} : {val}\n"
        
        details += f"\n🔍 *खोजा गया नंबर* : {vehicle_number}\n"
        
        footer = "\n╔════════════════════╗\n   🔥 *@Click2Hackk* 🔥\n   👑 *ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴄʟɪᴄᴋ 𝟸 ʜᴀᴄᴋ* 👑\n╚════════════════════╝"
        
        bot.edit_message_text(header + details + footer, 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id,
                              parse_mode='Markdown')
    else:
        bot.edit_message_text("❌ वाहन नंबर के लिए कोई जानकारी नहीं मिली!\n\nPlease check the number and try again.", 
                              chat_id=message.chat.id, 
                              message_id=status_msg.message_id)

# --- Flask Routes ---
@app.route('/')
def home():
    return {"status": "Vehicle Info Bot running with BOTH channels", "channels": CHANNELS}, 200

@app.route('/health')
def health():
    return {"status": "healthy", "bot_running": bot_running}, 200

def run_bot_polling():
    global bot_running
    while bot_running:
        try:
            print("🔄 Vehicle Info Bot polling started...")
            bot.remove_webhook()
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"❌ Polling error: {e}")
            if bot_running:
                time.sleep(10)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("="*50)
    print("🚗 C2H VEHICLE INFO BOT - BOTH CHANNELS (FIXED)")
    print("="*50)
    print(f"Channels: {CHANNELS}")
    print(f"Port: {port}")
    print("="*50)
    
    threading.Thread(target=run_bot_polling, daemon=True).start()
    app.run(host="0.0.0.0", port=port)
