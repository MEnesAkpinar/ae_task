

This file provides instructions for setting up and running the project.


# AE_Task with Airflow on Docker

This project replicates Alteryx workflows using Python, SQL, dbt, and Airflow, running on Docker.



## Setup

1. **Install Docker Desktop**:
   - Download and install the Docker Desktop tool from (https://www.docker.com/products/docker-desktop).

2. **Clone the Project**:

   git clone <repo-url>
   cd airflow-docker


3. **Start Airflow**:

   docker-compose up
   

4. **Access the Airflow UI**:
   - Open a browser and go to `http://localhost:8081`.
   - Log in with the default credentials:
     - Username: `admin`
     - Password: `xyz12345`

5. **Trigger the DAG**:
   - In the Airflow UI, find the `ae_workflow` DAG and click the **Trigger DAG** button.

6. **Monitor the Task**:
   - Monitor the progress of the task in the Airflow UI.




##  **Commands to Run the Project**

1. **Start Airflow**:

   docker-compose up


2. **Stop Airflow**:
  
   docker-compose down
  

3. **Rebuild Airflow Images** (in case of updating the `Dockerfile` or `requirements.txt`):

   docker-compose up --build
