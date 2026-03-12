**TimeSlice: F1 Telemetry & Performance Insights API**
======================================================

An N-tier asynchronous Python API built with FastAPI, SQLAlchemy, and Pydantic to transform raw OpenF1 telemetry into actionable racing insights.

*   **PDF API  Documentation** [F1APIDocumentaion.pdf](https://github.com/SamHurst47/Web_Ser_API/blob/main/Documentation/F1APIDocumentaion.pdf) Interactive documentation is also available via the links below.
    
*   **Technical Report:** [Technical Report](https://github.com/SamHurst47/Web_Ser_API/blob/main/Documentation/Deliverable/Technical%20Report.pdf)

*   **Presentation Slides** [Presentation Slides](https://github.com/SamHurst47/Web_Ser_API/blob/main/Documentation/TimeSlice%20F1%20API%20SH.pptx)

*   **Presentation Demo** [Presentation Demo]()

*   **AI Documentation** [AI Documentation](https://github.com/SamHurst47/Web_Ser_API/tree/main/Documentation/AIUsage) 

**🏁 Remote Access (Production)**
---------------------------------

The API is currently deployed on **Render** and can be accessed via the following links:

*   **Production URL:** [https://web-ser-api.onrender.com](https://web-ser-api.onrender.com)

*   **Interactive Documentation (Swagger):** [https://web-ser-api.onrender.com/docs](https://www.google.com/search?q=https://web-ser-api.onrender.com/docs)
    
*   **Redoc Documentation:** [https://web-ser-api.onrender.com/redoc](https://www.google.com/search?q=https://web-ser-api.onrender.com/redoc)



Note on Calling Endpoints: To call specific endpoints (e.g., /api/v1/analytics/true-pace), append the endpoint path to the Base Production URL as detailed in the Swagger or Redoc documentation above.

** # 🛠 Local Setup Instructions **
---------------------------------

This is for development purposes only and should not be followed unless you have access to the connection string for the database.

### **1. Initialise Environment**

Create and activate a virtual environment to manage dependencies:


Create the environment
```
python3 -m venv venv
```

Activate (macOS/Linux)
```
source venv/bin/activate
```

Activate (Windows)
```
venv\Scripts\activate
```


***

### **2. Install Dependencies**

```
pip install -r requirements.txt
```


***

### **3. Environment Configuration**

Create a `.env` file in the root directory.
This file is required for both the application and the testing suite to connect to the database and handle security.

```
DATABASE_URL=InsertURLHere
```


***

# 🧪 Testing Suite

The project uses **Pytest** for automated unit and integration testing.
These tests simulate a client to verify endpoint functionality and database persistence.

### **To Run All Tests:**

Ensure your virtual environment is active and running:

```
pytest
```


### **To Run with Verbose Output:**

```
pytest -v
```


***

# 🚀 Running the Local Server

To start the API locally for development:

```
uvicorn main:app --reload
```
Once started, you can access the local docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

-------------------------------

(ReadMe Created Using GenAI as in GenAI declaration)
