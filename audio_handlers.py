import json
import requests
import winsound
import speech_recognition as sr

from faster_whisper import WhisperModel

from config import SPEAKER_ID, TEMP_USER_IMPUT, TEMP_AI_RESPONCE
    
SpeakerID = SPEAKER_ID

whisper_model = WhisperModel("medium", device="cpu", compute_type="int8")

recognizer = sr.Recognizer()

# =========================
# ▼ 音声（VOICEVOX）
# =========================
class AIVoice:
    def __init__(self):
        pass
    def speak(self,text, speaker_id=SpeakerID):
        print(f"トーカ: {text}")
        try:
            q = requests.post(
                "http://127.0.0.1:50021/audio_query",
                params={"text": text, "speaker": speaker_id}
            )
            s = requests.post(
                "http://127.0.0.1:50021/synthesis",
                params={"speaker": speaker_id},
                data=json.dumps(q.json())
            )

            # AIVoice.speak 内
            with open(TEMP_AI_RESPONCE, "wb") as f:
                f.write(s.content)

            winsound.PlaySound(TEMP_AI_RESPONCE, winsound.SND_FILENAME)

        except Exception as e:
            print("音声エラー:", e)

# =========================
# ▼ 音声認識
# =========================
class ListenUser:
    def __init__(self):
            with sr.Microphone() as source:
                print("ノイズ調整中...")
                recognizer.adjust_for_ambient_noise(source,duration=1)

    def listen(self):
        try:
            with sr.Microphone() as source:
                print("\n話してください...（待機中）")
                recognizer.dynamic_energy_threshold = False

                try:
                    audio = recognizer.listen(source, phrase_time_limit=10.0)
                except sr.WaitTimeoutError:
                    return None

            # 一時保存
            with open(TEMP_USER_IMPUT, "wb") as f:
                f.write(audio.get_wav_data())

            print("解析中...")

            # ▼ ノイズ除去（VAD付き）
            segments, info = whisper_model.transcribe(
                TEMP_USER_IMPUT,
                language="ja",
                vad_filter=True,
                vad_parameters=dict(
                    min_speech_duration_ms=500  # ←短いノイズをカット
                ),
                condition_on_previous_text=False
            )

            user_text = ""
            for segment in segments:
                user_text += segment.text

            if not user_text:
                return None

            user_text = user_text.strip()

            # ▼ 動画系ノイズ除去
            ignore_phrases = ["ご視聴", "チャンネル登録", "字幕"]
            if any(p in user_text for p in ignore_phrases):
                return None

            print(f"あなた: {user_text}")
            return user_text

        except Exception as e:
            print(f"音声認識エラー: {e}")
            return None
