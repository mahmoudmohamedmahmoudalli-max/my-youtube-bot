import os
import asyncio
import edge_tts
import requests

# جلب المفاتيح
GROQ_KEY = os.getenv("GROQ_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def run_bot():
    print("--- تشغيل الماكينة بأحدث موديل ---")
    try:
        # 1. طلب السكربت من Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.1-8b-instant", # ده الموديل الجديد الشغال
            "messages": [{"role": "user", "content": "اكتب حقيقة علمية مذهلة في سطر واحد فقط باللغة العربية"}]
        }
        
        res = requests.post(url, headers=headers, json=data)
        
        if res.status_code != 200:
            print(f"❌ Error: {res.text}")
            return

        script = res.json()['choices'][0]['message']['content']
        print(f"📜 السكربت: {script}")

        # 2. تحويل الصوت
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("voice.mp3")

        # 3. إرسال لتلجرام
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": f"✅ أخيراً! اشتغلت يا محمود!\n\n📜 النص: {script}"})
        print("✅ تم الإرسال")

    except Exception as e:
        print(f"❌ خطأ: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_bot())
