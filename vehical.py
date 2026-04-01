#!/usr/bin/env python3
# C2H Vehicle Info Bot - v6
# Powered by Click 2 Hack vehicle osint

import telebot
import requests
import json
import time
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode

# --- बॉट और API की जानकारी ---
BOT_TOKEN = "8721553020:AAGUkfdqJsWcHj3yO0u4PPufNj3_b33C_Pc"
API_BASE = "https://vehicleinfobyterabaap.vercel.app/lookup"
CHANNEL_USERNAME = "@Click2Hackk"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# --- HTTP सर्वर (Render के लिए पोर्ट) ---
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheck)
    server.serve_forever()

# --- चैनल जॉइन चेक ---
def is_user_joined_channel(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

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
            return None, data.get("error", "API से अज्ञात त्रुटि।")
        return data, None
    except requests.exceptions.RequestException as e:
        return None, f"API से कनेक्ट करने में त्रुटि: {e}"
    except json.JSONDecodeError:
        return None, "API से अमान्य प्रतिक्रिया मिली।"

# --- कमांड हैंडलर ---
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not is_user_joined_channel(user_id):
        welcome_text = (
            "╔═══════════════════════════╗\n"
            "     🔥 𝗖𝗟𝗜𝗖𝗞 𝟮 𝗛𝗔𝗖𝗞 🔥              \n"
            "    🚗 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧 🚗         \n"
            "╚═══════════════════════════╝\n\n"
            "<b>⚠️ आपने हमारा चैनल जॉइन नहीं किया है!</b>\n\n"
            "कृपया पहले हमारा चैनल जॉइन करें:\n"
            f"👉 {CHANNEL_USERNAME}\n\n"
            "<b>चैनल जॉइन करने के बाद /start कमांड दोबारा भेजें।</b>"
        )
        bot.reply_to(message, welcome_text)
        return
    
    welcome_text = (
        "╔═══════════════════════════╗\n"
        "     🔥 𝗖𝗟𝗜𝗖𝗞 𝟮 𝗛𝗔𝗖𝗞 🔥              \n"
        "    🚗 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧 🚗         \n"
        "╚═══════════════════════════╝\n\n"
        "<b>SEND YOUR VEHICLE NUMBER</b>\n"
        "<i>Example: UP70GB3954</i>"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_vehicle_number(message):
    user_id = message.from_user.id
    
    if not is_user_joined_channel(user_id):
        not_joined_text = (
            "╔═══════════════════════════╗\n"
            "     🔥 𝗖𝗟𝗜𝗖𝗞 𝟮 𝗛𝗔𝗖𝗞 🔥              \n"
            "    🚗 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧 🚗         \n"
            "╚═══════════════════════════╝\n\n"
            "<b>⚠️ आपने हमारा चैनल जॉइन नहीं किया है!</b>\n\n"
            "कृपया पहले हमारा चैनल जॉइन करें:\n"
            f"👉 {CHANNEL_USERNAME}\n\n"
            "<b>चैनल जॉइन करने के बाद /start कमांड दोबारा भेजें।</b>"
        )
        bot.reply_to(message, not_joined_text)
        return
    
    vehicle_number = message.text.strip().upper()
    
    processing_msg = bot.reply_to(message, "<code>⏳ Processing... Please wait ⏳</code>")
    time.sleep(2)

    info, error = fetch_vehicle_data(vehicle_number)

    if error:
        error_text = f"<b>❌ ERROR ❌</b>\n\n<pre>{error}</pre>"
        bot.edit_message_text(chat_id=processing_msg.chat.id, message_id=processing_msg.message_id, text=error_text)
        return

    if info:
        header = (
            "╔═══════════════════════════╗\n"
            "   🔥 𝗖𝗟𝗜𝗖𝗞 𝟮 𝗛𝗔𝗖𝗞 🔥              \n"
            "   🚗 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧 🚗        \n"
            "╚═══════════════════════════╝\n\n"
        )
        
        details_text = ""
        
        field_order = [
            "ownerName", "registrationNumber", "vehicleClass", "chassisNumber",
            "engineNumber", "fuelType", "manufacturerModel", "manufacturerYear",
            "insuranceValidity", "fitnessValidity", "taxValidity", "pucValidity",
            "state", "district", "city", "status"
        ]
        
        for field in field_order:
            if field in info and info[field] and info[field] != "NA":
                pretty_field = field.replace("_", " ").title()
                value_str = str(info[field])
                details_text += f"<b>{pretty_field}</b> : {value_str}\n\n"
        
        for field, value in info.items():
            if field.lower() == 'copyright':
                continue
            if field not in field_order and value and value != "NA":
                pretty_field = field.replace("_", " ").title()
                value_str = str(value)
                details_text += f"<b>{pretty_field}</b> : {value_str}\n\n"
        
        details_text += f"<b>Searched Number</b> : {vehicle_number}\n\n"
        
        footer = (
            "╔═══════════════════════════╗\n"
            "   🔥 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆 𝗖𝗹𝗶𝗰𝗸 𝟮 𝗛𝗮𝗰𝗸 🔥   \n"
            "            🔥 @Click2Hackk 🔥      \n"
            "╚═══════════════════════════╝"
        )

        final_message = header + details_text + footer
        
        bot.edit_message_text(chat_id=processing_msg.chat.id, message_id=processing_msg.message_id, text=final_message)
    else:
        no_info_text = (
            "╔════════════════════════════╗\n"
            "   ❌ 𝗡𝗢 𝗗𝗔𝗧𝗔 𝗙𝗢𝗨𝗡𝗗 ❌          \n"
            "╚═════════════════════════════╝\n\n"
            "No information found for this vehicle number."
        )
        bot.edit_message_text(chat_id=processing_msg.chat.id, message_id=processing_msg.message_id, text=no_info_text)

# --- बॉट को शुरू करें ---
if __name__ == "__main__":
    # HTTP सर्वर अलग थ्रेड में चलाओ
    threading.Thread(target=run_http_server, daemon=True).start()
    
    print("🚀 Click 2 Hack Vehicle Info Bot शुरू हो रहा है...")
    print("✅ Powered by Click 2 Hack vehicle osint")
    print(f"✅ Channel Check: {CHANNEL_USERNAME}")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ बॉट बंद हो गया: {e}")
    print("🛑 बॉट बंद हो गया है。")
