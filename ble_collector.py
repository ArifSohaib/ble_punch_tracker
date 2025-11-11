import asyncio, json, time, uuid
from bleak import BleakClient
from sqlalchemy.orm import Session
from datetime import datetime

from db import SessionLocal
from models import WorkoutSession, Reading

BLE_DEVICE_NAME = "Nano33BLE_JSON"
CHAR_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214"
NO_MOVEMENT_TIMEOUT = 10  # seconds

class BLECollector:
    def __init__(self):
        self.session_id = None
        self.client = None
        self.active = False
        self.last_movement = time.time()

    async def connect_and_listen(self):
        from bleak import BleakScanner
        device = await BleakScanner.find_device_by_name(BLE_DEVICE_NAME)
        if not device:
            print("BLE device not found")
            return

        async with BleakClient(device) as client:
            print("Connected to BLE device")
            self.client = client
            self.session_id = str(uuid.uuid4())
            self.create_session()
            self.active = True
            await client.start_notify(CHAR_UUID, self.notification_handler)
            try:
                while self.active:
                    await asyncio.sleep(1)
                    if time.time() - self.last_movement > NO_MOVEMENT_TIMEOUT:
                        print("No movement detected, stopping session...")
                        await self.stop()
                        break
            finally:
                await client.stop_notify(CHAR_UUID)
                print("Stopped notifications")

    def create_session(self):
        db = SessionLocal()
        session = WorkoutSession(id=self.session_id)
        db.add(session)
        db.commit()
        db.close()
        print(f"New session created: {self.session_id}")

    def notification_handler(self, sender, data):
        try:
            msg = json.loads(data.decode())
            x, y, z = msg.get("x"), msg.get("y"), msg.get("z")

            db = SessionLocal()
            db.add(Reading(session_id=self.session_id, x=x, y=y, z=z))
            db.commit()
            db.close()

            if abs(x) > 0.1 or abs(y) > 0.1 or abs(z) > 0.1:
                self.last_movement = time.time()
        except Exception as e:
            print("Error:", e)

    async def stop(self):
        self.active = False
        if self.client and self.client.is_connected:
            await self.client.disconnect()

        db = SessionLocal()
        session = db.query(WorkoutSession).filter_by(id=self.session_id).first()
        if session:
            session.end_time = datetime.now()
            db.commit()
        db.close()

        print(f"Session {self.session_id} ended.")
