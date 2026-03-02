**TimeSlice: F1 Telemetry & Performance Insights API**
======================================================

An N-tier asynchronous Python API built with FastAPI, SQLAlchemy, and Pydantic to transform raw OpenF1 telemetry into actionable racing insights.

**🏁 Remote Access (Production)**
---------------------------------

The API is currently deployed on **Render** and can be accessed via the following links:

*   **Production URL:** [https://web-ser-api.onrender.com](https://web-ser-api.onrender.com) 
    
*   **Interactive Documentation (Swagger):** [https://web-ser-api.onrender.com/docs](https://www.google.com/search?q=https://web-ser-api.onrender.com/docs)
    
*   **Redoc Documentation:** [https://web-ser-api.onrender.com/redoc](https://www.google.com/search?q=https://web-ser-api.onrender.com/redoc)

Note on Calling Endpoints: To call specific endpoints (e.g., /api/v1/analytics/true-pace), append the endpoint path to the Base Production URL as detailed in the Swagger or Redoc documentation above.

**🛠 Local Setup Instructions**
-------------------------------

### **1\. Initialize Environment**

Create and activate a virtual environment to manage dependencies:

Bash

\# Create the environmentpython3 -m venv venv# Activate (macOS/Linux)source venv/bin/activate# Activate (Windows)# venv\\Scripts\\activate

### **2\. Install Dependencies**

Bash

pip install -r requirements.txt

### **3\. Environment Configuration**

Create a .env file in the root directory. This is required for both the application and the testing suite to communicate with the database and handle security.

Bash

DATABASE\_URL=postgresql://user:password@azure-host:5432/dbnameSECRET\_KEY=your\_super\_secret\_jwt\_keyALGORITHM=HS256ACCESS\_TOKEN\_EXPIRE\_MINUTES=30

**🧪 Testing Suite**
--------------------

The project uses **Pytest** for automated unit and integration testing. These tests simulate a client to verify endpoint functionality and database persistence.

### **To Run All Tests:**

Ensure your virtual environment is active and run:

Bash

pytest

### **To Run with Verbose Output:**

Bash

pytest -v

**🚀 Running the Local Server**
-------------------------------

To start the API locally for development:

Bash

uvicorn main:app --reload

Once started, you can access the local docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

-------------------------------

(ReadMe Created Using GenAI as in GenAI declaration)