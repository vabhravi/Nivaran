"""
NIVARAN — Hindi Simplifier & Text-to-Speech Module
Converts extracted civic notice entities into plain Hindi sentences,
then generates MP3 audio using gTTS.

Includes Hindi number localization (e.g., 500 → "Paanch Sau").
"""

import os
import uuid
import re
from gtts import gTTS

# ───────────────────────────────────────────────────────
# Audio output directory
# ───────────────────────────────────────────────────────
AUDIO_DIR = os.path.join(os.path.dirname(__file__), '..', 'temp_audio')
os.makedirs(AUDIO_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════
# HINDI NUMBER LOCALIZATION
# ═══════════════════════════════════════════════════════

# Basic Hindi number words
HINDI_ONES = [
    '', 'Ek', 'Do', 'Teen', 'Chaar', 'Paanch', 'Chhah', 'Saat', 'Aath', 'Nau',
    'Das', 'Gyaarah', 'Baarah', 'Terah', 'Chaudah', 'Pandrah', 'Solah',
    'Satrah', 'Athaarah', 'Unnees'
]

HINDI_TENS = [
    '', 'Das', 'Bees', 'Tees', 'Chaalees', 'Pachaas', 'Saath', 'Sattar',
    'Assi', 'Nabbe'
]

# Special two-digit numbers in Hindi (20-99 have unique forms)
HINDI_TWO_DIGITS = {}
# Fill common ones
_special_numbers = {
    20: 'Bees', 21: 'Ikkees', 22: 'Baaees', 23: 'Teyees', 24: 'Chaubees',
    25: 'Pachchees', 26: 'Chhabbees', 27: 'Sattaees', 28: 'Atthaees',
    29: 'Untees', 30: 'Tees', 31: 'Ikattees', 32: 'Battees',
    33: 'Taintees', 34: 'Chauntees', 35: 'Paintees', 36: 'Chhattees',
    37: 'Saintees', 38: 'Adtees', 39: 'Untaalees', 40: 'Chaalees',
    41: 'Iktaalees', 42: 'Bayaalees', 43: 'Taintaalees', 44: 'Chauvaalees',
    45: 'Paintaalees', 46: 'Chhiyaalees', 47: 'Saintaalees', 48: 'Adtaalees',
    49: 'Unchaas', 50: 'Pachaas', 51: 'Ikyaavan', 52: 'Baavan',
    53: 'Tirpan', 54: 'Chauvan', 55: 'Pachpan', 56: 'Chhappan',
    57: 'Sattaavan', 58: 'Atthaavan', 59: 'Unsath', 60: 'Saath',
    61: 'Iksath', 62: 'Baasath', 63: 'Tirsath', 64: 'Chaunsath',
    65: 'Painsath', 66: 'Chhiyaasath', 67: 'Sadsath', 68: 'Adsath',
    69: 'Unhattar', 70: 'Sattar', 71: 'Ikhattar', 72: 'Bahattar',
    73: 'Tihattar', 74: 'Chauhattar', 75: 'Pachhattar', 76: 'Chhihattar',
    77: 'Satahattar', 78: 'Athhattar', 79: 'Unaasee', 80: 'Assi',
    81: 'Ikyaasee', 82: 'Bayaasee', 83: 'Tiraasee', 84: 'Chauraasee',
    85: 'Pachaasee', 86: 'Chhiyaasee', 87: 'Sataasee', 88: 'Athaasee',
    89: 'Navaasee', 90: 'Nabbe', 91: 'Ikyaanbe', 92: 'Baanbe',
    93: 'Tiraanbe', 94: 'Chauraanbe', 95: 'Pachaanbe', 96: 'Chhiyaanbe',
    97: 'Sattaanbe', 98: 'Atthaanbe', 99: 'Ninyaanbe'
}
HINDI_TWO_DIGITS.update(_special_numbers)


def number_to_hindi(n):
    """
    Convert an integer to Hindi words (transliterated in Roman script).

    Supports the Indian numbering system:
    - Sau (100), Hazaar (1,000), Lakh (1,00,000), Crore (1,00,00,000)

    Examples:
        500 → "Paanch Sau"
        1500 → "Ek Hazaar Paanch Sau"
        25000 → "Pachchees Hazaar"
        100000 → "Ek Lakh"

    Args:
        n (int or float): The number to convert.

    Returns:
        str: Hindi words for the number.
    """
    if n is None:
        return ''

    # Handle float → int conversion
    n = int(round(float(n)))

    if n == 0:
        return 'Shoonya'

    if n < 0:
        return 'Minus ' + number_to_hindi(-n)

    parts = []

    # Crore (1,00,00,000)
    if n >= 10000000:
        crore = n // 10000000
        parts.append(_two_digit_hindi(crore) + ' Crore')
        n %= 10000000

    # Lakh (1,00,000)
    if n >= 100000:
        lakh = n // 100000
        parts.append(_two_digit_hindi(lakh) + ' Lakh')
        n %= 100000

    # Hazaar (1,000)
    if n >= 1000:
        hazaar = n // 1000
        parts.append(_two_digit_hindi(hazaar) + ' Hazaar')
        n %= 1000

    # Sau (100)
    if n >= 100:
        sau = n // 100
        parts.append(_two_digit_hindi(sau) + ' Sau')
        n %= 100

    # Remaining (1-99)
    if n > 0:
        parts.append(_two_digit_hindi(n))

    return ' '.join(parts)


def _two_digit_hindi(n):
    """Convert a number 1-99 to Hindi words."""
    if n <= 0:
        return ''
    if n < 20:
        return HINDI_ONES[n]
    if n in HINDI_TWO_DIGITS:
        return HINDI_TWO_DIGITS[n]
    # Fallback for any missing: tens + ones
    tens = n // 10
    ones = n % 10
    if ones == 0:
        return HINDI_TENS[tens]
    return HINDI_TENS[tens] + ' ' + HINDI_ONES[ones]


# ═══════════════════════════════════════════════════════
# HINDI SENTENCE CONSTRUCTION
# ═══════════════════════════════════════════════════════

# Hindi day names
DAY_MAP = {
    'monday': 'Somwaar', 'tuesday': 'Mangalwaar', 'wednesday': 'Budhwaar',
    'thursday': 'Guruwaar', 'friday': 'Shukrawaar', 'saturday': 'Shaniwaar',
    'sunday': 'Raviwaar',
    'mon': 'Somwaar', 'tue': 'Mangalwaar', 'wed': 'Budhwaar',
    'thu': 'Guruwaar', 'fri': 'Shukrawaar', 'sat': 'Shaniwaar', 'sun': 'Raviwaar',
}

# Hindi month names
MONTH_MAP = {
    'january': 'January', 'february': 'February', 'march': 'March',
    'april': 'April', 'may': 'May', 'june': 'June',
    'july': 'July', 'august': 'August', 'september': 'September',
    'october': 'October', 'november': 'November', 'december': 'December',
    'jan': 'January', 'feb': 'February', 'mar': 'March',
    'apr': 'April', 'jun': 'June', 'jul': 'July',
    'aug': 'August', 'sep': 'September', 'oct': 'October',
    'nov': 'November', 'dec': 'December',
}

# Action verb translations
ACTION_MAP = {
    'pay': 'bharo',
    'deposit': 'jamaa karo',
    'submit': 'jama karo',
    'file': 'daakhil karo',
    'report': 'report karo',
    'renew': 'naveeneekarana karo',
    'register': 'panjeekaran karo',
    'comply': 'paalan karo',
    'respond': 'javaab do',
    'appear': 'upasthit ho',
    'contact': 'sampark karo',
}


def build_hindi_summary(entities):
    """
    Construct a plain Hindi sentence summarizing a civic notice.

    Args:
        entities (dict): Output from ner_model.extract_civic_entities()

    Returns:
        str: Hindi summary sentence (transliterated Roman script for gTTS).
    """
    parts = []

    # Greeting
    parts.append('Namaste.')

    # Organization
    if entities.get('organizations'):
        org = entities['organizations'][0]
        parts.append(f'{org} ki taraf se yeh suchna hai.')

    # Amount
    if entities.get('amounts'):
        try:
            amount_str = entities['amounts'][0]
            amount_num = float(re.sub(r'[^\d.]', '', amount_str.replace(',', '')))
            hindi_amount = number_to_hindi(amount_num)
            parts.append(f'Aapko {hindi_amount} Rupaye bharne hain.')
        except (ValueError, TypeError, IndexError):
            parts.append(f'Aapko kuch rashi bharnee hai.')

    # Date / Deadline
    if entities.get('dates'):
        date_str = entities['dates'][0]
        hindi_date = _translate_date(date_str)
        parts.append(f'Iska antim din {hindi_date} hai.')

    # Action required
    if entities.get('actions'):
        action = entities['actions'][0]
        hindi_action = ACTION_MAP.get(action.lower(), action)
        parts.append(f'Kripya samay par {hindi_action}.')

    # Default if nothing extracted
    if len(parts) <= 1:
        parts.append('Is suchna mein koi vishesh jaankaaree nahi mili.')
        parts.append('Kripya apne najdeeki jan seva kendra se sampark karein.')

    # Closing
    parts.append('Dhanyavaad.')

    return ' '.join(parts)


def _translate_date(date_str):
    """Translate a date string to more readable Hindi-transliterated form."""
    result = date_str
    # Replace English day/month names with Hindi equivalents
    for eng, hindi in DAY_MAP.items():
        result = re.sub(r'\b' + eng + r'\b', hindi, result, flags=re.IGNORECASE)
    for eng, hindi in MONTH_MAP.items():
        result = re.sub(r'\b' + eng + r'\b', hindi, result, flags=re.IGNORECASE)
    return result


# ═══════════════════════════════════════════════════════
# TEXT-TO-SPEECH (gTTS)
# ═══════════════════════════════════════════════════════

def generate_audio(text, lang='hi'):
    """
    Generate an MP3 audio file from Hindi text using gTTS.

    Args:
        text (str): The Hindi text (Roman transliteration works with gTTS 'hi').
        lang (str): Language code for gTTS. Default 'hi' (Hindi).

    Returns:
        dict: {
            'audio_filename': str — filename of generated MP3,
            'audio_path': str — full path to the MP3 file,
            'error': str or None
        }
    """
    try:
        # Generate unique filename
        audio_filename = f'nivaran_{uuid.uuid4().hex[:12]}.mp3'
        audio_path = os.path.join(AUDIO_DIR, audio_filename)

        # Generate audio with gTTS
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(audio_path)

        return {
            'audio_filename': audio_filename,
            'audio_path': audio_path,
            'error': None
        }

    except Exception as e:
        return {
            'audio_filename': None,
            'audio_path': None,
            'error': f'Audio generation failed: {str(e)}'
        }


def cleanup_audio_file(audio_path):
    """Delete an audio file after it has been served (stateless processing)."""
    try:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
    except OSError:
        pass
