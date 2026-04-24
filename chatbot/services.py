import os

class KeyManager:
    def __init__(self):
        keys_string = os.getenv('GEMINI_API_KEYS', '')
        self.keys = [k.strip() for k in keys_string.split(',') if k.strip()]
        self.failed_keys = set()

    def get_key(self):
        available = [k for k in self.keys if k not in self.failed_keys]
        return available[0] if available else None

    def mark_failed(self, key):
        self.failed_keys.add(key)

    def is_exhausted(self):
        return len(self.failed_keys) >= len(self.keys)


class GeminiService:
    def __init__(self):
        self.key_manager = KeyManager()
        self.model = None
        self.current_key = None

    def _setup_model(self):
        if self.model is not None:
            return

        import google.generativeai as genai

        key = self.key_manager.get_key()
        if not key:
            raise Exception("All API keys exhausted")

        genai.configure(api_key=key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.current_key = key

    def chat(self, message, history):
        self._setup_model()

        from .context import STORE_INFO, PRODUCT_SUMMARY
        from .prompts import SYSTEM_PROMPT

        try:
            context = f"Categories: {', '.join(STORE_INFO['categories'])}\nProducts: {PRODUCT_SUMMARY}"
            history_text = self._format_history(history)
            prompt = SYSTEM_PROMPT.format(
                store_name=STORE_INFO['name'],
                store_context=context,
                history=history_text,
                message=message
            )
            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "exhausted" in error_msg or "limit" in error_msg:
                self.key_manager.mark_failed(self.current_key)
                self.model = None
                self.current_key = None
                if not self.key_manager.is_exhausted():
                    return self.chat(message, history)
                return "All API keys are exhausted. Please try again tomorrow."
            return f"Error: {str(e)}"

    def _format_history(self, history):
        if not history:
            return "(No previous conversation)"
        lines = []
        for msg in history[-10:]:
            role = "User" if msg['role'] == 'user' else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)