#!/usr/bin/env python3
# C2H Vehicle Info Bot - v7 (Cron-Job Fix)
# Powered by Click 2 Hack vehicle osint

import telebot
import requests
import json
import time
from urllib.parse import urlencode
# --- वेब सर्विस के लिए ज़रूरी चीजें ---
import os
from flask import Flask, Response  # Response को यहाँ इम्पोर्ट करें
from threading import Thread
# ------------------------------------

# --- बॉट और API की जानकारी ---
BOT_TOKEN = "8721553020:AAGUkfdqJsWcHj3yO0u4PPufNj3_b33C_Pc"
API_BASE = "https://vehicleinfobyterabaap.vercel.app/lookup"
CHANNEL_USERNAME = "@Click2Hackk"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- वेब सर्विस को जिंदा रखने के लिए सर्वर ---
app = Flask(__name__)

@app.route('/')
def index():
    # --- यहाँ बदलाव किया गया है ---
    # अब यह कोई टेक्स्ट नहीं भेजेगा, सिर्फ एक खाली 'OK' (200) रिस्पॉन्स देगा।
    return Response(status=200)

def run_web_server():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
# -------------------------------------------

# --- बाकी का पूरा कोड बिल्कुल वैसा ही रहेगा जैसा पहले था ---

# --- चैनल जॉइन चेक करने का फंक्शन ---
def is_user_joined_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# --- मुख्य लॉजिक ---
def fetch_vehicle_data(rc):
    params = {"rc": rc}
    url = f"{API_BASE}?{urlencode(params)}"
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "FirewallBreaker/PRO (by thakur2309)"})
        resp.raise_for_status()
        data = resp.json()
        return (data, None) if "error" not in data else (None, data.get("error", "API से अज्ञात त्रुटि।"))
    except requests.exceptions.RequestException as e:
        return None, f"API से कनेक्ट करने में त्रुटि: {e}"
    except json.JSONDecodeError:
        return None, "API से अमान्य प्रतिक्रिया मिली।"

# --- टेलीग्राम बॉट के कमांड हैंडलर ---
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    user_id = message.from_user.id
    if not is_user_joined_channel(user_id):
        bot.reply_to(message, f"<b>⚠️ आपने हमारा चैनल जॉइन नहीं किया है!</b>\n\nकृपया पहले हमारा चैनल जॉइन करें:\n👉 {CHANNEL_USERNAME}\n\n<b>चैनल जॉइन करने के बाद /start कमांड दोबारा भेजें।</b>")
        return
    bot.reply_to(message, "╔═══════════════════════════╗\n     🔥 𝗖𝗟𝗜𝗖𝗞 𝟮 𝗛𝗔𝗖𝗞 🔥              \n    🚗 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧 🚗         \n╚═══════════════════════════╝\n\n<b>SEND YOUR VEHICLE NUMBER</b>\n<i>Example: UP70GB3954</i>")

@bot.message_handler(func=lambda message: True)
def handle_vehicle_number(message):
    user_id = message.from_user.id
    if not is_user_joined_channel(user_id):
        bot.reply_to(message, f"<b>⚠️ आपने हमारा चैनल जॉइन नहीं किया है!</b>\n\nकृपया पहले हमारा चैनल जॉइन करें:\n👉 {CHANNEL_USERNAME}\n\n<b>चैनल जॉइन करने के बाद /start कमांड दोबारा भेजें।</b>")
        return
    
    vehicle_number = message.text.strip().upper()
    processing_msg = bot.reply_to(message, "<code>⏳ Processing... Please wait ⏳</code>")
    time.sleep(2)

    info, error = fetch_vehicle_data(vehicle_number)

    if error:
        bot.edit_message_text(f"<b>❌ ERROR ❌</b>\n\n<pre>{error}</pre>", chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)
        return

    if info:
        header = "╔═══════════════════════════╗\n   🔥 𝗖𝗟𝗜𝗖𝗞 𝟮 𝗛𝗔𝗖𝗞 🔥              \n   🚗 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧 🚗        \n╚═══════════════════════════╝\n\n"
        details_text = ""
        field_order = ["ownerName", "registrationNumber", "vehicleClass", "chassisNumber", "engineNumber", "fuelType", "manufacturerModel", "manufacturerYear", "insuranceValidity", "fitnessValidity", "taxValidity", "pucValidity", "state", "district", "city", "status"]
        
        for field in field_order:
            if field in info and info[field] and info[field] != "NA":
                details_text += f"<b>{field.replace('_', ' ').title()}</b> : {info[field]}\n\n"
        
        for field, value in info.items():
            if field.lower() != 'copyright' and field not in field_order and value and value != "NA":
                details_text += f"<b>{field.replace('_', ' ').title()}</b> : {value}\n\n"
        
        details_text += f"<b>Searched Number</b> : {vehicle_number}\n\n"
        footer = "╔═══════════════════════════╗\n   🔥 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆 𝗖𝗹𝗶𝗰𝗸 𝟮 𝗛𝗮𝗰𝗸 🔥   \n            🔥 @Click2Hackk 🔥      \n╚═══════════════════════════╝"
        
        bot.edit_message_text(header + details_text + footer, chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)
    else:
        bot.edit_message_text("╔════════════════════════════╗\n   ❌ 𝗡𝗢 𝗗𝗔𝗧𝗔 𝗙𝗢𝗨𝗡𝗗 ❌          \n╚═════════════════════════════╝\n\nNo information found for this vehicle number.", chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)

# --- बॉट को शुरू करें ---
if __name__ == "__main__":
    print("🚀 Click 2 Hack Vehicle Info Bot शुरू हो रहा है...")
    web_thread = Thread(target=run_web_server)
    web_thread.start()
    
    print("✅ Bot polling शुरू हो रहा है...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ बॉट बंद हो गया: {e}")
    print("🛑 बॉट बंद हो गया है।")
