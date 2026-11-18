class JBotVoiceBridge:
    def __init__(self, wake_word="J-Bot"):
        self.wake_word = wake_word
        self.hands_free_enabled = True

    def parse_voice_intent(self, transcript):
        t = transcript.lower()
        if any(k in t for k in ["repair", "phone", "frp", "flash", "screen", "battery"]):
            return "REPAIR_PRO"
        if any(k in t for k in ["price", "appraise", "card", "listing", "store", "sell"]):
            return "COMMERCE"
        if any(k in t for k in ["music", "story", "comic", "reaper", "script", "video"]):
            return "STUDIO"
        return "DEV_OPS"
