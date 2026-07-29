import os
import asyncio
import edge_tts
import requests
import subprocess

# جلب المفاتيح
GROQ_KEY = os.getenv("GROQ_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_tg(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    res = requests.post(url, data={"chat_id": TG_CHAT_ID, "text": msg})
    if res.status_code == 200:
        print("✅ تم الإرسال لتلجرام بنجاح!")
    else:
        print(f"❌ فشل الإرسال: {res.text}")

async def run_factory():
    print("---بدء التشغيل---")
    try:
        # 1. السكربت
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "اكتب حقيقة علمية مذهلة عن الفضاء في سطر واحد بالعربي"}]}
        res = requests.post(url, headers=headers, json=data)
        script = res.json()['choices'][0]['message']['content']
        print(f"📜 السكربت: {script}")

        # 2. الصوت
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("audio.mp3")

        # 3. إرسال الرسالة (جرب نبعت النص الأول)
        send_tg(f"✅ الماكينة نجحت يا محمود!\n📜 النص: {script}")

    except Exception as e:
        print(f"❌ عطل: {str(e)}")
        # محاولة إرسال الإيرور برضه
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      data={"chat_id": TG_CHAT_ID, "text": f"❌ عطل: {str(e)}"})

if __name__ == "__main__":
    asyncio.run(run_factory())
