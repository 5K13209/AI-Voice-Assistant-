import time

last_request_time = 0
MIN_INTERVAL = 5 

# =========================
# ▼ 感情
# =========================
class Emotion:
    def update_emotion(text, emotion):
        hap = ["好き","ありがとう","すごい","最高"]
        fun = ["面白い","楽しい","興味深い","草"]
        ang = ["キモイ","下手","変","おかしい","ばか","うるさい"]
        sad = ["残念","がっかり","失望","嫌い"]

        if any(h in text for h in hap):
            emotion["like"] += 3
            emotion["trust"] += 2

        if any(f in text for f in fun):
            emotion["fun"] += 4

        if any(a in text for a in ang):
            emotion["anger"] += 5
            emotion["trust"] -= 3

        if any(s in text for s in sad):
            emotion["sad"] += 4
            emotion["like"] -= 2

        # clamp
        for k in emotion:
            emotion[k] = max(0, min(100, emotion[k]))

        return emotion
    
class AppUtils:
    def can_send():
        return (time.time() - last_request_time) > MIN_INTERVAL