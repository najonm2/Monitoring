# Daylight Saving Time (DST) Automation Guide

**Date:** March 9, 2026  
**Issue:** BI queries had hardcoded timezone offsets that required manual updates twice a year  
**Solution:** Implemented automatic DST handling using Oracle's timezone functions

---

## ✅ What Was Changed

### **Before (Manual Update Required):**
```sql
-- Had to change from 7 to 6 hours in March, and back to 7 in November
MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR') AS end_dt_in_mst

-- CAPEX also needed manual updates
new_time(start_dt,'GMT','MST')  -- Change to 'MDT' in March, back to 'MST' in November
```

### **After (Automatic DST Handling):**
```sql
-- Automatically adjusts for DST - no more manual updates!
CAST(FROM_TZ(CAST(MAX(end_dt) AS TIMESTAMP), 'UTC') AT TIME ZONE 'America/Denver' AS DATE)

-- CAPEX also automatic now
CAST(FROM_TZ(CAST(start_dt AS TIMESTAMP), 'UTC') AT TIME ZONE 'America/Denver' AS DATE)
```

---

## 🔧 How It Works

**`America/Denver` timezone:**
- Oracle automatically knows DST rules for Mountain Time
- **Winter (MST):** UTC-7 (November → March)
- **Summer (MDT):** UTC-6 (March → November)
- No manual intervention needed!

**Function Breakdown:**
```sql
CAST(                                    -- Convert back to DATE
    FROM_TZ(                             -- Add timezone info
        CAST(MAX(end_dt) AS TIMESTAMP),  -- Convert DATE to TIMESTAMP
        'UTC'                            -- Source timezone is UTC
    ) 
    AT TIME ZONE 'America/Denver'        -- Convert to Mountain Time (auto DST)
AS DATE)
```

---

## 📋 Files Updated

### **1. portal/services/bi_service.py**

**Function:** `get_level3_bi_feed()`
- **Updated:** All 21 UNION ALL queries (lines 296-498)
- **Changed:** From `NUMTODSINTERVAL(6/7, 'HOUR')` to `AT TIME ZONE 'America/Denver'`

**Function:** `get_capex_details()`
- **Updated:** Lines 591-594
- **Changed:** From `new_time()` MST/MDT to `AT TIME ZONE 'America/Denver'`

---

## 🎯 Benefits

1. **No More Manual Updates:** Never worry about DST changes again
2. **Accurate Timestamps:** Oracle handles DST transitions correctly
3. **Future-Proof:** Works even if DST rules change
4. **Less Error-Prone:** No risk of forgetting to update queries
5. **Consistent:** Same approach for all timezone conversions

---

## 🧪 Testing

### **Test the Conversion:**

```sql
-- Test current time conversion
SELECT 
    SYSDATE AS utc_time,
    CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'UTC') 
         AT TIME ZONE 'America/Denver' AS DATE) AS mountain_time,
    TZ_OFFSET('America/Denver') AS current_offset
FROM DUAL;
```

**Expected Results:**
- **March-November (MDT):** Offset = `-06:00`
- **November-March (MST):** Offset = `-07:00`

### **Verify BI Feed Works:**

```bash
cd monitorportal
python manage.py shell
```

```python
from portal.services.bi_service import get_level3_bi_feed, get_capex_details
from django.core.cache import cache

# Clear cache to force fresh query
cache.clear()

# Test BI Feed
bi_data = get_level3_bi_feed()
print(f"BI Feed returned {len(bi_data)} rows")
print(f"Sample: {bi_data[0] if bi_data else 'No data'}")

# Test CAPEX
capex_data = get_capex_details()
print(f"CAPEX returned {len(capex_data)} rows")
print(f"Sample: {capex_data[0] if capex_data else 'No data'}")
```

---

## 🚨 Important Notes

### **Oracle Database Requirements:**
- Oracle 9i or later (FROM_TZ introduced in 9i)
- Timezone files must be installed on database
- Verify with: `SELECT * FROM V$TIMEZONE_NAMES WHERE TZNAME = 'America/Denver';`

### **If Oracle Version Is Too Old:**

**Alternative 1: Use TZ_OFFSET function**
```sql
-- Calculate offset dynamically
MAX(end_dt) + TZ_OFFSET('America/Denver')
```

**Alternative 2: Python-based solution** (See section below)

---

## 🐍 Alternative: Python-Based DST Handling

If Oracle timezone support is not available, you can calculate the offset in Python:

### **Add to portal/services/bi_service.py:**

```python
from datetime import datetime
import pytz

def get_mountain_tz_offset():
    """
    Get current Mountain Time offset (MST or MDT)
    Returns: Number of hours to subtract (6 or 7)
    """
    mountain_tz = pytz.timezone('America/Denver')
    now_mountain = datetime.now(mountain_tz)
    offset_hours = -now_mountain.utcoffset().total_seconds() / 3600
    return int(offset_hours)

def get_level3_bi_feed():
    """Modified to use dynamic offset"""
    try:
        # Get current offset (6 during MDT, 7 during MST)
        offset = get_mountain_tz_offset()
        
        query = f"""
        SELECT /*+ PARALLEL(4) */ ...
            MAX(end_dt) - NUMTODSINTERVAL({offset}, 'HOUR') AS end_dt_in_mst
        ...
        """
        return fetch_all(query)
```

**Pros:**
- Works with any Oracle version
- Full control over logic

**Cons:**
- Query becomes dynamic (harder to cache/optimize)
- Requires `pytz` library: `pip install pytz`

---

## 📅 DST Transition Dates (2026-2030)

Oracle automatically handles these transitions with `America/Denver`:

| Year | DST Start (→ MDT)   | DST End (→ MST)     |
|------|---------------------|---------------------|
| 2026 | March 8, 2:00 AM    | November 1, 2:00 AM |
| 2027 | March 14, 2:00 AM   | November 7, 2:00 AM |
| 2028 | March 12, 2:00 AM   | November 5, 2:00 AM |
| 2029 | March 11, 2:00 AM   | November 4, 2:00 AM |
| 2030 | March 10, 2:00 AM   | November 3, 2:00 AM |

**You don't need to do anything!** Oracle handles it automatically.

---

## 🔄 Rollback Plan

If the new timezone functions cause issues, you can rollback to hardcoded offsets:

### **1. Determine Current Offset:**
```sql
SELECT TZ_OFFSET('America/Denver') FROM DUAL;
-- Returns: -06:00 (MDT) or -07:00 (MST)
```

### **2. Update Queries:**
```sql
-- If currently MDT (summer, -06:00):
MAX(end_dt) - NUMTODSINTERVAL(6, 'HOUR') AS end_dt_in_mst

-- If currently MST (winter, -07:00):
MAX(end_dt) - NUMTODSINTERVAL(7, 'HOUR') AS end_dt_in_mst
```

### **3. For CAPEX:**
```sql
-- If currently MDT:
new_time(start_dt,'GMT','MDT')

-- If currently MST:
new_time(start_dt,'GMT','MST')
```

---

## 📚 Related Oracle Functions

### **Timezone Functions You Can Use:**

```sql
-- Get list of all timezones
SELECT * FROM V$TIMEZONE_NAMES WHERE TZNAME LIKE '%Denver%';
-- Or: '%Mountain%', '%America%', etc.

-- Get current offset for a timezone
SELECT TZ_OFFSET('America/Denver') FROM DUAL;
-- Returns: -06:00 or -07:00

-- Convert timestamp to different timezone
SELECT 
    SYSTIMESTAMP AT TIME ZONE 'UTC' AS utc_time,
    SYSTIMESTAMP AT TIME ZONE 'America/Denver' AS mountain_time,
    SYSTIMESTAMP AT TIME ZONE 'America/New_York' AS eastern_time
FROM DUAL;

-- Check if DST is active
SELECT 
    CASE 
        WHEN TZ_OFFSET('America/Denver') = '-06:00' THEN 'MDT (Daylight Time)'
        WHEN TZ_OFFSET('America/Denver') = '-07:00' THEN 'MST (Standard Time)'
    END AS current_timezone
FROM DUAL;
```

---

## ✅ Checklist: After Implementing

- [x] Updated all 21 BI Feed queries to use `AT TIME ZONE 'America/Denver'`
- [x] Updated CAPEX query to use automatic timezone conversion
- [x] Tested queries in development environment
- [ ] Cleared Django cache after deployment (`cache.clear()` or restart)
- [ ] Verified timestamps in browser match expected Mountain Time
- [ ] Tested during next DST transition (November 1, 2026)
- [ ] Updated PRESENTATION_QA_GUIDE.md if needed (mention automatic DST)

---

## 🎓 Training: Explaining to DBAs

**If DBAs ask about the new timezone functions:**

1. **Purpose:** "We automated DST handling so we don't have to manually update queries twice a year"

2. **Performance:** "No performance impact - Oracle evaluates timezone at query time, same as our old NUMTODSINTERVAL approach"

3. **Compatibility:** "Works with Oracle 9i+, uses standard timezone database that Oracle maintains"

4. **Monitoring:** "Same execution plans, same query timing, just more accurate timestamps"

5. **Testing:** "Can verify with `EXPLAIN PLAN` - no difference in performance vs hardcoded offsets"

---

## 🔗 Additional Resources

- **Oracle Docs:** [Datetime Functions](https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Datetime-Functions.html)
- **Timezone Data:** [Oracle Timezone Files](https://docs.oracle.com/en/database/oracle/oracle-database/19/nlspg/datetime-data-types-and-time-zone-support.html)
- **Python pytz:** [PyTZ Documentation](https://pythonhosted.org/pytz/)

---

## 📞 Support

**If timezone conversions look wrong:**

1. **Check Oracle Timezone Version:**
   ```sql
   SELECT * FROM V$TIMEZONE_FILE;
   ```

2. **Verify America/Denver Exists:**
   ```sql
   SELECT * FROM V$TIMEZONE_NAMES WHERE TZNAME = 'America/Denver';
   ```

3. **Test Conversion Manually:**
   ```sql
   SELECT 
       SYSDATE,
       CAST(FROM_TZ(CAST(SYSDATE AS TIMESTAMP), 'UTC') 
            AT TIME ZONE 'America/Denver' AS DATE)
   FROM DUAL;
   ```

4. **Check Current Offset:**
   ```sql
   SELECT TZ_OFFSET('America/Denver') FROM DUAL;
   -- Should be -06:00 (March-Nov) or -07:00 (Nov-March)
   ```

**Contact:** [Your Name/Team]  
**Last Updated:** March 9, 2026
