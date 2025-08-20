import os
import json
import time
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from utilities import execute_script, execute_query, insert_rows


class AgentService:
    def __init__(self, project_id: str):
        self.project_id = project_id

    # def search(self, search_text: str, limit: int) -> List[Dict[str, Any]]:
    #     search_id = str(uuid.uuid4())
    #     start_time = time.time()
    #     error_message = None
    #     results = []
    #
    #     try:
    #         execute_script(project_id=self.project_id, sql_file_path="bigquery/bq_ddl.sql", verbose=True)
    #
    #         query = f"""
    #         SELECT * FROM book_agent_v1.search_paragraphs('{search_text.replace("'", "\\'")}')
    #         LIMIT {limit}
    #         """
    #         result_iterator = execute_query(project_id=self.project_id, query_text=query, verbose=True)
    #
    #         if result_iterator:
    #             result_list = list(result_iterator)
    #             results = [
    #                 {
    #                     "book_id": row["book_id"],
    #                     "paragraph_id": row["paragraph_id"],
    #                     "page_number": row["page_number"],
    #                     "start_char": row["start_char"],
    #                     "end_char": row["end_char"],
    #                     "content": row["content"],
    #                     "similarity_score": row["similarity_score"],
    #                     "inserted_at": row["inserted_at"].isoformat() if row["inserted_at"] else None
    #                 }
    #                 for row in result_list
    #             ]
    #     except Exception as e:
    #         error_message = str(e)
    #         print(f"Error in search: {error_message}")
    #
    #     execution_time = time.time() - start_time
    #
    #     self._log_search(
    #         search_id=search_id,
    #         search_text=search_text,
    #         result_count=len(results),
    #         execution_time=execution_time,
    #         error_message=error_message,
    #         results_json=json.dumps(results) if results else None
    #     )
    #
    #     return results
    #
    # def _log_search(self, search_id: str, search_text: str, result_count: int,
    #                 execution_time: float, error_message: Optional[str] = None,
    #                 results_json: Optional[str] = None) -> None:
    #     try:
    #         search_log = {
    #             "search_id": search_id,
    #             "search_text": search_text,
    #             "result_count": result_count,
    #             "execution_time": execution_time,
    #             "error_message": error_message,
    #             "results_json": results_json,
    #             "inserted_at": datetime.now(timezone.utc).isoformat()
    #         }
    #
    #         insert_rows(
    #             project_id=self.project_id,
    #             dataset_id="book_agent_v1",
    #             table_id="searches_v1",
    #             rows=[search_log],
    #             verbose=True
    #         )
    #     except Exception as e:
    #         print(f"Error logging search: {str(e)}")


if __name__ == "__main__":
    _project_id = os.getenv("GCP_PROJECT", "robot-rnd-nilor-gcp")

    _service = AgentService(project_id=_project_id)
    # _result = _service.search(search_text="network state governance digital sovereignty", limit=10)
    # print(f"Search result: {_result}")
