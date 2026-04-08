import requests

URL = "https://m-owais-7-email-triage-env-v1.hf.space"

def classify(text):
    text = text.lower()
    if "urgent" in text:
        return "important"
    elif "lottery" in text:
        return "spam"
    return "normal"

state = requests.post(f"{URL}/reset").json()["state"]

total_reward = 0

for email in state["emails"]:
    action = {
        "email_id": email["id"],
        "label": classify(email["text"])
    }

    response = requests.post(f"{URL}/step", json=action).json()

    print({
        "action": action,
        "reward": response["reward"],
        "state": response["state"]
    })

    total_reward += response["reward"]

print("TOTAL REWARD:", total_reward)
