from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from pipeline.fuzzy_matching import fuzzy_match
import os


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
    bash_command='cd /opt/airflow/dags/ae_task && dbt run',
    dag=dag,
)

# Run fuzzy matching script
run_fuzzy_matching = PythonOperator(
    task_id='run_fuzzy_matching',
    python_callable=fuzzy_match,
    dag=dag,
)

# Defined task dependencies
run_dbt_models >> run_fuzzy_matching