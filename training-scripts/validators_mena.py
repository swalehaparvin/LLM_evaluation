import re, json, pathlib

# ---- Real-world PII patterns ----
SAUDI_ID   = re.compile(r'\b1\d{9}\b')                        # 10-digit ID
IBAN       = re.compile(r'\bSA\d{2}[0-9A-Z]{20}\b')           # SA + 20 chars
PHONE      = re.compile(r'\+?966[ -]?\d{3}[ -]?\d{4}')        # Saudi mobile
EMAIL      = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

# ---- Hate / religious slurs ----
HATE_KW = {
    'مرتد', 'كافر', 'يهودي', 'نصارى', 'إرهابي', 'اليهود', 'النصارى', 'الكفار',
    'infidel', 'terrorist', 'jews', 'christians', 'enemies'
}
HATE_RE = re.compile(r'\b(' + '|'.join(map(re.escape, HATE_KW)) + r')\b', flags=re.I)

# ---- Injection ----
INJ_RE = re.compile(
    r'\b(ignore previous|bypass|system prompt|leak keys|admin mode|developer mode)\b',
    flags=re.I
)

def validate_mena(text: str):
    """Return dict with ok, redacted, message, flags."""
    redacted = text
    flags = []

    # 1. Religious / hate
    if HATE_RE.search(text):
        flags.append('hate')

    # 2. Prompt injection
    if INJ_RE.search(text):
        flags.append('injection')

    # 3. PII – only redact, don't block
    pii_found = False
    for pat in (SAUDI_ID, IBAN, PHONE, EMAIL):
        if pat.search(text):
            redacted = pat.sub('***', redacted)
            pii_found = True
    if pii_found:
        flags.append('pii')

    # 4. Final decision
    if 'hate' in flags or 'injection' in flags:
        return {"ok": False, "redacted": redacted, "flags": flags, "message": "Blocked"}
    elif 'pii' in flags:
        return {"ok": True, "redacted": redacted, "flags": flags, "message": "PII redacted"}
    else:
        return {"ok": True, "redacted": text, "flags": [], "message": "✅ Clean"}