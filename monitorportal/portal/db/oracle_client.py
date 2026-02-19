# portal/db/oracle_client.py
from __future__ import annotations

from contextlib import contextmanager
import oracledb


# ---------------------------------------------------------
# HARD-CODED ORACLE CONNECTION CONFIG
# ---------------------------------------------------------
DB_CONFIG = {
    "host": "azeus2loraipcp2.corp.intranet",
    "port": 1521,
    "service": "infr01p_app",
    "user": "icsm_appl",
    "password": "icsm_appl_infprd"
}


# ---------------------------------------------------------
# CONNECTION CREATION
# ---------------------------------------------------------
def get_conn() -> oracledb.Connection:
    """
    Creates and returns a new Oracle DB connection
    using python-oracledb with keyword arguments.
    """
    dsn = oracledb.makedsn(
        DB_CONFIG["host"],
        DB_CONFIG["port"],
        service_name=DB_CONFIG["service"]
    )

    conn = oracledb.connect(
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        dsn=dsn
    )
    return conn


# ---------------------------------------------------------
# CURSOR CONTEXT MANAGER
# ---------------------------------------------------------
@contextmanager
def oracle_cursor():
    """
    Usage:
        with oracle_cursor() as cur:
            cur.execute("select 1 from dual")
            rows = cur.fetchall()
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        yield cur
    finally:
        try:
            cur.close()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass


# ---------------------------------------------------------
# FETCH HELPERS
# ---------------------------------------------------------
def fetch_all(sql: str, params: dict | None = None) -> list[dict]:
    """
    Returns all rows as a list of {column: value} dicts.
    Column names are converted to lowercase.
    """
    with oracle_cursor() as cur:
        cur.execute(sql, params or {})
        cols = [c[0].lower() for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def fetch_kv(sql: str) -> dict:
    """
    For queries that return: METRIC_KEY, METRIC_VALUE
    Returns:
        {"TOTAL_FAILED_JOBS": 10, "COMPLETED_JOBS": 5, ...}
    """
    rows = fetch_all(sql)
    out = {}
    for r in rows:
        key = str(r.get("metric_key", "")).strip()
        out[key] = r.get("metric_value", 0)
    return out