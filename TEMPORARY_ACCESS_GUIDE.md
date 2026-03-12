# 🌐 Temporary Public Access Guide

This guide shows multiple ways to temporarily share your PASE Monitor Portal with others for demos, testing, or stakeholder reviews.

---

## ⭐ Option 1: pyngrok (EASIEST - Recommended)

**Pros:** Pure Python, automatic setup, no manual installation  
**Cons:** Free tier has session time limits

### Quick Start:

```powershell
cd monitorportal
python run_with_ngrok.py
```

That's it! You'll get a public URL like:
```
https://abc123.ngrok-free.app
```

### Optional: Get Free Auth Token (Removes Limits)

1. Visit: https://dashboard.ngrok.com/signup
2. Copy your auth token
3. Add to `run_with_ngrok.py`:
   ```python
   ngrok.set_auth_token("YOUR_TOKEN_HERE")
   ```

---

## 🔧 Option 2: VS Code Port Forwarding (BUILT-IN)

**Pros:** No installation, secure, GitHub authentication  
**Cons:** Requires VS Code and GitHub account

### Steps:

1. **Start Django server:**
   ```powershell
   cd monitorportal
   python manage.py runserver 8000
   ```

2. **Forward Port in VS Code:**
   - Press `Ctrl+Shift+P`
   - Type: "Forward a Port"
   - Enter: `8000`
   - Visibility: Select "Public"

3. **Share URL:**
   - Right-click port 8000 in Ports panel
   - Copy "Forwarded Address"
   - Share URL (looks like: `https://abc-8000.preview.app.github.dev`)

**Security:** Requires GitHub authentication by default.

---

## 🌍 Option 3: localtunnel (Simple Alternative)

**Pros:** No account needed, simple  
**Cons:** Requires Node.js

### Installation:

```powershell
npm install -g localtunnel
```

### Usage:

```powershell
# Terminal 1: Start Django
cd monitorportal
python manage.py runserver 8000

# Terminal 2: Create tunnel
lt --port 8000
```

You'll get a URL like: `https://cool-tiger-12.loca.lt`

---

## ☁️ Option 4: Cloudflare Tunnel (Professional)

**Pros:** Free, permanent URLs, enterprise-grade  
**Cons:** More setup steps

### Installation:

```powershell
# Download cloudflared
winget install --id Cloudflare.cloudflared
```

### Usage:

```powershell
# Start Django
cd monitorportal
python manage.py runserver 8000

# Create tunnel (different terminal)
cloudflared tunnel --url http://localhost:8000
```

### Get Permanent URL:

1. Create Cloudflare account (free)
2. Run: `cloudflared tunnel login`
3. Create named tunnel: `cloudflared tunnel create pase-portal`
4. Configure permanent URL

---

## 🔐 Option 5: Tailscale (Most Secure)

**Pros:** Private network, no public internet exposure, enterprise security  
**Cons:** All users need Tailscale installed

### Setup:

1. **Install Tailscale:**
   - Visit: https://tailscale.com/download/windows
   - Install and sign in

2. **Start Django:**
   ```powershell
   cd monitorportal
   python manage.py runserver 0.0.0.0:8000
   ```

3. **Share Access:**
   - Get your Tailscale IP: `tailscale ip -4`
   - Share: `http://[YOUR_TAILSCALE_IP]:8000`
   - Users must join your Tailscale network

**Best for:** Internal Lumen team sharing with high security

---

## 📊 Comparison Table

| Solution | Pros | Cons | Best For |
|----------|------|------|----------|
| **pyngrok** | ✅ Easiest<br>✅ Pure Python<br>✅ Quick setup | ⚠️ Free tier time limits | Quick demos |
| **VS Code** | ✅ No install<br>✅ Secure by default | ⚠️ VS Code + GitHub required | Development sharing |
| **localtunnel** | ✅ No account<br>✅ Simple | ⚠️ Requires Node.js<br>⚠️ Less reliable | Quick tests |
| **Cloudflare** | ✅ Professional<br>✅ Permanent URLs | ⚠️ More setup | Long-term demos |
| **Tailscale** | ✅ Most secure<br>✅ Private network | ⚠️ All users need install | Internal team |

---

## 🚨 Security Considerations

### ⚠️ WARNING: These methods expose your portal to the internet!

**Before sharing:**

1. ✅ **Verify database credentials are not exposed**
2. ✅ **Check DEBUG mode** (should be False for sensitive data)
3. ✅ **Review ALLOWED_HOSTS** (already configured for ngrok)
4. ✅ **Test with read-only database user** if possible
5. ✅ **Monitor access logs** for suspicious activity

### Recommended Settings for Public Demos:

```python
# monitorportal/monitorportal/settings.py

# For sensitive demos, disable debug mode
DEBUG = False

# Add your ngrok/tunnel domains
ALLOWED_HOSTS = [
    "127.0.0.1", 
    "localhost",
    ".ngrok.io",
    ".ngrok-free.app",
    "your-custom-domain.com",
]

# Enable CSRF protection for external domains
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.app",
    "https://*.ngrok.io",
]
```

---

## 📝 Quick Reference

### Start with pyngrok (Recommended):

```powershell
cd monitorportal
python run_with_ngrok.py
```

### Alternative - Manual Django + ngrok:

```powershell
# Terminal 1: Django
cd monitorportal
python manage.py runserver 8000

# Terminal 2: Tunnel (if using localtunnel)
lt --port 8000

# OR with cloudflared
cloudflared tunnel --url http://localhost:8000
```

---

## 🎯 Recommended Workflow

### For Quick Demos (5-30 minutes):
→ **Use pyngrok** (Option 1)

### For Stakeholder Reviews (1-2 hours):
→ **Use VS Code Port Forwarding** (Option 2) or **pyngrok with auth token**

### For Multi-Day UAT:
→ **Use Cloudflare Tunnel** (Option 4) with permanent URL

### For Internal Team Sharing:
→ **Use Tailscale** (Option 5) for maximum security

---

## 🐛 Troubleshooting

### "Address already in use" error:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### "ALLOWED_HOSTS" error:
- Already fixed! ✅ `settings.py` includes ngrok domains

### Tunnel won't start:
```powershell
# Check if Django is running first
curl http://localhost:8000

# If not, start Django
cd monitorportal
python manage.py runserver 8000
```

### Slow performance over tunnel:
- Normal for free tiers
- Consider paid ngrok/cloudflare for better performance
- Or use Tailscale for internal team (fastest)

---

## 📞 Support

For issues or questions:
- Check Django logs: `monitorportal/logs/`
- Test local access first: http://localhost:8000
- Verify database connectivity before creating tunnel

---

## ✅ Success Checklist

Before sharing URL with others:

- [ ] Django server running without errors
- [ ] Local access works (http://localhost:8000)
- [ ] Tunnel created successfully
- [ ] Public URL loads portal correctly
- [ ] Database queries returning data
- [ ] No sensitive credentials visible in UI
- [ ] Shared URL and instructions with users
- [ ] Monitoring tunnel for access/errors

---

**Last Updated:** March 9, 2026  
**Maintained by:** Data Engineering Team
