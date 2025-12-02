# CharlesS
Python version 3.10.0 Web API Testbed

# Create the Env name cenv 
D:\DC\Charles>conda create -p cenv python==3.10.0
D:\DC\Udemy\AgentRAG>conda activate cenv\

# Run the necessary libaries for cenv
(D:\DC\Charles\cenv) D:\DC\Charles>pip install -r requirements-cs.txt 

# Run the program
(D:\DC\Charles\cenv) D:\DC\Charles>python health_checker.py

# uvicorn load
(D:\DC\Charles\cenv) D:\DC\Charles>uvicorn health_checker:app --reload

# Check the API
http://127.0.0.1:8000/docs#/default/perform_health_check_healthcheck_post

# Sample Request (JSON Body)

Use the following JSON body for the sample DAG you provided:
{
    "relationships": {
        "User Interface": ["API Gateway"],
        "API Gateway": ["Auth Service", "Billing Service", "Order Service"],
        "Auth Service": ["Database", "Cache"],
        "Billing Service": ["Database"],
        "Order Service": ["Inventory Service", "Database"],
        "Inventory Service": ["Database"]
    }
}

# System Health Check Complete (Time: 0.19s) ---
Component            Status     Details
------------------------------------------------------------
API Gateway          UP         OK
Auth Service         UP         OK
Billing Service      UP         OK
Cache                UP         OK
Database             UP         OK
Inventory Service    UP         OK
Order Service        UP         OK
User Interface       UP         OK

------------------------------------------------------
INFO:     127.0.0.1:56799 - "POST /healthcheck HTTP/1.1" 200 OK

# Check the graph
https://www.onlinewebtoolkit.com/base64-to-image-converter
Copy and Paste to see the graph_image_base64 : 

