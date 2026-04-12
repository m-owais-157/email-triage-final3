import os
import time
import json
import urllib.request

API_BASE_URL = os.getenv("API_BASE_URL", "")
MODEL_NAME = os.getenv("MODEL_NAME", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
ENV_URL = os.getenv("ENV_URL", "https://m-owais-7-email-triage-env-v1.hf.space")

def post_json(url, data=None):
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    body = json.dumps(data).encode("utf-8") if data is not None else b""
    with urllib.request.urlopen(req, data=body, timeout=30) as f:
        return json.load(f)

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
    try:
        reset_data = post_json(f"{ENV_URL}/reset")
    except Exception as e:
        print(f"[ERROR] Failed to reset: {e}")
        return

    state = reset_data.get("state", {})
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
        try:
            resp = post_json(f"{ENV_URL}/step", data=action)
            r = resp.get("reward", 0)
            done = resp.get("done", False)
            info = resp.get("info", {})
            total += r
            print(f"[STEP] step={step} email_id={eid} predicted={label} correct={info.get('correct_label','?')} reward={r} total_reward={total} done={done}")
            if done:
                break
        except Exception as e:
            print(f"[ERROR] Step failed: {e}")
            break

    elapsed = round(time.time() - t0, 2)
    max_r = n * 2
    score = max(0.0, min(1.0, total / max_r)) if max_r > 0 else 0.0
    print(f"[END] total_reward={total} normalized_score={round(score, 4)} steps={step} elapsed={elapsed}s")

if __name__ == '__main__':
    main()
