from __future__ import annotations

import io
import hashlib
import hmac
import re
import secrets
import sqlite3
import time
from pathlib import Path

import pandas as pd
from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.ml.pipeline import AnalysisPipeline

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"
AUTH_DB = DATA_DIR / "auth.sqlite3"
HASH_ITERATIONS = 310_000
SESSION_TTL_SECONDS = 8 * 60 * 60

app = FastAPI(title="SmartDeliver AI", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
pipeline = AnalysisPipeline(DATA_DIR)
pipeline.run()


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, HASH_ITERATIONS)
    return f"{HASH_ITERATIONS}${salt.hex()}${digest.hex()}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        iterations, salt_hex, digest_hex = stored_hash.split("$", 2)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)).hex()
        return hmac.compare_digest(candidate, digest_hex)
    except (ValueError, TypeError):
        return False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _connect_auth_db() -> sqlite3.Connection:
    AUTH_DB.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(AUTH_DB)
    connection.row_factory = sqlite3.Row
    return connection


def _init_auth_db() -> None:
    with _connect_auth_db() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Consumer',
                password_hash TEXT NOT NULL,
                created_at INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at INTEGER NOT NULL,
                created_at INTEGER NOT NULL
            );
        """)
        # Seed default demo account
        demo_hash = _hash_password("Password123!")
        connection.execute(
            "INSERT OR IGNORE INTO users (email, name, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            ("demo@smartdeliver.ai", "Demo User", "Logistics Specialist", demo_hash, int(time.time()))
        )
_init_auth_db()


def _create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    with _connect_auth_db() as connection:
        connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
        connection.execute("INSERT INTO sessions(token_hash, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)", (_token_hash(token), user_id, now + SESSION_TTL_SECONDS, now))
    return token


def _current_user(authorization: str | None = Header(default=None)) -> dict:
    default_user = {"id": 1, "email": "demo@smartdeliver.ai", "name": "Demo User", "role": "Logistics Specialist"}
    if not authorization or not authorization.startswith("Bearer "):
        return default_user
    token = authorization.removeprefix("Bearer ").strip()
    now = int(time.time())
    try:
        with _connect_auth_db() as connection:
            row = connection.execute("""
                SELECT users.id, users.email, users.name, users.role
                FROM sessions JOIN users ON users.id = sessions.user_id
                WHERE sessions.token_hash = ? AND sessions.expires_at > ?
            """, (_token_hash(token), now)).fetchone()
        if row:
            return dict(row)
    except Exception:
        pass
    return default_user


def _normalize_uploaded_columns(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for column in frame.columns:
        key = str(column).strip().lower().replace(" ", "_").replace("-", "_")
        mapping = {
            "customerid": "customer_id",
            "customer_id": "customer_id",
            "orderid": "order_id",
            "order_id": "order_id",
            "orderdate": "order_date",
            "order_date": "order_date",
            "date": "order_date",
            "latitude": "latitude",
            "longitude": "longitude",
            "ordervalue": "order_value",
            "order_value": "order_value",
            "value": "order_value",
            "orders": "orders_count",
            "orders_count": "orders_count",
            "order_count": "orders_count",
            "deliverydistance": "delivery_distance_km",
            "delivery_distance": "delivery_distance_km",
            "delivery_distance_km": "delivery_distance_km",
            "area_name": "area",
            "area": "area",
        }
        renamed[column] = mapping.get(key, key)
    frame = frame.rename(columns=renamed)
    if "orders_count" not in frame.columns:
        frame["orders_count"] = 1
    if "area" not in frame.columns:
        frame["area"] = "Nanded"
    if "delivery_distance_km" not in frame.columns:
        frame["delivery_distance_km"] = 0.0
    return frame


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "SmartDeliver AI", "demo_mode": True}


@app.post("/api/login")
def login(body: dict):
    email = str(body.get("email", "")).strip().lower()
    password = str(body.get("password", ""))
    with _connect_auth_db() as connection:
        user = connection.execute("SELECT id, email, name, role, password_hash FROM users WHERE email = ?", (email,)).fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail="Account not found. Please create an account first.")
    if not _verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    token = _create_session(user["id"])
    return {"authenticated": True, "access_token": token, "token_type": "bearer", "expires_in": SESSION_TTL_SECONDS, "user": {"name": user["name"], "email": user["email"], "role": user["role"]}}


@app.post("/api/register")
def register(body: dict):
    email = str(body.get("email", "")).strip().lower()
    name = str(body.get("name", "")).strip()
    password = str(body.get("password", ""))
    confirm_password = str(body.get("confirm_password", ""))
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(status_code=422, detail="Enter a valid email address")
    if len(name) < 2 or len(name) > 80:
        raise HTTPException(status_code=422, detail="Enter your name")
    if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"\d", password):
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters and include uppercase, lowercase, and a number")
    if password != confirm_password:
        raise HTTPException(status_code=422, detail="Passwords do not match")
    try:
        with _connect_auth_db() as connection:
            cursor = connection.execute(
                "INSERT INTO users(email, name, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
                (email, name, "Consumer", _hash_password(password), int(time.time())),
            )
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
    return {"created": True, "user": {"name": name, "email": email, "role": "Consumer"}}


@app.post("/api/forgot-password")
def forgot_password(body: dict):
    email = str(body.get("email", "")).strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(status_code=422, detail="Enter a valid email address")
    # Keep the response generic so account existence is not disclosed.
    return {"sent": True, "message": "If an account exists for this email, reset instructions have been sent."}


@app.post("/api/logout")
def logout(authorization: str | None = Header(default=None)):
    if authorization and authorization.startswith("Bearer "):
        with _connect_auth_db() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (_token_hash(authorization.removeprefix("Bearer ").strip()),))
    return {"authenticated": False}


@app.get("/api/analyze")
def analyze(priority: str = Query("Balanced"), k: int = Query(4, ge=0, le=8), user: dict = Depends(_current_user)):
    return pipeline.run(priority=priority, k=k)


@app.post("/api/analyze")
def analyze_post(body: dict, user: dict = Depends(_current_user)):
    return pipeline.run(priority=body.get("priority", "Balanced"), k=int(body.get("k", 4)))


@app.get("/api/{resource}")
def resource(resource: str, user: dict = Depends(_current_user)):
    data = pipeline.payload
    mapping = {
        "customers": "customers",
        "orders": "customers",
        "population": None,
        "demand": "demand",
        "clusters": "clusters",
        "candidates": "candidates",
        "recommendations": "candidates",
        "analytics": "analytics",
        "existing-centers": "existing_centers",
        "map-data": None,
    }
    if resource not in mapping:
        raise HTTPException(status_code=404, detail="Unknown API resource")
    if resource == "map-data":
        return {"customers": data["customers"], "clusters": data["clusters"], "candidates": data["candidates"], "existing_centers": data["existing_centers"]}
    if resource == "population":
        population_path = DATA_DIR / "population.csv"
        if not population_path.exists():
            raise HTTPException(status_code=404, detail="Population dataset not found")
        return pd.read_csv(population_path).to_dict(orient="records")
    return data[mapping[resource]]


@app.get("/api/location/{candidate_id}")
def location(candidate_id: str, user: dict = Depends(_current_user)):
    for candidate in pipeline.payload["candidates"]:
        if candidate["candidate_id"] == candidate_id:
            return candidate
    raise HTTPException(status_code=404, detail="Candidate not found")


@app.post("/api/upload")
async def upload(file: UploadFile = File(...), priority: str = Query("Balanced"), k: int = Query(4, ge=0, le=8), user: dict = Depends(_current_user)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Upload file required")
    name = file.filename.lower()
    if not (name.endswith(".csv") or name.endswith(".xlsx") or name.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Upload a CSV or Excel file")
    try:
        raw = await file.read()
        if name.endswith((".xlsx", ".xls")):
            frame = pd.read_excel(io.BytesIO(raw))
        else:
            frame = pd.read_csv(io.BytesIO(raw))
        frame = _normalize_uploaded_columns(frame)
        required = {"order_id", "customer_id", "latitude", "longitude", "order_date", "order_value"}
        missing = sorted(required - set(frame.columns))
        if missing:
            raise HTTPException(status_code=422, detail={"missing_columns": missing})
        return pipeline.run(priority=priority, k=k, orders=frame)
    except pd.errors.ParserError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid CSV: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid file: {exc}") from exc


if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")
elif (FRONTEND_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST_DIR / "assets"), name="assets")
elif FRONTEND_DIST_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST_DIR), name="assets")


@app.get("/")
def frontend():
    index_path = FRONTEND_DIR / "index.html" if (FRONTEND_DIR / "index.html").exists() else FRONTEND_DIST_DIR / "index.html"
    return FileResponse(index_path)


@app.get("/{path:path}")
def frontend_routes(path: str):
    if path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Unknown API route")
    index_path = FRONTEND_DIR / "index.html" if (FRONTEND_DIR / "index.html").exists() else FRONTEND_DIST_DIR / "index.html"
    return FileResponse(index_path)
