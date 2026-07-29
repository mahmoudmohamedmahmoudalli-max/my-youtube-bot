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

async def run_factory():
    print("--- 🕵️ بدء عملية التحقيق ---")
    try:
        # 1. السكربت
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "اكتب حقيقة علمية في سطر واحد بالعربي"}]}
        res = requests.post(url, headers=headers, json=data)
        script = res.json()['choices'][0]['message']['content']
        print(f"✅ السكربت جاهز: {script}")

        # 2. الصوت
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("audio.mp3")

        # 3. فيديو Pexels
        pex_url = f"https://api.pexels.com/videos/search?query=nature&per_page=1&orientation=portrait"
        pex_res = requests.get(pex_url, headers={"Authorization": PEXELS_KEY}).json()
        vid_link = pex_res['videos'][0]['video_files'][0]['link']
        with open("video_bg.mp4", "wb") as f:
            f.write(requests.get(vid_link).content)

        # 4. الدمج
        subprocess.run("ffmpeg -i video_bg.mp4 -i audio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest final.mp4 -y", shell=True)
        print("✅ الفيديو تم صنعه")

        # 5. التحقيق في الإرسال (أهم جزء)
        print("📤 جاري محاولة الإرسال لتلجرام...")
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendVideo"
        with open("final.mp4", 'rb') as video:
            r = requests.post(tg_url, files={'video': video}, data={'chat_id': TG_CHAT_ID, 'caption': "تجربة نهائية"})
        
        if r.status_code == 200:
            print("🚀 مبروك! تلجرام استلم الفيديو فعلاً!")
        else:
            print(f"❌ تلجرام رفض الرسالة! السبب: {r.text}")

    except Exception as e:
        print(f"💥 خطأ في الكود: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_factory())
