pip install -r requirements.txt
pip install fastapi uvicorn pandas
pip install python-multipart
uvicorn API:app --reload
http://127.0.0.1:8000/docs