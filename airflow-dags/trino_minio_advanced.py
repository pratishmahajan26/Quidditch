from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from  airflow.operators.python import BranchPythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta
import pandas as pd
import os

from operators.validation_operator import DataValidationOperator


def process_data(**context):
    task_instance = context['ti']
    query_results = task_instance.xcom_pull(task_ids='execute_query')

    column_name = ['sale_id', 'sale_date', 'customer_name', 'product_name', 'quantity', 'price', 'total']
    df = pd.DataFrame(query_results, columns=column_name)

    if df.empty:
        raise ValueError("No data returned from query.")

    processed_path = '/tmp/processed_data.csv'
    df.to_csv(processed_path, index=False)

    return processed_path


def notify_failure(context):
    return {
        'subject': f"Task Failed: {context['task_instance'].task_id}",
        'html_content': f"<p>Task {context['task_instance'].task_id} failed. Please check the logs for more details.</p>"
    }


def notify_success(context):
    return {
        'subject': "Workflow Completed Successfully",
        'html_content': "<p>The workflow has completed successfully. All tasks have been executed without errors.</p>"
    }


def check_validation(**context):
    validation_result = context['ti'].xcom_pull(task_ids='validate_data')
    print(f"validation_result {validation_result}")
    if validation_result == 'success':
        return 'upload_to_minio'
    else:
        return 'notify_failure'


dag = DAG(
    'presto_minio_advanced_workflow',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False,
    default_args={
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
    }
)

query_task = SQLExecuteQueryOperator(
    task_id='execute_query',
    conn_id="trino_conn_id",
    sql="SELECT * FROM rdbms.public.sales",
    handler=list,
    dag=dag
)

process_task = PythonOperator(
    task_id='process_data',
    python_callable=process_data,
    provide_context=True,
    dag=dag
)

validate_task = DataValidationOperator(
    task_id='validate_data',
    input_file_path='/tmp/processed_data.csv',
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

# notify_success_task = EmailOperator(
#     task_id='notify_success',
#     to='recipient@example.com',
#     subject='Workflow Completed Successfully',
#     html_content='<p>The workflow has completed successfully. All tasks have been executed without errors.</p>',
#     dag=dag
# )

notify_failure_task = EmailOperator(
    task_id='notify_failure',
    to='recipient@example.com',
    subject='Task Failed',
    html_content='<p>Task {{ task_instance.task_id }} failed. Please check the logs for more details.</p>',
    dag=dag
)

check_validation_task = BranchPythonOperator(
    task_id='check_validation',
    python_callable=check_validation,
    provide_context=True,
    dag=dag
)


# def choose_branch_notify(**context):
#     file_path = context['task_instance'].xcom_pull(task_ids='upload_task')
#     if os.path.getsize(file_path) > 0:
#         return 'upload_to_minio'
#     else:
#         return 'dummy_failure'

# branch_task_notify = BranchPythonOperator(
#     task_id='branch_notify',
#     python_callable=choose_branch_notify,
#     provide_context=True,
#     dag=dag
# )

# dummy_failure = DummyOperator(
#     task_id='dummy_failure',
#     dag=dag
# )

query_task >> process_task >> validate_task >> check_validation_task >> [upload_task, notify_failure_task]
