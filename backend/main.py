from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import sqlite3
import os

ADMIN_TOKEN = "admintoken123"
DB_PATH = os.path.join(os.path.dirname(__file__), "kampuskuevent.db")

app = FastAPI(title="KampusKuEvent API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schemas
class EventBase(BaseModel):
    title: str
    date: str
    location: str
    quota: int
    description: Optional[str] = ""

class Event(EventBase):
    id: int
    class Config:
        orm_mode = True

class ParticipantBase(BaseModel):
    name: str
    email: EmailStr
    event_id: int

class Participant(ParticipantBase):
    id: int
    class Config:
        orm_mode = True

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def admin_required(x_api_key: Optional[str] = Header(None)):
    if x_api_key != ADMIN_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing admin token")
    return True

# Event endpoints
@app.get("/events", response_model=List[Event])
def read_events(conn=Depends(get_db)):
    cur = conn.execute("SELECT * FROM events ORDER BY date")
    rows = cur.fetchall()
    return [dict(r) for r in rows]

@app.post("/events", response_model=Event, status_code=201)
def create_event(event: EventBase, authorized: bool = Depends(admin_required), conn=Depends(get_db)):
    cur = conn.execute(
        "INSERT INTO events (title, date, location, quota, description) VALUES (?, ?, ?, ?, ?)",
        (event.title, event.date, event.location, event.quota, event.description)
    )
    conn.commit()
    event_id = cur.lastrowid
    row = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    return dict(row)

@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: int, event: EventBase, authorized: bool = Depends(admin_required), conn=Depends(get_db)):
    cur = conn.execute(
        "UPDATE events SET title=?, date=?, location=?, quota=?, description=? WHERE id=?",
        (event.title, event.date, event.location, event.quota, event.description, event_id)
    )
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    row = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    return dict(row)

@app.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: int, authorized: bool = Depends(admin_required), conn=Depends(get_db)):
    cur = conn.execute("DELETE FROM events WHERE id=?", (event_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Event not found")
    return

# Participant endpoints
@app.get("/participants", response_model=List[Participant])
def get_participants(conn=Depends(get_db)):
    rows = conn.execute("SELECT * FROM participants").fetchall()
    return [dict(r) for r in rows]

@app.post("/participants", response_model=Participant, status_code=201)
def register_participant(participant: ParticipantBase, conn=Depends(get_db)):
    # check event exists
    ev = conn.execute("SELECT * FROM events WHERE id=?", (participant.event_id,)).fetchone()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    # check quota
    count = conn.execute("SELECT COUNT(*) as c FROM participants WHERE event_id=?", (participant.event_id,)).fetchone()['c']
    if count >= ev['quota']:
        raise HTTPException(status_code=400, detail="Event quota full")
    cur = conn.execute(
        "INSERT INTO participants (name, email, event_id) VALUES (?, ?, ?)",
        (participant.name, participant.email, participant.event_id)
    )
    conn.commit()
    pid = cur.lastrowid
    row = conn.execute("SELECT * FROM participants WHERE id=?", (pid,)).fetchone()
    return dict(row)

@app.get("/events/{event_id}/participants", response_model=List[Participant])
def participants_by_event(event_id: int, conn=Depends(get_db)):
    ev = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    rows = conn.execute("SELECT * FROM participants WHERE event_id=?", (event_id,)).fetchall()
    return [dict(r) for r in rows]

@app.delete("/participants/{participant_id}", status_code=204)
def delete_participant(participant_id: int, authorized: bool = Depends(admin_required), conn=Depends(get_db)):
    cur = conn.execute("DELETE FROM participants WHERE id=?", (participant_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Participant not found")
    return
