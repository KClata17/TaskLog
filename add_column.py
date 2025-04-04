from app import db, app
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as connection:
        connection.execute(text('ALTER TABLE TaskLog ADD COLUMN status TEXT DEFAULT "Pending";'))

print("Column 'status' added successfully!")
