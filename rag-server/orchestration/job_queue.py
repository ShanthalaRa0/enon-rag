# orchestration/job_queue.py
# Separates queues by workload.

# Example:

# ocr_queue
# embedding_queue
# search_queue
# llm_queue
# rerank_queue

from queue import Queue


ingestion_queue = Queue()


def enqueue_job(
    file_path,
):
    """
    Add ingestion job to queue.
    """

    ingestion_queue.put(
        file_path
    )


def dequeue_job():
    """
    Get next ingestion job.
    """

    return ingestion_queue.get()