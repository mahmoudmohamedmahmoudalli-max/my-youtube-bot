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

async def run_story_factory():
    print("--- 📖 بدء صناعة قصة مشوقة (أجزاء) ---")
    try:
        # 1. توليد قصة مقسمة لأجزاء (سنطلب منه الجزء الأول مثلاً)
        # ملحوظة: يمكنك تغيير "القصة" هنا (رعب، خيال علمي، تاريخ)
        topic = random.choice(["رعب في الغابة", "سر اختفاء سفينة", "كنز مفقود في مصر", "مغامرة في كوكب غريب"])
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        prompt = (
            f"اكتب قصة مشوقة جداً عن '{topic}'. "
            "اريد منك كتابة 'الجزء الأول' فقط. "
            "ابدأ بـ 'الجزء الأول' وعنوان مثير. "
            "اجعل القصة تنتهي بـ 'Cliffhanger' (قفلة مشوقة) تجعل المشاهد ينتظر الجزء الثاني. "
            "السكربت يجب أن يكون طويلاً (حوالي 120 كلمة) ليكون الفيديو مدته دقيقة."
        )
        data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}]}
        res = requests.post(url, headers=headers, json=data)
        script = res.json()['choices'][0]['message']['content']
        print(f"📜 السكربت: {script}")

        # 2. تحويل الصوت (صوت شاكر المصري بطريقة قصصية)
        communicate = edge_tts.Communicate(script, "ar-EG-ShakirNeural", rate="-2%", pitch="-1Hz")
        await communicate.save("audio.mp3")

        # 3. تحميل 3 فيديوهات مختلفة من Pexels عشان التنوع
        query = random.choice(["dark forest", "mystery", "adventure", "cinematic"])
        pex_url = f"https://api.pexels.com/videos/search?query={query}&per_page=3&orientation=portrait"
        pex_res = requests.get(pex_url, headers={"Authorization": PEXELS_KEY}).json()
        
        video_files = []
        for i in range(3):
            vid_link = pex_res['videos'][i]['video_files'][0]['link']
            v_name = f"bg_{i}.mp4"
            with open(v_name, "wb") as f:
                f.write(requests.get(vid_link).content)
            video_files.append(v_name)

        # 4. دمج الـ 3 فيديوهات ثم ركيب الصوت عليهم
        print("🎥 جاري صناعة المونتاج المنوع...")
        # دمج الفيديوهات أولاً
        with open("list.txt", "w") as f:
            for v in video_files: f.write(f"file '{v}'\n")
        
        # دمج الفيديوهات وتكرارهم ليناسبوا طول الصوت
        cmd_merge = "ffmpeg -f concat -safe 0 -i list.txt -c copy merged_bg.mp4 -y"
        subprocess.run(cmd_merge, shell=True)
        
        cmd_final = (
            "ffmpeg -stream_loop -1 -i merged_bg.mp4 -i audio.mp3 "
            "-map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest final.mp4 -y"
        )
        subprocess.run(cmd_final, shell=True)

        # 5. الإرسال لتلجرام
        tg_url = f"https://api.telegram.org/bot{TG_TOKEN}/sendVideo"
        with open("final.mp4", 'rb') as video:
            requests.post(tg_url, files={'video': video}, data={'chat_id': TG_CHAT_ID, 'caption': f"🔥 قصة جديدة (الجزء الأول)\n\n{script[:200]}..."})
        
        print("✅ تم تجهيز وإرسال فيديو القصة!")

    except Exception as e:
        print(f"❌ عطل: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_story_factory())
