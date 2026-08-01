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

async def run_bot():
    print("--- بدء فحص الماكينة ---")
    try:
        # 1. اختبار المفاتيح أولاً
        if not GROQ_KEY or not PEXELS_KEY:
            raise Exception("فيه مفتاح ناقص في GitHub Secrets! اتأكد إنك ضفت GROQ_API_KEY و PEXELS_API_KEY")

        # 2. طلب السكربت
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "اكتب قصة رعب قصيرة جدا في سطر واحد"}]}
        res = requests.post(url, headers=headers, json=data)
        
        if res.status_code != 200:
            raise Exception(f"غلط في Groq: {res.text}")
        
        script = res.json()['choices'][0]['message']['content']

        # 3. تحويل الصوت
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("audio.mp3")

        # 4. فيديو بكسلز
        pex_url = f"https://api.pexels.com/videos/search?query=dark&per_page=1"
        pex_res = requests.get(pex_url, headers={"Authorization": PEXELS_KEY}).json()
        
        if 'videos' not in pex_res:
            raise Exception("مفتاح Pexels غلط أو منتهي الصلاحية")
            
        vid_link = pex_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f:
            f.write(requests.get(vid_link).content)

        # 5. الدمج
        subprocess.run("ffmpeg -i bg.mp4 -i audio.mp3 -c:v copy -c:a aac -shortest final.mp4 -y", shell=True)

        # 6. الإرسال
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendVideo"
        with open("final.mp4", 'rb') as video:
            requests.post(tg_url, files={'video': video}, data={'chat_id': TG_CHAT_ID, 'caption': f"✅ اشتغلت!\n{script}"})

    except Exception as e:
        error_msg = f"❌ العطل هو: {str(e)}"
        print(error_msg)
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={"chat_id": TG_CHAT_ID, "text": error_msg})

if __name__ == "__main__":
    asyncio.run(run_bot())
