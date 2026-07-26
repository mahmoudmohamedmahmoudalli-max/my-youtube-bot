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

async def create_video():
    try:
        # 1. السكربت من Groq
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "اكتب حقيقة مذهلة عن الفضاء في سطر واحد بالعربي"}]}
        res = requests.post(url, headers=headers, json=data)
        script = res.json()['choices'][0]['message']['content']

        # 2. تحويل الصوت
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural")
        await communicate.save("audio.mp3")

        # 3. تحميل فيديو من Pexels
        pex_url = f"https://api.pexels.com/videos/search?query=space&per_page=1&orientation=portrait"
        pex_res = requests.get(pex_url, headers={"Authorization": PEXELS_KEY}).json()
        vid_link = pex_res['videos'][0]['video_files'][0]['link']
        with open("video_bg.mp4", "wb") as f:
            f.write(requests.get(vid_link).content)

        # 4. دمج الصوت مع الفيديو (صناعة الفيلم)
        video_clip = VideoFileClip("video_bg.mp4")
        audio_clip = AudioFileClip("audio.mp3")
        final_video = video_clip.set_audio(audio_clip).set_duration(audio_clip.duration)
        final_video.write_videofile("final_short.mp4", codec="libx264", audio_codec="aac", fps=24)

        # 5. إرسال إشعار لتلجرام
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                      data={"chat_id": TG_CHAT_ID, "text": f"✅ الفيديو جاهز يا محمود!\n📜 النص: {script}"})
        
        return "final_short.mp4"

    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={"chat_id": TG_CHAT_ID, "text": f"❌ خطأ: {str(e)}"})

if __name__ == "__main__":
    asyncio.run(create_video())
