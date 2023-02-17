from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.apache.beam.operators.beam import BeamRunPythonPipelineOperator
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 2, 17),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('puppeteer_scraper_dag', default_args=default_args,
          schedule_interval='@once')

# Define the list of websites to scrape and the corresponding MongoDB databases to store the scraped data
websites = [
    {'url': 'https://example.com', 'db_name': 'example_db'},
    {'url': 'https://example2.com', 'db_name': 'example2_db'},
    {'url': 'https://example3.com', 'db_name': 'example3_db'},
]

# Define the list of tasks to scrape the data from the websites using Puppeteer and store it in MongoDB
tasks = []
for website in websites:
    task_id = f'scrape_{website["db_name"]}'
    task_command = f'node /puppeteer/scraper.js --url {website["url"]} --db {website["db_name"]}'
    task = BashOperator(task_id=task_id, bash_command=task_command, dag=dag)
    tasks.append(task)

# Define the task to merge the data from the different MongoDB databases using Apache Beam
merge_data = BeamRunPythonPipelineOperator(
    task_id='merge_data',
    py_file='/beam/merge_script.py',
    pipeline_options={
        'mongo_db': [website['db_name'] for d in websites]
        'runner': 'DirectRunner',
        'input_uris': [
            f'mongodb://localhost/{website["db_name"]}.collection' for website in websites
        ],
        'output_uri': 'mongodb://localhost/merged_data.collection'
    },
    dag=dag
)

# Define the task to stream the merged data to Kafka
# stream_data = BashOperator(
#     task_id='stream_data',
#     bash_command='python /path/to/kafka/stream_script.py',
#     dag=dag
# )

# Define the task dependencies
for task in tasks:
    task >> merge_data

# merge_data >> stream_data
