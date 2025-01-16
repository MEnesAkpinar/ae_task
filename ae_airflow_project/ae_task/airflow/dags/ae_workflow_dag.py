# This Airflow DAG orchestrates the execution of the dbt models and Python scripts. It uses environment variables for Snowflake credentials.


from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import os


snowflake_config = {
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
}

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 10, 1),
    'retries': 1,
}

dag = DAG(
    'ae_workflow',
    default_args=default_args,
    description='Orchestrate AE Workflow',
    schedule_interval='@daily',
)


# Run dbt models
run_dbt_models = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd /opt/airflow/dags/ae_project && dbt run',
    dag=dag,
)

# Run fuzzy matching script
run_fuzzy_matching = PythonOperator(
    task_id='run_fuzzy_matching',
    python_callable=fuzzy_match,
    dag=dag,
)

# Define task dependencies
run_dbt_models >> run_fuzzy_matching