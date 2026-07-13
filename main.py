import os
import asyncio
import edge_tts
import requests

# جلب المفاتيح من الخزنة
GROQ_KEY = os.getenv("GROQ_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def run_bot():
    print("--- تشغيل الماكينة بنظام Groq ---")
    try:
        # 1. طلب السكربت من Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": "اكتب حقيقة علمية مذهلة عن عجائب الطبيعة في سطر واحد فقط باللغة العربية المشوقة"}]
        }
        res = requests.post(url, headers=headers, json=data)
        script = res.json()['choices'][0]['message']['content']
        print(f"📜 السكربت: {script}")

        # 2. تحويل السكربت لصوت مصري
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("voice.mp3")

        # 3. إرسال الرسالة النهائية لتلجرام
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        final_msg = f"✅ مبروك يا محمود! الماكينة نجحت!\n\n📜 النص: {script}\n\n🔊 تم تجهيز الصوت بنجاح."
        requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": final_msg})
        print("✅ تم الإرسال بنجاح")

    except Exception as e:
        error_msg = f"❌ حصلت مشكلة تقنية: {str(e)}"
        print(error_msg)
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={"chat_id": TG_CHAT_ID, "text": error_msg})

if __name__ == "__main__":
    asyncio.run(run_bot())
