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
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  data={"chat_id": TG_CHAT_ID, "text": msg})

async def run_factory():
    try:
        # 1. السكربت
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "اكتب حقيقة علمية مذهلة عن الفضاء في سطر واحد بالعربي"}]}
        res = requests.post(url, headers=headers, json=data)
        script = res.json()['choices'][0]['message']['content']

        # 2. الصوت
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("audio.mp3")

        # 3. الفيديو من Pexels
        pex_url = f"https://api.pexels.com/videos/search?query=space&per_page=1&orientation=portrait"
        pex_res = requests.get(pex_url, headers={"Authorization": PEXELS_KEY}).json()
        vid_link = pex_res['videos'][0]['video_files'][0]['link']
        with open("video_bg.mp4", "wb") as f:
            f.write(requests.get(vid_link).content)

        # 4. دمج الفيديو بالصوت باستخدام FFmpeg مباشرة (أضمن طريقة)
        cmd = "ffmpeg -i video_bg.mp4 -i audio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest final.mp4 -y"
        subprocess.run(cmd, shell=True)

        send_tg(f"✅ مبروك يا محمود! الماكينة صنعت فيديو كامل بنجاح!\n📜 السكربت: {script}")

    except Exception as e:
        send_tg(f"❌ عطل تقني: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_factory())
