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

async def run_tiktok_viral():
    try:
        # 1. تأليف قصة طويلة (الجزء الأول) بأسلوب تيك توك
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        
        # برومبت مخصص للقصص الطويلة والأجزاء
        prompt = (
            "اكتب الجزء الأول من قصة رعب حقيقية غامضة. "
            "ابدأ بـ 'في سر غامض محدش عرف يفسره لحد النهاردة..'. "
            "اجعل الأسلوب باللهجة المصرية المشوقة (زي فيديوهات تيك توك). "
            "القصة يجب أن تكون طويلة (حوالي 150 كلمة). "
            "أنهِ الفيديو بكلمة: (عشان تعرفوا اللي حصل في الجزء التاني، لايك وفولو)."
        )
        
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}]}
        res = requests.post(url, headers=headers, json=data)
        script = res.json()['choices'][0]['message']['content']

        # 2. تحويل الصوت (شاكر المصري)
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural", rate="-2%")
        await communicate.save("audio.mp3")

        # 3. تحميل خلفية "Satisfying" (زي اللي في تيك توك)
        pex_queries = ["parkour", "satisfying", "abstract", "skating"]
        query = random.choice(pex_queries)
        pex_url = f"https://api.pexels.com/videos/search?query={query}&per_page=1&orientation=portrait"
        pex_res = requests.get(pex_url, headers={"Authorization": PEXELS_KEY}).json()
        vid_link = pex_res['videos'][0]['video_files'][0]['link']
        with open("bg.mp4", "wb") as f:
            f.write(requests.get(vid_link).content)

        # 4. المونتاج ودمج الصوت + كتابة "الجزء الأول" (Watermark)
        # هنستخدم FFmpeg لإضافة نص "الجزء 1" في نص الفيديو
        draw_text = "drawtext=text='Part 1 - الجزء الأول':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2+200:box=1:boxcolor=black@0.5:boxborderw=5"
        cmd = f"ffmpeg -stream_loop -1 -i bg.mp4 -i audio.mp3 -vf \"{draw_text}\" -map 0:v:0 -map 1:a:0 -c:a aac -shortest final.mp4 -y"
        subprocess.run(cmd, shell=True)

        # 5. الإرسال لتلجرام
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendVideo"
        with open("final.mp4", 'rb') as video:
            requests.post(tg_url, files={'video': video}, data={'chat_id': TG_CHAT_ID, 'caption': f"🔥 فيديو قصة - الجزء 1\n\n#قصص #رعب #fyp"})

    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", data={"chat_id": TG_CHAT_ID, "text": f"❌ عطل: {str(e)}"})

if __name__ == "__main__":
    asyncio.run(run_tiktok_viral())
