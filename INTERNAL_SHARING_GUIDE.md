# Internal Network Sharing Guide

## Option A: Share via Your Computer's IP

### Step 1: Find Your IP Address
```powershell
# Get your IP address
ipconfig | Select-String "IPv4"
```

You'll see something like: `192.168.1.100`

### Step 2: Allow External Connections
Edit `monitorportal/monitorportal/settings.py`:
```python
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost", 
    "192.168.1.100",  # Your actual IP
    "*",  # Allow all (temporary - for testing only)
]
```

### Step 3: Start Django on All Interfaces
```powershell
cd monitorportal
python manage.py runserver 0.0.0.0:8000
```

### Step 4: Share URL with Team
```
http://192.168.1.100:8000
```

**Requirements:**
- Users must be on same network (VPN or office network)
- Firewall must allow port 8000
- Your computer must stay on during demo

---

## Option B: Deploy to Internal Dev Server

### Best for: Multi-day demos, UAT testing

If Lumen has internal dev servers, deploy there:

1. **Windows Server with IIS:**
   - Use `web.config` (already configured)
   - Deploy via network share or Git
   - URL: `http://dev-server.lumen.com/pase-monitor`

2. **Azure App Service (Internal):**
   - Deploy to Lumen's Azure subscription
   - Private endpoint for internal access
   - Professional URL with SSL

3. **VM on corporate network:**
   - Provision Windows VM
   - Install Python + dependencies
   - Run Django as Windows service
   - Access via internal DNS

---

## Option C: Scheduled Demo Sessions

### For: Live presentations only

1. **Screen Sharing:**
   - Teams/Zoom screen share
   - Run on localhost
   - Walk through features live

2. **Recording:**
   - Record demo video
   - Loom/Teams recording
   - Share recording link

---

## Comparison

| Method | Setup Time | Duration | Security | Best For |
|--------|-----------|----------|----------|----------|
| **VS Code Port Forward** | 2 min | Session | High | Quick demos |
| **Azure Dev Tunnels** | 10 min | Persistent | High | Multi-day |
| **Network IP Sharing** | 5 min | While PC on | Medium | Same network |
| **Internal Server** | 2-4 hours | Permanent | Highest | Production-like |
| **Screen Share** | 1 min | Meeting only | Highest | Live demos |

---

## Recommended Approach

### For Quick Demo (Today):
→ **VS Code Port Forwarding** (2 minutes, works now)

### For This Week:
→ **Azure Dev Tunnels** (10 minutes, Microsoft-owned)

### For Production Readiness:
→ **Internal IIS Server** (talk to Lumen IT/DevOps)
