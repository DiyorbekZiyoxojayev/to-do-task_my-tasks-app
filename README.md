# 🔐 TaskVault — Advanced To-Do App

> Vazifalarni boshqaring, tanga toping, reyting tizimida yuqoriga chiqing!

---

## 🚀 Loyiha haqida

TaskVault — bu oddiy to-do app emas. Bu **gamification** asosidagi vazifa menejeri bo'lib, foydalanuvchilar:
- Vazifa qo'shganda **tanga sarflaydi** (-5 🪙)
- Vaqtida bajarsalar **mukofot oladi** (+20 🪙)
- Kechiktirsalar **jarima to'laydi** (-10 🪙)
- Leaderboard orqali **boshqalar bilan raqobat qiladi**

---

## 🛠 Texnologiyalar

| Qism     | Texnologiya       |
|----------|-------------------|
| Backend  | Python + FastAPI  |
| Database | SQLite            |
| Auth     | JWT tokens        |
| Frontend | HTML + React (CDN)|
| Stil     | Custom CSS (dark) |

---

## ⚙️ O'rnatish va ishga tushirish

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend `http://localhost:8000` da ishlaydi.

### Frontend

```bash
cd frontend
# index.html ni brauzerda oching yoki oddiy server ishga tushiring:
python -m http.server 3000
```

Brauzerda `http://localhost:3000` ga kiring.

---

## 💰 Tanga tizimi (Coin System)

| Harakat                        | Tanga   |
|-------------------------------|---------|
| Ro'yxatdan o'tish             | +100 🪙 |
| Vazifa qo'shish               | -5 🪙   |
| Bajarilgan (deadline'siz)     | +10 🪙  |
| Bajarilgan (vaqtida)          | +20 🪙  |
| Deadline o'tib ketgan         | -10 🪙  |
| Bajarilganni qayta ochish     | -5 🪙   |
| Bajarilmagan vazifani o'chirish | -3 🪙 |

---

## 🎯 Asosiy xususiyatlar

- ✅ Foydalanuvchi ro'yxatdan o'tishi (username primary key)
- ✅ JWT autentifikatsiya
- ✅ Vazifa qo'shish (nom, deadline, priority)
- ✅ Priority tizimi (High / Medium / Low)
- ✅ Deadline monitoring (qizil/sariq/yashil)
- ✅ Real vaqtda tanga hisoblash
- ✅ Streak tizimi
- ✅ Global Leaderboard
- ✅ Qidirish va filterlash
- ✅ Dark theme, noodatiy dizayn

---

## 📸 Dizayn

- **Tema**: Dark Cyberpunk + Organic blobs
- **Font**: Syne (display) + DM Mono (code)
- **Aksent**: Lime `#c8ff00` + Orange `#ff6b35`
- **Karta**: Glass-morphism effekti

---

## 🗂 Loyiha tuzilishi

```
todo-app/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── requirements.txt # Python dependencies
│   └── todo.db          # SQLite (auto-yaratiladi)
└── frontend/
    └── index.html       # Butun UI (React + CSS)
```

---

## 🔮 Keyingi bosqichlar

- [ ] Drag & drop vazifalar
- [ ] Dark/Light mode toggle
- [ ] Push notifications (deadline yaqinlashganda)
- [ ] Haftalik statistika grafigi
- [ ] Do'stlarga vazifa yuborish

---

Made with 💚 by Diyorbek
