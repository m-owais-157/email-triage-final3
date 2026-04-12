import os
import time
import requests

# env config
API_BASE_URL = os.getenv("API_BASE_URL", "")
MODEL_NAME = os.getenv("MODEL_NAME", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
ENV_URL = os.getenv("ENV_URL", "https://m-owais-7-email-triage-env-v1.hf.space")


def classify_email(text):
    lower = text.lower()
    spam_kw = ["lottery", "won", "free", "click link", "claim", "limited time", "prize", "!!!"]
    imp_kw = ["urgent", "otp", "verify", "blocked", "deadline", "security", "account", "do not share", "internship", "application"]
    if sum(1 for k in spam_kw if k in lower) >= 2:
        return "spam"
    if any(k in lower for k in imp_kw):
        return "important"
    return "normal"


def try_llm(text):
    if not API_BASE_URL or not MODEL_NAME:
        return classify_email(text)
    try:
        from openai import OpenAI
        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "none")
        prompt = f"Classify this email as spam, important, or normal. Reply with ONLY the label.\n\nEmail: {text}"
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10, temperature=0.0
        )
        result = resp.choices[0].message.content.strip().lower()
        if result in ("spam", "important", "normal"):
            return result
    except Exception:
        pass
    return classify_email(text)


def main():
    t0 = time.time()
    reset_data = requests.post(f"{ENV_URL}/reset", timeout=30).json()
    state = reset_data["state"]
    emails = state.get("emails", [])
    n = len(emails)
    print(f"[START] tasks={n} env_url={ENV_URL}")

    total = 0.0
    step = 0
    for email in emails:
        step += 1
        eid = email["id"]
        label = try_llm(email["text"])
        action = {"email_id": eid, "label": label}
        resp = requests.post(f"{ENV_URL}/step", json=action, timeout=30).json()
        r = resp.get("reward", 0)
        done = resp.get("done", False)
        info = resp.get("info", {})
        total += r
        print(f"[STEP] step={step} email_id={eid} predicted={label} correct={info.get('correct_label','?')} reward={r} total_reward={total} done={done}")
        if done:
            break

    elapsed = round(time.time() - t0, 2)
    max_r = n * 2
    score = max(0.0, min(1.0, total / max_r)) if max_r > 0 else 0.0
    print(f"[END] total_reward={total} normalized_score={round(score, 4)} steps={step} elapsed={elapsed}s")


if __name__ == "__main__":
    main()
