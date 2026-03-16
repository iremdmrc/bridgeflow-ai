from db import init_db, seed_sample_data

print("Initializing database...")

init_db()
seed_sample_data()

print("Database initialized successfully.")