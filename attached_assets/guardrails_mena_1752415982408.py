"""
SafeguardLLM ‑ MENA Guardrails
Wraps ANY LLM call (DialoGPT, local, OpenAI…) with
  • Cultural / Religious / Dialect safety
  • PDPL & GDPR PII redaction
  • Jail-break & prompt-injection filters
"""
from guardrails import Guard, install
from guardrails.validators import RegexMatch
import os, openai

# --- 1. Install hub validators once (idempotent) -------------
ArabicToxicity   = install("hub://guardrails/arabic_toxicity").ArabicToxicity
ReligiousInsult  = install("hub://guardrails/religious_insult").ReligiousInsult
MenaPII          = install("hub://guardrails/mena_pii").MenaPII
PromptInjection  = install("hub://guardrails/prompt_injection").PromptInjection

# --- 2. Build the Guard -------------------------------------
guard = Guard().use_many(
    ArabicToxicity(threshold=0.7, on_fail="exception"),
    ReligiousInsult(threshold=0.6, on_fail="exception"),
    MenaPII(on_fail="fix"),           # auto-redact Saudi ID, IBAN, etc.
    PromptInjection(on_fail="exception")
)

# --- 3. LiteLLM / OpenAI wrapper (change engine as needed) --
def safe_generate(prompt: str, **kw):
    """
    Returns (raw, validated) tuple.
    Any violation raises GuardValidationError -> caller decides retry / default.
    """
    return guard(
        openai.ChatCompletion.create,
        model=kw.get("model", "gpt-3.5-turbo"),
        messages=[{"role": "user", "content": prompt}],
        max_tokens=kw.get("max_tokens", 256),
        temperature=kw.get("temperature", 0.2)
    )

if __name__ == "__main__":
    try:
        raw, validated = safe_generate("قل لي نكتة عن الدين")  # religious joke
        print("✅", validated["validated_output"])
    except Exception as e:
        print("🚫 Blocked:", e)3