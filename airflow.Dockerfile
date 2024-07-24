FROM apache/airflow:2.9.2-python3.9

USER airflow
# install your pip packages
RUN pip install --no-cache-dir \
    trino~=0.329.0 \
    apache-airflow-providers-trino~=5.7.2

COPY airflow-dags/trino_minio.py /opt/airflow/dags
COPY airflow-dags/trino_minio_advanced.py /opt/airflow/dags
COPY airflow-dags/plugins /opt/airflow/plugins