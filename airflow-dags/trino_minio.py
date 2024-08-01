from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from datetime import datetime
import pandas as pd
import boto3


def process_data(**context):
    task_instance = context['ti']
    query_results = task_instance.xcom_pull(task_ids='execute_query')

    column_name = ['sale_id', 'sale_date', 'customer_name', 'product_name', 'category', 'quantity', 'price', 'discount',
                   'region', 'sales_rep', 'total']
    df = pd.DataFrame(query_results, columns=column_name)

    df.to_csv('/tmp/processed_data.csv', index=False)


dag = DAG(
    'presto_minio_workflow',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False
)

query_task = SQLExecuteQueryOperator(
    task_id='execute_query',
    conn_id="trino_conn_id",
    sql="SELECT * FROM rdbms.public.sales",
    handler=list
)

process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    provide_context=True,
    dag=dag
)

upload_task = LocalFilesystemToS3Operator(
    task_id='upload_to_minio',
    filename='/tmp/processed_data.csv',
    dest_key='processed_data/processed_data.csv',
    dest_bucket='minio-airflow',
    aws_conn_id='my_s3_conn',
    replace=True,
    dag=dag
)

query_task >> process_task >> upload_task

