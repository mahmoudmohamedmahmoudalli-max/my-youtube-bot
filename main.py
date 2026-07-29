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

async def run_viral_factory():
    print("--- 🎬 بدء صناعة فيديو احترافي ---")
    try:
        # 1. توليد سكربت طويل مع "هوك" قوي
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        prompt = (
            "اكتب سكربت فيديو يوتيوب شورتس عن معلومة غريبة جداً في الفضاء. "
            "لازم يبدأ بجملة صادمة (هوك) في أول 3 ثواني. "
            "السكربت لازم يكون طويل شوية (حوالي 60 لـ 80 كلمة) عشان يوصل لـ 40 ثانية. "
            "استخدم لغة عربية مشوقة جداً."
        )
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}]}
        res = requests.post(url, headers=headers, json=data)
        script = res.json()['choices'][0]['message']['content']
        print(f"📜 السكربت الطويل: {script}")

        # 2. تحويل الصوت (بسرعة طبيعية)
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural", rate="-5%") # أبطأ قليلاً لزيادة المشوقة
        await communicate.save("audio.mp3")

        # 3. تحميل فيديو خلفية من Pexels
        pex_url = f"https://api.pexels.com/videos/search?query=galaxy&per_page=1&orientation=portrait"
        pex_res = requests.get(pex_url, headers={"Authorization": PEXELS_KEY}).json()
        vid_link = pex_res['videos'][0]['video_files'][0]['link']
        with open("video_bg.mp4", "wb") as f:
            f.write(requests.get(vid_link).content)

        # 4. دمج الصوت وتكرار الفيديو (Loop) عشان يناسب طول السكربت
        print("🎥 جاري دمج الفيديو وتطويله...")
        # الأمر ده بيخلي الفيديو يكرر نفسه لحد ما الصوت يخلص
        cmd = (
            "ffmpeg -stream_loop -1 -i video_bg.mp4 -i audio.mp3 "
            "-map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest final.mp4 -y"
        )
        subprocess.run(cmd, shell=True)

        # 5. الإرسال لتلجرام
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendVideo"
        with open("final.mp4", 'rb') as video:
            requests.post(tg_url, files={'video': video}, data={'chat_id': TG_CHAT_ID, 'caption': f"🔥 فيديو احترافي جديد!\n\n{script[:200]}..."})
        
        print("✅ تم تجهيز وإرسال الفيديو الطويل!")

    except Exception as e:
        print(f"❌ عطل: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_viral_factory())
