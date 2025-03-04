import os
import subprocess
import sys

# Install requirements.txt if packages are missing
def install_requirements():
    try:
        import fastapi, uvicorn, pandas  # Try importing modules
    except ImportError:
        print("Installing missing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Run the installation check before importing dependencies
install_requirements()

# Now import libraries
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

# Ensure 'uploads' directory exists
os.makedirs("uploads", exist_ok=True)

# Function to process hockey data (Time on Ice Calculation)
def process_hockey_data(file_path: str):
    df = pd.read_csv(file_path)  # Read CSV file
    if "player" not in df.columns or "time_on_ice" not in df.columns:
        raise ValueError("CSV must contain 'player' and 'time_on_ice' columns")

    # Sum total time on ice per player
    time_on_ice = df.groupby("player")["time_on_ice"].sum().reset_index()
    
    # Convert to dictionary format
    processed_data = time_on_ice.to_dict(orient="records")

    # Save processed data
    with open("processed_data.json", "w") as f:
        import json
        json.dump(processed_data, f)

    return processed_data

# API Endpoint to Upload Hockey Data
@app.post("/upload_hockey/")
async def upload_hockey_data(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    try:
        processed_data = process_hockey_data(file_path)
        return {"message": "Hockey data processed successfully", "data": processed_data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Load Processed Data
def load_processed_data():
    import json
    if os.path.exists("processed_data.json"):
        with open("processed_data.json", "r") as f:
            return json.load(f)
    return []

# API Endpoint to Get Player Stats
@app.get("/player_stats/")
async def get_player_stats(player: str):
    data = load_processed_data()
    
    # Search for player's time on ice
    player_stats = next((p for p in data if p["player"] == player), None)
    
    if player_stats:
        return {"player": player, "time_on_ice": player_stats["time_on_ice"]}
    
    raise HTTPException(status_code=404, detail="Player not found")
