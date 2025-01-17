FROM apache/airflow:2.5.1

ARG DEST_INSTALL=/home/airflow

# Switch to the root user to perform setup tasks
USER root

# Install system dependencies (if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to the airflow user
USER airflow

WORKDIR ${DEST_INSTALL}

ENV PATH=${PATH}:/home/airflow/.local/bin

# Copy the requirements.txt file into the container
COPY requirements.txt /requirements.txt

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

ENV PYTHONPATH="${AIRFLOW_HOME}:${PYTHONPATH}"

# Set environment variables for Airflow
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW_CORE_LOAD_EXAMPLES=False
ENV AIRFLOW_CORE_EXECUTOR=LocalExecutor
ENV AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
ENV AIRFLOW_WEBSERVER_SECRET_KEY=your-secret-key
ENV AIRFLOW_WEBSERVER_EXPOSE_CONFIG=True

USER root
COPY ./dags/ ${AIRFLOW_HOME}/dags/
COPY ./dbt/ ${AIRFLOW_HOME}/dbt/
COPY ./pipeline/ ${AIRFLOW_HOME}/pipeline/


RUN chown -R "airflow" "${AIRFLOW_HOME}"
USER airflow
WORKDIR ${AIRFLOW_HOME}/dbt

WORKDIR ${AIRFLOW_HOME}