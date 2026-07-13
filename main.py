import os
import asyncio
import edge_tts
import requests

# جلب المفاتيح
GROQ_KEY = os.getenv("GROQ_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def run_bot():
    print("--- كشف أعطال الماكينة ---")
    try:
        # 1. طلب السكربت
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama3-8b-8192", # غيرنا الموديل لواحد أخف وأسرع
            "messages": [{"role": "user", "content": "اكتب حقيقة علمية مذهلة في سطر واحد فقط باللغة العربية"}]
        }
        
        res = requests.post(url, headers=headers, json=data)
        
        # لو النتيجة مش 200 (يعني فيه غلط)
        if res.status_code != 200:
            error_detail = f"❌ Groq Error {res.status_code}: {res.text}"
            print(error_detail)
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          data={"chat_id": TG_CHAT_ID, "text": f"⚠️ تنبيه من الماكينة:\nالموقع رافض يشتغل والسبب:\n{res.text[:200]}"})
            return

        # لو النتيجة صح، كمل
        script = res.json()['choices'][0]['message']['content']
        print(f"📜 السكربت: {script}")

        # 2. تحويل الصوت
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("voice.mp3")

        # 3. إرسال لتلجرام
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": f"✅ مبروك! اشتغلت أخيراً!\n\n📜 النص: {script}"})
        print("✅ نجاح")

    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      data={"chat_id": TG_CHAT_ID, "text": f"❌ عطل فني: {str(e)}"})

if __name__ == "__main__":
    asyncio.run(run_bot())
