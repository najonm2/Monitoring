# portal/services/level3_service.py
from portal.db.oracle_client import fetch_all, fetch_kv
from portal.sql.level3_queries import MAIN_QUERY, SUMMARY_QUERY, LONG_RUNNING_QUERY, clean_sql


def get_level3_failed_jobs():
    """
    Returns:
      summary_map: dict -> {TOTAL_FAILED_JOBS:..., COMPLETED_JOBS:...}
      main_rows: list[dict]
      long_rows: list[dict]
    """
    main_rows = fetch_all(clean_sql(MAIN_QUERY))
    summary_map = fetch_kv(clean_sql(SUMMARY_QUERY))
    long_rows = fetch_all(clean_sql(LONG_RUNNING_QUERY))
    return summary_map, main_rows, long_rows