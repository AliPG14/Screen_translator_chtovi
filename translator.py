"""
translator.py - Translation module using deep_translator (Google Translate, free)
"""
from deep_translator import GoogleTranslator
import hashlib


class TranslationCache:
    """Simple LRU-like cache to avoid re-translating identical text."""

    def __init__(self, max_size: int = 200):
        self._cache: dict[str, str] = {}
        self._keys: list[str] = []
        self._max = max_size

    def _key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    def get(self, text: str) -> str | None:
        return self._cache.get(self._key(text))

    def set(self, text: str, translation: str):
        k = self._key(text)
        if k not in self._cache:
            if len(self._keys) >= self._max:
                old = self._keys.pop(0)
                del self._cache[old]
            self._keys.append(k)
        self._cache[k] = translation


class Translator:
    """Translate text from Chinese to Vietnamese using Google Translate."""

    def __init__(self, source: str = "zh-CN", target: str = "vi"):
        self.source = source
        self.target = target
        self.cache = TranslationCache()
        self._translator = GoogleTranslator(source=source, target=target)

    def translate(self, text: str) -> str:
        """Translate text. Returns original on failure."""
        if not text or not text.strip():
            return ""

        # Check cache first
        cached = self.cache.get(text)
        if cached is not None:
            return cached

        try:
            result = self._translator.translate(text)
            if result:
                self.cache.set(text, result)
                return result
        except Exception as e:
            print(f"[Translator] Loi dich: {e}")

        return f"[Loi dich] {text}"

    def set_languages(self, source: str, target: str):
        """Change source/target language pair."""
        self.source = source
        self.target = target
        self._translator = GoogleTranslator(source=source, target=target)
        self.cache = TranslationCache()  # Clear cache on language change
