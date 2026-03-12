# Performance Testing Checklist ✅

## Quick Performance Test (5 minutes)

### 1. **Restart Django Server**
```powershell
# Stop current server (Ctrl+C in terminal)
# Start fresh server
python manage.py runserver
```

---

### 2. **Test BEFORE Cache (First Load)**
1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Clear cache: Right-click → Clear browser cache
4. Navigate to: `http://localhost:8000/portal/level3/bi-report`
5. **Record time:** Look for total load time in Network tab (bottom right)
   - Expected: 4-8 seconds (first load with parallel queries)
   - Previous: 8-12 seconds

---

### 3. **Test AFTER Cache (Subsequent Loads)**
1. **Important:** Do NOT clear cache this time
2. Keep Network tab open
3. Refresh page (F5) immediately
4. **Record time:** Should be MUCH faster
   - Expected: <100ms (cached response!)
   - Previous: 8-12 seconds (no cache)

---

### 4. **Test Cache Expiration**
1. Wait 3+ minutes (cache expires)
2. Refresh page again
3. **Should be slow again** (rebuilding cache)
4. Refresh immediately → Fast again (cache hit)

---

## Expected Results 📊

### Scenario 1: First Load (Cache MISS)
- **Before optimization:** 8-12 seconds
- **After optimization:** 4-8 seconds
- **Improvement:** 40-50% faster

### Scenario 2: Subsequent Loads (Cache HIT within 3 min)
- **Before optimization:** 8-12 seconds (no cache!)
- **After optimization:** <100ms
- **Improvement:** 95% faster! 🚀

---

## What to Check

### ✅ Success Indicators:
- [ ] First page load: 4-8 seconds
- [ ] Second page load (within 3 min): <100ms
- [ ] Page displays all data correctly
- [ ] No errors in browser console
- [ ] No errors in Django terminal

### ❌ Problem Indicators:
- [ ] Page takes >15 seconds to load
- [ ] Django shows Oracle connection errors
- [ ] Missing data in BI Feed or CAPEX sections
- [ ] Cache not working (every load is slow)

---

## Browser DevTools - Network Tab Guide

### How to Read Network Tab:
1. **DOMContentLoaded** (blue line): HTML parsed
2. **Load** (red line): All resources loaded
3. **Finish** (bottom right): Total time

### Look for:
- **portal/level3/bi-report** request
- **Time column:** Response time for main request
- **Waterfall:** Visual timeline

### Example Output:
```
Name                          Status  Type      Size      Time
─────────────────────────────────────────────────────────────
level3/bi-report              200     document  45.2 KB   456ms  ← Cache HIT!
level3_bi_report.css          200     css       3.1 KB    12ms
level3_bi_report.js           200     js        8.5 KB    15ms
─────────────────────────────────────────────────────────────
Finish: 483ms  |  DOMContentLoaded: 458ms  |  Load: 483ms
```

---

## Test All Level3 Pages

Apply same test to ALL Level3 reports:

### 1. **BI Report** (just optimized!)
   - URL: `/portal/level3/bi-report`
   - Cache: 3 minutes
   - Expected: Fast!

### 2. **Failed Job Status**
   - URL: `/portal/level3/failed-job-status`
   - Cache: 2 minutes (already had caching)
   - Expected: Already fast

### 3. **7-Day Insights**
   - URL: `/portal/level3/7day-insights`
   - Cache: 3 minutes (already had caching)
   - Expected: Already fast

---

## PowerShell Performance Test Script

```powershell
# Save as test_performance.ps1
# Measures page load time

Write-Host "Testing Level3 BI Report Performance..." -ForegroundColor Cyan

# Test 1: First load (cache miss)
Write-Host "`nTest 1: First Load (Cache MISS)" -ForegroundColor Yellow
$time1 = Measure-Command {
    $response1 = Invoke-WebRequest -Uri "http://localhost:8000/portal/level3/bi-report" -UseBasicParsing
}
Write-Host "Time: $($time1.TotalSeconds) seconds" -ForegroundColor Green

# Wait 1 second
Start-Sleep -Seconds 1

# Test 2: Second load (cache hit)
Write-Host "`nTest 2: Second Load (Cache HIT)" -ForegroundColor Yellow
$time2 = Measure-Command {
    $response2 = Invoke-WebRequest -Uri "http://localhost:8000/portal/level3/bi-report" -UseBasicParsing
}
Write-Host "Time: $($time2.TotalSeconds) seconds" -ForegroundColor Green

# Calculate improvement
$improvement = [math]::Round((1 - ($time2.TotalSeconds / $time1.TotalSeconds)) * 100, 1)
Write-Host "`n==== RESULTS ====" -ForegroundColor Magenta
Write-Host "First Load:  $($time1.TotalSeconds) seconds" -ForegroundColor White
Write-Host "Second Load: $($time2.TotalSeconds) seconds" -ForegroundColor White
Write-Host "Improvement: $improvement% faster!" -ForegroundColor Green

# Validate
if ($time2.TotalSeconds -lt 1.0) {
    Write-Host "`n✅ SUCCESS: Cache is working! Second load < 1 second" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  WARNING: Second load still slow. Cache may not be working." -ForegroundColor Yellow
}
```

### Run test:
```powershell
cd c:\Users\ab64033\source\repos\infa_monitor_portal
.\test_performance.ps1
```

---

## Django Server Logs

### Watch for these messages:
```
# Cache MISS (first load)
[INFO] Fetching fresh data for level3_bi_report

# Cache HIT (subsequent load)
[INFO] Using cached data for level3_bi_report
```

### Check for errors:
```
# Oracle connection error
DatabaseError: ORA-xxxxx

# Cache error
CacheKeyWarning: Cache key contains invalid characters
```

---

## Quick Validation Checklist

After testing, verify:

- [ ] **BI Report loads fast** (<1 sec after first load)
- [ ] **All data displays correctly**
  - [ ] BI Feed table populated
  - [ ] CAPEX details showing
  - [ ] ERP status showing
- [ ] **No console errors** (F12 → Console tab)
- [ ] **No Django errors** (check terminal)
- [ ] **Cache expires** (after 3+ min, data refreshes)

---

## Rollback if Needed

If anything breaks:

```bash
# 1. Stop server (Ctrl+C)

# 2. Revert changes
git diff views.py
git diff services/bi_service.py

# 3. Manual revert: Remove cache logic from views.py
# 4. Manual revert: Remove query hints from bi_service.py

# 5. Restart server
python manage.py runserver
```

---

## Next Steps if Still Slow

If performance is still not acceptable:

1. **Check database server load**
   - Oracle might be slow/busy
   - Network latency to database

2. **Increase cache timeout**
   - Change from 180s to 300s (5 min)
   - Change from 180s to 600s (10 min) if data is static

3. **Add Redis caching**
   - Install django-redis
   - Configure Redis backend
   - Much faster than LocMemCache

4. **Database tuning** (DBA required)
   - Add indexes on ICSM.app_control_status
   - Optimize query plans
   - Check table statistics

---

## Support

If issues occur:
1. Check Django terminal for errors
2. Check browser console (F12) for JavaScript errors
3. Test with PowerShell script for timing data
4. Share timings and error messages for debugging

**Expected outcome:** Page should load in <1 second for cached requests! 🚀
