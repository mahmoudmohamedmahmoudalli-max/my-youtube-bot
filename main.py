import os
import asyncio
import edge_tts
import requests

# جلب المفاتيح من الخزنة
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def run_bot():
    print("--- بدء التشغيل وكشف الأعطال ---")
    try:
        # 1. طلب السكربت من جوجل Gemini
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {
            "contents": [{
                "parts": [{"text": "اكتب حقيقة علمية مذهلة عن الفضاء في سطر واحد"}]
            }]
        }
        
        res = requests.post(gemini_url, json=payload)
        data = res.json()

        # كاشف الأعطال: لو جوجل ردت بغلط
        if 'error' in data:
            error_text = f"❌ جوجل بتقول فيه غلط في المفتاح: {data['error']['message']}"
            print(error_text)
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={"chat_id": TG_CHAT_ID, "text": error_text})
            return

        # لو مفيش غلط، كمل عادي
        script = data['candidates'][0]['content']['parts'][0]['text']
        print(f"📜 النص: {script}")

        # 2. تحويل النص لصوت
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("voice.mp3")

        # 3. إرسال الرسالة لتلجرام
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": f"✅ الماكينة نجحت!\n\n📜 النص: {script}"})
        print("✅ تم الإرسال")

    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={"chat_id": TG_CHAT_ID, "text": f"❌ عطل تقني: {str(e)}"})

if __name__ == "__main__":
    asyncio.run(run_bot())
