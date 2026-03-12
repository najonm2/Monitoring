#!/usr/bin/env python
import urllib.request
import socket

# First check if server is running
try:
    sock = socket.create_connection(('127.0.0.1', 8000), timeout=5)
    sock.close()
    print('✅ Server is running on port 8000')
except Exception as e:
    print(f'❌ Server not responding: {e}')
    exit(1)

# Now fetch and check for JavaScript
try:
    response = urllib.request.urlopen('http://127.0.0.1:8000/dashboards/level3/lvl3-7day-insights/', timeout=10)
    content = response.read().decode('utf-8')
    
    print('')
    print('=' * 50)
    print('VERIFICATION RESULTS:')
    print('=' * 50)
    
    checks = [
        ('manualRefresh() function', 'function manualRefresh()'),
        ('startCountdownTimer() function', 'function startCountdownTimer()'),
        ('toggleAutoRefresh() function', 'function toggleAutoRefresh(enabled)'),
        ('updateLastRefreshTime() function', 'function updateLastRefreshTime()'),
        ('startAutoRefresh() function', 'function startAutoRefresh()'),
        ('manualRefreshBtn HTML element', 'id="manualRefreshBtn"'),
        ('autoRefreshToggle HTML element', 'id="autoRefreshToggle"'),
        ('REFRESH CONTROLS HTML', 'AUTO-REFRESH CONTROLS SCRIPT')
    ]
    
    for check_name, check_string in checks:
        if check_string in content:
            print(f'✅ {check_name}')
        else:
            print(f'❌ {check_name}')
    
    print('=' * 50)
    
except Exception as e:
    print(f'❌ Error fetching page: {e}')
