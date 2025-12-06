FROM apache/airflow:3.0.6

USER root

# Install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER airflow

COPY --chown=airflow:root dags /opt/airflow/dags
COPY --chown=airflow:root dbt /opt/airflow/dbt

# Install custom requirements
COPY requirements.txt requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Install Airflow dependencies (Excluding dbt) using strict constraints
# Remove dbt packages here to prevent conflict with Airflow's pinned versions
RUN grep -vE "dbt-snowflake|dbt-core|dbt-postgres" requirements.txt > requirements_airflow.txt \
    && pip install --no-cache-dir -r requirements_airflow.txt -c https://raw.githubusercontent.com/apache/airflow/constraints-3.0.6/constraints-3.10.txt

# Install dbt-snowflake explicitly
# Install it without constraints so it can resolve its own deps.
RUN pip install --no-cache-dir dbt-snowflake==1.8.4
