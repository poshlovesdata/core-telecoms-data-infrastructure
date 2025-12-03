import os
from airflow.providers.slack.operators.slack import SlackAPIPostOperator
import logging
from datetime import datetime


def task_failure_alert(context):
    """
    Sends a Slack alert using SlackAPIPostOperator via env variable connection.
    """
    dag_id = context["dag"].dag_id
    task_id = context["task_instance"].task_id
    execution_date = context.get("logical_date") or context.get("execution_date")
    log_url = context["task_instance"].log_url
    error = str(context.get("exception"))
    logger = logging.getLogger("airflow.task")

    message = f"""
🚨 *Airflow Task Failed!*
*DAG:* `{dag_id}`
*Task:* `{task_id}`
*Execution:* `{execution_date}`
*Error:* `{error}`
🔗 <{log_url}|View Logs>
"""

    try:
        alert = SlackAPIPostOperator(
            task_id="slack_failure_alert",
            slack_conn_id="slack_conn",  # uses env var connection
            text=message,
            username="TheEngine",
            channel="#airflow",
        )
        alert.execute(context=context)
        logger.info("Slack alert sent via SlackAPIPostOperator.")
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")


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
