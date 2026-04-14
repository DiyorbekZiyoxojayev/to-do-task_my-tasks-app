from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import hashlib
import jwt
import datetime
import os

app = FastAPI(title="Advanced To-Do App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "todo_app_secret_key_2024"
ALGORITHM = "HS256"
DB_PATH = "todo.db"

# ─── DATABASE ────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            coins INTEGER DEFAULT 100,
            streak INTEGER DEFAULT 0,
            total_completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            deadline TEXT,
            priority TEXT DEFAULT 'medium',
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ─── HELPERS ─────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401, detail="Token noto'g'ri yoki muddati o'tgan")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    return verify_token(token)

# ─── SCHEMAS ─────────────────────────────────────────────────────────────────

class RegisterData(BaseModel):
    username: str
    password: str

class TaskCreate(BaseModel):
    title: str
    deadline: Optional[str] = None
    priority: str = "medium"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    deadline: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None

# ─── AUTH ROUTES ─────────────────────────────────────────────────────────────

@app.post("/register")
def register(data: RegisterData):
    conn = get_db()
    c = conn.cursor()
    existing = c.execute("SELECT username FROM users WHERE username = ?", (data.username,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=400, detail="Bu username band, boshqa tanlang!")
    c.execute(
        "INSERT INTO users (username, password_hash, coins) VALUES (?, ?, 100)",
        (data.username, hash_password(data.password))
    )
    conn.commit()
    conn.close()
    token = create_token(data.username)
    return {
        "message": f"Xush kelibsiz, {data.username}! 🎉 Sizga 100 ta tanga berildi!",
        "token": token,
        "username": data.username,
        "coins": 100
    }

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db()
    c = conn.cursor()
    user = c.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (form_data.username, hash_password(form_data.password))
    ).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Username yoki parol noto'g'ri!")
    token = create_token(form_data.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user["username"],
        "coins": user["coins"],
        "streak": user["streak"],
        "total_completed": user["total_completed"]
    }

@app.get("/me")
def get_me(username: str = Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    user = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    return {
        "username": user["username"],
        "coins": user["coins"],
        "streak": user["streak"],
        "total_completed": user["total_completed"]
    }

# ─── TASK ROUTES ─────────────────────────────────────────────────────────────

@app.get("/tasks")
def get_tasks(username: str = Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    tasks = c.execute(
        "SELECT * FROM tasks WHERE username = ? ORDER BY created_at DESC",
        (username,)
    ).fetchall()
    conn.close()
    return [dict(t) for t in tasks]

@app.post("/tasks")
def create_task(task: TaskCreate, username: str = Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    # Task qo'shganda 5 tanga sarflanadi
    user = c.execute("SELECT coins FROM users WHERE username = ?", (username,)).fetchone()
    if user["coins"] < 5:
        conn.close()
        raise HTTPException(status_code=400, detail="Tangalaringiz yetarli emas! (kerak: 5 🪙)")
    c.execute(
        "INSERT INTO tasks (username, title, deadline, priority) VALUES (?, ?, ?, ?)",
        (username, task.title, task.deadline, task.priority)
    )
    c.execute("UPDATE users SET coins = coins - 5 WHERE username = ?", (username,))
    task_id = c.lastrowid
    conn.commit()
    new_task = c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    new_coins = c.execute("SELECT coins FROM users WHERE username = ?", (username,)).fetchone()["coins"]
    conn.close()
    return {
        "task": dict(new_task),
        "coins": new_coins,
        "message": "Vazifa qo'shildi! -5 🪙 sarflandi"
    }

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate, username: str = Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    task = c.execute(
        "SELECT * FROM tasks WHERE id = ? AND username = ?", (task_id, username)
    ).fetchone()
    if not task:
        conn.close()
        raise HTTPException(status_code=404, detail="Vazifa topilmadi")

    reward_msg = ""
    penalty_msg = ""

    if update.completed is not None:
        was_completed = task["completed"]
        if update.completed and not was_completed:
            # Bajarildi — mukofot hisoblash
            today = datetime.date.today().isoformat()
            deadline = task["deadline"]
            reward = 0
            if deadline:
                if today <= deadline:
                    reward = 20  # Vaqtida bajardi
                    reward_msg = "⚡ Vaqtida bajardingiz! +20 🪙"
                else:
                    penalty = 10
                    c.execute("UPDATE users SET coins = coins - ? WHERE username = ?", (penalty, username))
                    penalty_msg = f"⏰ Deadline o'tib ketgan! -{penalty} 🪙 jarimasi"
            else:
                reward = 10
                reward_msg = "✅ Vazifa bajarildi! +10 🪙"

            if reward > 0:
                c.execute("UPDATE users SET coins = coins + ?, streak = streak + 1, total_completed = total_completed + 1 WHERE username = ?", (reward, username))
            else:
                c.execute("UPDATE users SET streak = 0, total_completed = total_completed + 1 WHERE username = ?", (username,))

            c.execute(
                "UPDATE tasks SET completed = 1, completed_at = ? WHERE id = ?",
                (datetime.datetime.now().isoformat(), task_id)
            )
        elif not update.completed and was_completed:
            # Qayta ochildi — 5 tanga jarimasi
            c.execute("UPDATE users SET coins = coins - 5, streak = 0 WHERE username = ?", (username,))
            c.execute("UPDATE tasks SET completed = 0, completed_at = NULL WHERE id = ?", (task_id,))
            penalty_msg = "🔄 Vazifa qayta ochildi. -5 🪙 jarimasi"

    if update.title is not None:
        c.execute("UPDATE tasks SET title = ? WHERE id = ?", (update.title, task_id))
    if update.deadline is not None:
        c.execute("UPDATE tasks SET deadline = ? WHERE id = ?", (update.deadline, task_id))
    if update.priority is not None:
        c.execute("UPDATE tasks SET priority = ? WHERE id = ?", (update.priority, task_id))

    conn.commit()
    updated_task = dict(c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())
    user_data = dict(c.execute("SELECT coins, streak FROM users WHERE username = ?", (username,)).fetchone())
    conn.close()

    return {
        "task": updated_task,
        "coins": user_data["coins"],
        "streak": user_data["streak"],
        "message": reward_msg or penalty_msg or "Yangilandi"
    }

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, username: str = Depends(get_current_user)):
    conn = get_db()
    c = conn.cursor()
    task = c.execute(
        "SELECT * FROM tasks WHERE id = ? AND username = ?", (task_id, username)
    ).fetchone()
    if not task:
        conn.close()
        raise HTTPException(status_code=404, detail="Vazifa topilmadi")
    # O'chirish jarimasi — 3 tanga
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if not task["completed"]:
        c.execute("UPDATE users SET coins = coins - 3 WHERE username = ?", (username,))
    conn.commit()
    new_coins = c.execute("SELECT coins FROM users WHERE username = ?", (username,)).fetchone()["coins"]
    conn.close()
    return {
        "message": "Vazifa o'chirildi" + ("" if task["completed"] else " (-3 🪙 jarimasi)"),
        "coins": new_coins
    }

@app.get("/leaderboard")
def leaderboard():
    conn = get_db()
    c = conn.cursor()
    users = c.execute(
        "SELECT username, coins, streak, total_completed FROM users ORDER BY coins DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return [dict(u) for u in users]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
