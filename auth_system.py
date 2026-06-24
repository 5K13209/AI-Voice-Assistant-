import speech_recognition as sr
import os

from speechbrain.inference.speaker import SpeakerRecognition
from config import THRESHOLD
    
Threshold = THRESHOLD

class RegisterVoice:
    def __init__(self):
        self.recognizer = sr.Recognizer()

#　録音部分
    def record_voice(self, filename):
        try:

            with sr.Microphone() as source:
                print("マイク調整中...")
                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1
                )

                print("録音開始")

                audio = self.recognizer.listen(
                    source,
                    timeout=None,
                    phrase_time_limit=8.0
                )

            with open(filename, "wb") as f:
                f.write(audio.get_wav_data())

            print(f"{filename} に保存")

            return filename

        except Exception as e:
            print(f"録音エラー: {e}")
            return None

#　回数指定と返却
    def register(self):
        os.makedirs("voice_data", exist_ok=True)

        voice_refs = []

        for i in range(5):

            print(f"{i+1}/5 回目")

            filename = os.path.join(
            "voice_data",
            f"voice_{i}.wav"
        )

            result = self.record_voice(filename)

            if result:
                voice_refs.append(result)

        print(voice_refs)

        return voice_refs
    
#==========================
# ▼ 声帯認証
# =========================
class VoiceAuth:
    def __init__(self,memory_manager):
        self.model = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb"
        ) 

        self.memory_manager = memory_manager

    def voice_check(self, path):
        refs = self.memory_manager.get_voice_refs()

        if not refs:
            print("登録音声がありません")
            return False

        scores = []

        for ref in refs:

            if not os.path.exists(ref):
                print(f"ファイルなし: {ref}")
                continue

            print(ref)
            print(os.path.exists(ref))
        
            score, _ = self.model.verify_files(ref, path)

            print(f"{ref} : {float(score):.4f}")

            scores.append(float(score))

        if len(scores) == 0:
            print("利用可能な登録音声がありません")
            return False

        max_score = max(scores)

        print(f"平均スコア: {max_score:.3f}")

        if max_score > Threshold:
            print("本人")
            return True

        print("他人")
        return False
