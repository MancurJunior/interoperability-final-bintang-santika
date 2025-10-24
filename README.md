KampusKuEvent - Full UTS Project (FastAPI + SQLite)

Struktur:
- backend/
  - main.py (FastAPI app)
  - kampuskuevent.db (SQLite database with seed data)
  - requirements.txt
  - create_db.sql
- frontend/
  - index.html (user: daftar event)
  - event_detail.html (detail event + daftar peserta + form pendaftaran)
  - admin.html (admin: CRUD event & peserta)
  - style.css (biru-putih)
- README.md (cara menjalankan)

Cara menjalankan:
1. Backend:
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --host 127.0.0.1 --port 8000

   Akses API docs: http://127.0.0.1:8000/docs

2. Frontend:
   cd frontend
   python -m http.server 8080
   Buka browser:
   - User: http://127.0.0.1:8080/index.html
   - Detail: http://127.0.0.1:8080/event_detail.html?id=1
   - Admin: http://127.0.0.1:8080/admin.html

Admin token:
- Gunakan header X-API-KEY: admintoken123 untuk endpoint admin (POST/PUT/DELETE)
