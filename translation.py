from googletrans import Translator
from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator
from transformers import AutoModel, AutoTokenizer

# --------------------
# 1. Input text (Telugu)
# --------------------
raw = "ఇది ప్రముఖ కంప్యూటర్ సైన్స్ ప్లాట్‌ఫారమ్."

# --------------------
# 2. Translation using Google Translate
# --------------------
translator = Translator()
translated_hi = translator.translate(raw, src='te', dest='').text
print("Telugu → Hindi Translation:", translated_hi)