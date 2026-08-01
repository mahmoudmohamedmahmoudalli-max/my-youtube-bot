import os
import asyncio
import edge_tts
import requests
import subprocess
import random

# جلب المفاتيح
GROQ_KEY = os.getenv("GROQ_API_KEY")
PEXELS_KEY = os.getenv("PEXELS_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def run_tiktok_bot():
    print("--- 🎬 تشغيل ماكينة قصص تيك توك ---")
    try:
        # 1. السكربت (قصة مشوقة أجزاء)
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        prompt = "اكتب قصة مشوقة جداً ومرعبة (الجزء الأول) في سطرين طوال باللغة العربية، تنتهي بقفلة تخلي الناس تطلب الجزء التاني."
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}]}
        
        res = requests.post(url, headers=headers, json=data)
        script = res.json()['choices'][0]['message']['content']
        print(f"📜 القصة: {script}")

        # 2. تحويل الصوت
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural", rate="+0%")
        await communicate.save("audio.mp3")

        # 3. فيديو الخلفية (Pexels) - هنحمل فيديو واحد جودته عالية
        pex_url = f"https://api.pexels.com/videos/search?query=mystery&per_page=1&orientation=portrait"
        pex_res = requests.get(pex_url, headers={"Authorization": PEXELS_KEY}).json()
        vid_link = pex_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f:
            f.write(requests.get(vid_link).content)

        # 4. المونتاج (FFmpeg)
        # الأمر ده بيطول الفيديو عشان يناسب الصوت وبيركبهم مع بعض
        cmd = "ffmpeg -stream_loop -1 -i bg.mp4 -i audio.mp3 -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest final.mp4 -y"
        subprocess.run(cmd, shell=True)

        # 5. الإرسال لتلجرام مع الهاشتاجات
        hashtags = "\n\n#قصص #رعب #تيك_توك #fyp #viral"
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendVideo"
        with open("final.mp4", 'rb') as video:
            requests.post(tg_url, files={'video': video}, data={'chat_id': TG_CHAT_ID, 'caption': f"🎬 الجزء الأول جاهز!\n\n{script[:150]}...{hashtags}"})
        
        print("✅ تم بنجاح!")

    except Exception as e:
        print(f"❌ عطل: {str(e)}")
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={"chat_id": TG_CHAT_ID, "text": f"❌ عطل: {str(e)}"})

if __name__ == "__main__":
    asyncio.run(run_tiktok_bot())
