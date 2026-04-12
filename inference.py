import os
import requests
import json

URL = "https://m-owais-7-email-triage-env-v1.hf.space"

def classify(text):
        text = text.lower()
            if "urgent" in text or "important" in text:
                        return "important"
                            if "lottery" in text or "win" in text or "prize" in text:
                                        return "spam"
                                            return "normal"

                                            def main():
                                                    print("[START] starting email triage")
                                                        
                                                            print("[STEP 1] resetting environment")
                                                                state = requests.post(f"{URL}/reset").json()["state"]
                                                                    
                                                                        total_reward = 0
                                                                            for i, email in enumerate(state["emails"]):
                                                                                        print(f"[STEP {i+2}] processing email {email['id']}")
                                                                                                label = classify(email["text"])
                                                                                                        action = {"email_id": email["id"], "label": label}
                                                                                                                
                                                                                                                        response = requests.post(f"{URL}/step", json=action).json()
                                                                                                                                reward = response.get("reward", 0)
                                                                                                                                        total_reward += reward
                                                                                                                                                
                                                                                                                                                        print(json.dumps({"action": action, "reward": reward}))
                                                                                                                                                                
                                                                                                                                                                    print(f"[END] total reward: {total_reward}")

                                                                                                                                                                    if __name__ == "__main__":
                                                                                                                                                                            main()
                                                                                                                                                                            