# 🌐 Internal Network Sharing - READY TO USE!

## ✅ Your Portal is Now Accessible!

Django is running on your corporate network IP address.

---

## 📍 Share These URLs:

### **For Lumen Employees (On Lumen Network/VPN):**
```
http://10.161.206.34:8000
```

### **For Local Network (Office WiFi):**
```
http://192.168.0.100:8000
```

### **Test Locally (Your Computer):**
```
http://localhost:8000
```

---

## 📋 Who Can Access?

✅ **Anyone on Lumen's internal network** (VPN or office)  
✅ **Anyone on your same WiFi network**  
❌ **NOT accessible from outside internet** (secure!)

---

## 🔥 Firewall Note

**If users get connection timeout:**

Your Windows Firewall might be blocking port 8000. To fix:

```powershell
# Allow Python through firewall (Run as Administrator)
New-NetFirewallRule -DisplayName "Django Dev Server" -Direction Inbound -Program "C:\Users\ab64033\AppData\Local\Programs\Python\Python312\python.exe" -Action Allow

# OR allow port 8000 directly
New-NetFirewallRule -DisplayName "Django Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

**Simpler: When Windows prompts "Allow access?", click YES**

---

## 🚀 How to Use

1. **Share the URL:**
   - Send this URL to stakeholders: `http://10.161.206.34:8000`
   
2. **They visit the URL:**
   - Must be on Lumen VPN or office network
   - Portal will load in their browser
   
3. **Keep your computer on:**
   - Server runs on your machine
   - Don't close this terminal
   - Don't put computer to sleep

4. **To Stop Sharing:**
   - Press `Ctrl+C` in the terminal
   - Or close the terminal window

---

## 📱 Test It Now

**From your machine:**
```powershell
# Open in browser
Start-Process "http://localhost:8000"
```

**From another computer on network:**
- Visit: `http://10.161.206.34:8000`
- Should see the PASE Monitor Portal login/home page

---

## 🎯 Quick Demo Checklist

Before sharing with stakeholders:

- [ ] Server is running (check terminal)
- [ ] You tested locally: http://localhost:8000 works
- [ ] Shared URL: `http://10.161.206.34:8000`
- [ ] Told users to connect to Lumen VPN
- [ ] Your computer is plugged in (won't sleep)
- [ ] Prepared demo scenarios/data to show

---

## 🛑 To Stop the Server

In the terminal running Django:
```
Press Ctrl+C
```

Then server stops and URL becomes inaccessible.

---

## ⏰ Duration

This sharing method works as long as:
- ✅ Django server is running
- ✅ Your computer is on
- ✅ Your computer is connected to network

**No time limits!** Run demos all day if needed.

---

## 🔒 Security Notes

✅ **GOOD:**
- Only accessible on internal network
- Not exposed to public internet
- Lumen firewall protection applies

⚠️ **REMEMBER:**
- This is temporary demo setup
- For production, deploy to proper server
- Keep Django terminal visible to monitor access

---

## 📞 Support

**If URL doesn't work for others:**

1. **Check they're on VPN/Lumen network**
2. **Check Windows Firewall** (see firewall note above)
3. **Verify server is running** (check terminal)
4. **Try alternative:** Screen share via Teams/Zoom

---

**Server Started:** March 9, 2026  
**Your IP:** 10.161.206.34  
**Port:** 8000  
**Status:** ✅ RUNNING

**Keep this terminal open!** 🚀
