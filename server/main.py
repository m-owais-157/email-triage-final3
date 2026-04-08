from fastapi import FastAPI

app = FastAPI(docs_url="/docs", redoc_url="/redoc")

# Global state
current_step = 0

# 🔥 Improved dataset (realistic + noisy)
emails = [
    {"id": 1, "text": "URGENT: Your SBI account will be blocked in 24 hrs. Verify now.", "label": "important"},
    {"id": 2, "text": "Congrats! You won ₹10 lakh lottery. Click link to claim.", "label": "spam"},
    {"id": 3, "text": "Reminder: Project meeting rescheduled to Monday 10 AM", "label": "normal"},
    {"id": 4, "text": "Flipkart Big Billion Days sale is live!", "label": "normal"},
    {"id": 5, "text": "Google internship application deadline extended", "label": "important"},
    {"id": 6, "text": "Your OTP is 492831. Do not share.", "label": "important"},
    {"id": 7, "text": "Win iPhone 15 FREE!!! Limited time offer", "label": "spam"}
]

# ---------------- BASIC ROUTES ----------------

@app.get("/")
def home():
    return {"message": "Email Triage OpenEnv is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/metadata")
def metadata():
    return {
        "name": "Smart Email Triage Environment",
        "description": "Classify emails into spam, important, or normal using realistic scenarios and reward-based learning"
    }

@app.get("/schema")
def schema():
    return {
        "action": {
            "email_id": "int",
            "label": "string"
        },
        "observation": {
            "emails": "list",
            "step": "int"
        },
        "state": {
            "step": "int"
        }
    }

@app.get("/state")
def state():
    return {"state": {"step": current_step}}

# ---------------- ENVIRONMENT ----------------

@app.post("/reset")
def reset():
    global current_step
    current_step = 0

    visible_emails = [{"id": e["id"], "text": e["text"]} for e in emails]

    return {
        "state": {
            "emails": visible_emails,
            "step": current_step
        }
    }

@app.post("/step")
def step(action: dict):
    global current_step

    email_id = action.get("email_id")
    user_label = action.get("label")

    email = next((e for e in emails if e["id"] == email_id), None)

    if email is None:
        return {
            "state": {"step": current_step},
            "reward": -2,
            "done": False,
            "info": {"error": "Invalid email_id"}
        }

    correct_label = email["label"]

    # 🔥 Improved reward logic
    if user_label == correct_label:
        reward = 2
    elif correct_label == "spam":
        reward = -3  # harsher penalty
    else:
        reward = -1

    current_step += 1
    done = current_step >= len(emails)

    return {
        "state": {"step": current_step},
        "reward": reward,
        "done": done,
        "info": {"correct_label": correct_label}
    }

# ---------------- MCP ----------------

@app.post("/mcp")
def mcp():
    return {
        "jsonrpc": "2.0",
        "result": "ok"
    }

# ---------------- RUN ----------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
@app.get("/state")
def get_state():
    return {"state": state}
