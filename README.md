Create and use a Python virtual environment to isolate and run your project dependencies.

## 1. Create Virtual Environment

```
python3 -m venv venv
```

## 2. Activate Virtual Environment

```
source venv/bin/activate
```

## 3. Install Requirements

```
pip install -r requirements.txt
```

## 4. Run Project

```
python3 main.py
```

## 5. Deactivate Virtual Environment

```
deactivate
```

## 6. To Run

```
uvicorn app.main:app --reload
```
## 6. Open in Browser 
Normal Mode
```
http://127.0.0.1:8000
```
Testing mode 
```
http://127.0.0.1:8000/docs#/
```
