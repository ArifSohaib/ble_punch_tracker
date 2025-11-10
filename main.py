from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import text, select
from fastapi.responses import JSONResponse

from db import Base, SessionLocal, engine, get_db
from models import Reading, WorkoutSession
from ble_collector import BLECollector
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import json_item
import pandas as pd 

app = FastAPI()
templates = Jinja2Templates(directory="templates")
collector = BLECollector()

# create tables
Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Fetch sessions from DB
    with SessionLocal() as db:
        sessions = db.execute(select(WorkoutSession).order_by(WorkoutSession.start_time.desc())).scalars().all()
    return templates.TemplateResponse("index.html", {"request": request, "sessions": sessions})


@app.get("/debug/sessions")
async def debug_sessions():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM sessions ORDER BY start_time DESC LIMIT 10"))
        rows = [dict(row._mapping) for row in result]
    return JSONResponse(rows)

@app.get("/debug/readings")
async def debug_sessions():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM readings ORDER BY session_id DESC"))
        rows = [dict(row._mapping) for row in result]
    return JSONResponse(rows)

@app.get("/session/{session_id}")
def get_session(session_id: str):
    with SessionLocal() as db:
        session = db.query(WorkoutSession).filter(WorkoutSession.id == session_id).first()
        data = db.query(Reading).filter(Reading.session_id == session.id).all()

    indices = list(range(len(data)))  # Use index as x-axis
    values_x = [d.x for d in data]  # Acceleration magnitude
    values_y = [d.y for d in data]
    values_z = [d.z for d in data]
    p = figure(title="Punch Acceleration", x_axis_label="Reading #", y_axis_label="Acceleration")
    p.line(indices, values_x, line_width=2, color='red', legend_label='x-axis acc')
    p.line(indices, values_y, line_width=2, color='green', legend_label='y-axis acc')
    p.line(indices, values_z, line_width=2, color='blue', legend_label='z-axis acc')

    return json_item(p)

@app.post("/start")
async def start_collection(background_tasks: BackgroundTasks):
    background_tasks.add_task(collector.connect_and_listen)
    return {"status": "started"}

@app.post("/stop")
async def stop_collection():
    await collector.stop()
    return {"status": "stopped"}


