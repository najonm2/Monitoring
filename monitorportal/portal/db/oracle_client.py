# portal/db/oracle_client.py
from __future__ import annotations

from contextlib import contextmanager
import oracledb


# ---------------------------------------------------------
# HARD-CODED ORACLE CONNECTION CONFIG
# ---------------------------------------------------------
# Level3 Application Database (Informatica Repository)
DB_CONFIG = {
    "host": "azeus2loraipcp2.corp.intranet",
    "port": 1521,
    "service": "infr01p_app",
    "user": "icsm_appl",
    "password": "Infprd3_appl"
}

# MDM, ERP, ADF Applications Database (IICS CDI / Metadata Framework)
MAPDQPRD_DB_CONFIG = {
    "host": "RACORAP32-SCAN.CORP.INTRANET",
    "port": 1521,
    "service": "SVC_IDG01P",
    "user": "mapdqprd",
    "password": "2026NewIDMC"
}


# ---------------------------------------------------------
# CONNECTION POOLS (reuse connections instead of open/close)
# ---------------------------------------------------------
_pool = None
_pool_mapdqprd = None


def _get_pool() -> oracledb.ConnectionPool:
    """Lazy-init connection pool for INFA_PCREPO database."""
    global _pool
    if _pool is None:
        dsn = oracledb.makedsn(
            DB_CONFIG["host"],
            DB_CONFIG["port"],
            service_name=DB_CONFIG["service"]
        )
        _pool = oracledb.create_pool(
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            dsn=dsn,
            min=2,
            max=8,
            increment=1,
            getmode=oracledb.POOL_GETMODE_WAIT,
        )
    return _pool


def _get_pool_mapdqprd() -> oracledb.ConnectionPool:
    """Lazy-init connection pool for MAPDQPRD database."""
    global _pool_mapdqprd
    if _pool_mapdqprd is None:
        dsn = oracledb.makedsn(
            MAPDQPRD_DB_CONFIG["host"],
            MAPDQPRD_DB_CONFIG["port"],
            service_name=MAPDQPRD_DB_CONFIG["service"]
        )
        _pool_mapdqprd = oracledb.create_pool(
            user=MAPDQPRD_DB_CONFIG["user"],
            password=MAPDQPRD_DB_CONFIG["password"],
            dsn=dsn,
            min=2,
            max=8,
            increment=1,
            getmode=oracledb.POOL_GETMODE_WAIT,
        )
    return _pool_mapdqprd


# ---------------------------------------------------------
# CONNECTION CREATION (now uses pool)
# ---------------------------------------------------------
def get_conn() -> oracledb.Connection:
    """
    Returns a connection from the pool (much faster than creating new ones).
    """
    try:
        return _get_pool().acquire()
    except Exception:
        # Fallback to direct connection if pool fails
        dsn = oracledb.makedsn(
            DB_CONFIG["host"],
            DB_CONFIG["port"],
            service_name=DB_CONFIG["service"]
        )
        return oracledb.connect(
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            dsn=dsn
        )


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
    Configured to handle LONG and CLOB fields up to 10MB.
    """
    with oracle_cursor() as cur:
        # Configure cursor to handle large LONG and CLOB fields
        cur.arraysize = 100
        # Set large output size for LONG columns (10MB limit)
        cur.setoutputsize(10000000)
        
        cur.execute(sql, params or {})
        
        # Get column info and check for LONG types
        cols = [c[0].lower() for c in cur.description]
        
        # Fetch all rows and convert LOB objects to strings
        rows = []
        for row in cur.fetchall():
            row_dict = {}
            for col_name, value in zip(cols, row):
                # Handle CLOB/BLOB objects by reading them  
                if hasattr(value, 'read'):
                    try:
                        row_dict[col_name] = value.read()
                    except:
                        row_dict[col_name] = str(value)
                else:
                    row_dict[col_name] = value
            rows.append(row_dict)
        
        return rows


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


# ---------------------------------------------------------
# MAPDQPRD DATABASE CONNECTION (MDM, ERP, ADF)
# ---------------------------------------------------------
def get_mapdqprd_conn() -> oracledb.Connection:
    """
    Returns a connection from the MAPDQPRD pool (much faster than creating new ones).
    """
    try:
        return _get_pool_mapdqprd().acquire()
    except Exception:
        # Fallback to direct connection if pool fails
        dsn = oracledb.makedsn(
            MAPDQPRD_DB_CONFIG["host"],
            MAPDQPRD_DB_CONFIG["port"],
            service_name=MAPDQPRD_DB_CONFIG["service"]
        )
        return oracledb.connect(
            user=MAPDQPRD_DB_CONFIG["user"],
            password=MAPDQPRD_DB_CONFIG["password"],
            dsn=dsn
        )


@contextmanager
def mapdqprd_cursor():
    """
    Context manager for MAPDQPRD database
    Usage:
        with mapdqprd_cursor() as cur:
            cur.execute("select * from MAPDQPRD.IICS_CDI_RUN_INFO")
            rows = cur.fetchall()
    """
    conn = get_mapdqprd_conn()
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


def fetch_all_mapdqprd(sql: str, params: dict | None = None) -> list[dict]:
    """
    Returns all rows from MAPDQPRD database as a list of {column: value} dicts.
    Column names are converted to lowercase.
    Used for MDM, ERP, and ADF queries.
    """
    with mapdqprd_cursor() as cur:
        cur.execute(sql, params or {})
        cols = [c[0].lower() for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]