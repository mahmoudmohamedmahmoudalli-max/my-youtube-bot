import os
import asyncio
import edge_tts
import requests
from moviepy.editor import VideoFileClip, AudioFileClip

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
        print("💡 جاري تأليف السكربت...")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "اكتب حقيقة علمية مذهلة عن الفضاء في سطر واحد بالعربي"}]}
        res = requests.post(url, headers=headers, json=data)
        script = res.json()['choices'][0]['message']['content']
        print(f"✅ السكربت: {script}")

        # 2. الصوت
        print("🔊 جاري تحويل الصوت...")
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("audio.mp3")

        # 3. الفيديو
        print("🎬 جاري تحميل فيديو الخلفية...")
        pex_url = f"https://api.pexels.com/videos/search?query=space&per_page=1&orientation=portrait"
        pex_res = requests.get(pex_url, headers={"Authorization": PEXELS_KEY}).json()
        if 'videos' not in pex_res or not pex_res['videos']:
            raise Exception("فشل تحميل فيديو من Pexels - اتأكد من المفتاح")
        
        vid_link = pex_res['videos'][0]['video_files'][0]['link']
        with open("video_bg.mp4", "wb") as f:
            f.write(requests.get(vid_link).content)

        # 4. الدمج
        print("🎥 جاري دمج الصوت مع الفيديو...")
        video = VideoFileClip("video_bg.mp4")
        audio = AudioFileClip("audio.mp3")
        final = video.set_audio(audio).set_duration(audio.duration)
        final.write_videofile("final.mp4", codec="libx264", audio_codec="aac", fps=24, logger=None)

        send_tg(f"✅ مبروك يا محمود! الماكينة صنعت فيديو كامل بنجاح!\n📜 السكربت: {script}")
        print("🚀 نجاح باهر!")

    except Exception as e:
        error_msg = f"❌ الماكينة عطلت في خطوة معينة:\n{str(e)}"
        print(error_msg)
        send_tg(error_msg)

if __name__ == "__main__":
    asyncio.run(run_factory())
