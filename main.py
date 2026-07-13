import os
import asyncio
import edge_tts
import requests

# جلب المفاتيح من الخزنة
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def run_bot():
    print("---بدء التشغيل---")
    try:
        # 1. طلب السكربت من جوجل Gemini برابط مباشر
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": "اكتب حقيقة علمية مذهلة وسريعة عن الفضاء باللغة العربية في سطر واحد فقط"}]
            }]
        }
        res = requests.post(gemini_url, json=payload)
        script = res.json()['candidates'][0]['content']['parts'][0]['text']
        print(f"📜 النص: {script}")

        # 2. تحويل النص لصوت
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("voice.mp3")
        print("🔊 تم تجهيز الصوت")

        # 3. إرسال الرسالة لتلجرام
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": f"✅ الماكينة اشتغلت!\n\n📜 النص: {script}"})
        print("✅ تم الإرسال لتلجرام")

    except Exception as e:
        error_msg = f"❌ حصلت مشكلة: {str(e)}"
        print(error_msg)
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      data={"chat_id": TG_CHAT_ID, "text": error_msg})

if __name__ == "__main__":
    asyncio.run(run_bot())
