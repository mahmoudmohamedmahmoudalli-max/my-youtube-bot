import os
import asyncio
import edge_tts
import requests
import google.generativeai as genai

# جلب المفاتيح من الخزنة اللي إنت عملتها
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def run_bot():
    try:
        # 1. توليد سكربت بـ Gemini
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-pro')
        prompt = "اكتب لي حقيقة مذهلة وقصيرة جداً عن عجائب العالم القديم باللغة العربية المشوقة في سطر واحد فقط."
        response = model.generate_content(prompt)
        script = response.text

        # 2. تحويل السكربت لصوت مصري (شاكر)
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("voice.mp3")

        # 3. إرسال إشعار لتلجرام
        message = f"🚀 الماكينة اشتغلت بنجاح!\n\n📜 النص: {script}\n\n📢 تم تجهيز الصوت بنجاح، الفيديو القادم في الطريق!"
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      data={"chat_id": TG_CHAT_ID, "text": message})
        print("Success!")
    except Exception as e:
        # لو حصلت مشكلة هيبعتلك على تلجرام
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      data={"chat_id": TG_CHAT_ID, "text": f"❌ Error: {str(e)}"})

if __name__ == "__main__":
    asyncio.run(run_bot())
