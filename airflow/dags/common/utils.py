import os
from airflow.providers.smtp.operators.smtp import EmailOperator

import logging
from datetime import datetime


def task_failure_alert(context):
    """Send an HTML email with task failure details and a link to logs."""
    dag_id = context.get("dag").dag_id
    task_id = context.get("task_instance").task_id
    execution_date = context.get("execution_date")
    log_url = context.get("task_instance").log_url
    exception = context.get("exception")

    subject = f"Airflow Alert: {dag_id} - Task {task_id} Failed"
    html_content = f"""
    <h3>Airflow Task Failed</h3>
    <p><b>DAG:</b> {dag_id}</p>
    <p><b>Task:</b> {task_id}</p>
    <p><b>Execution Date:</b> {execution_date}</p>
    <p><b>Error:</b> {exception}</p>
    <p><b>Logs:</b> <a href="{log_url}">View Logs</a></p>
    """

    email = EmailOperator(
        task_id="failure_notification",
        from_email=f'{os.getenv("FROM_EMAIL")}',
        to=["poshlovesdata@gmail.com"],
        subject=subject,
        html_content=html_content,
        conn_id="smtp_conn",
    )
    email.execute(context=context)


def get_source_s3():
    """Helper functioon to get S3 Client"""
    import boto3
    from dotenv import load_dotenv

    load_dotenv()

    logger = logging.getLogger("airflow.task")

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    logger.info("Connecting to S3 Client")
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION,
    )


def get_logical_date():
    """Get airflow context for runtime variables. this returns a date"""
    from airflow.sdk import get_current_context

    logger = logging.getLogger("airflow.task")
    try:
        context = get_current_context()

        logical_date = context["logical_date"]  # type: ignore
        return logical_date
    except Exception as e:
        # Fallback for local testing (when no airflow context exists)
        logger.warning(
            f"No Airflow context found. Using datetime.now() for local test: {e}"
        )
        logical_date = datetime.now()
        return logical_date
