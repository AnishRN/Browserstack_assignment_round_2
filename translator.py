import requests

class MyMemoryTranslator:

    API_URL = "https://api.mymemory.translated.net/get"

    def translate(self, text, target="en"):
        params = {
            "q": text,
            "langpair": f"es|{target}"
        }
        try:
            r = requests.get(self.API_URL, params=params)
            data = r.json()
            return data["responseData"]["translatedText"]
        except:
            return text

    def translate_batch(self, texts):
        return [self.translate(t) for t in texts]
