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

# Install custom requirements
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
