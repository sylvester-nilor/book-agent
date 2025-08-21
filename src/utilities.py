import os
from datetime import datetime

import google.auth
from google.cloud import bigquery
from googleapiclient.discovery import build

from tag import TAG


def execute_script(project_id, sql_file_path, verbose=True):
    # Ensure the sql_file_path is an absolute path
    if not os.path.isabs(sql_file_path):
        # Assuming the script is located in the src directory, adjust the path accordingly
        base_path = os.path.dirname(__file__)
        sql_file_path = os.path.join(base_path, sql_file_path)

    sql_file_path = os.path.abspath(sql_file_path)

    print(f"{TAG} query: start. file: {sql_file_path}")

    try:
        with open(sql_file_path, 'r') as file_stream:
            sql_text = file_stream.read()
            execute_query(project_id, sql_text, verbose)
    except FileNotFoundError:
        print(f"Error: The file {sql_file_path} does not exist.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    print(f"{TAG} query: complete. file: {sql_file_path}")


def execute_query(project_id, query_text, verbose=True):
    if verbose:
        print(f"{TAG} query_text: \n{query_text}")

    with bigquery.Client(project=project_id) as client:
        query_job = client.query(query_text)
        return query_job.result()  # Waits for job to complete.


def insert_rows(project_id, dataset_id, table_id, rows, verbose=True):
    if verbose:
        print(f"{TAG} insert_rows: start. dataset: {dataset_id}, table: {table_id}, rows: {len(rows)}")

    with bigquery.Client(project=project_id) as client:
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        errors = client.insert_rows_json(table_ref, rows)

        if errors:
            print(f"{TAG} insert_rows: errors: {errors}")
            return False
        else:
            print(f"{TAG} insert_rows: success. inserted {len(rows)} rows")
            return True
