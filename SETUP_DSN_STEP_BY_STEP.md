# Step-by-Step: Configure Databricks ODBC DSN in Windows

## What is a DSN?
A **DSN (Data Source Name)** is a saved configuration in Windows that stores database connection details. Instead of providing connection strings in your code, you just reference the DSN name.

---

## Step 1: Check if Simba Spark ODBC Driver is Installed

### Option A: Quick Check via PowerShell
```powershell
Get-OdbcDriver | Where-Object {$_.Name -like "*Spark*" -or $_.Name -like "*Databricks*"}
```

**Expected Output:**
```
Name                          Platform
----                          --------
Simba Spark ODBC Driver       64-bit
```

### Option B: Manual Check
1. Press `Windows + R`
2. Type: `odbcad32.exe`
3. Click the **"Drivers"** tab
4. Look for: **"Simba Spark ODBC Driver"**

**If you DON'T see the driver**, you need to install it first (see Step 2).

---

## Step 2: Install Simba Spark ODBC Driver (if needed)

### Check Your Organization's Software Center
1. Open **Software Center** or **Company Portal**
2. Search for: `Databricks` or `Spark ODBC`
3. Install if available

### OR Download from Databricks
1. Go to your Databricks workspace
2. Navigate to: **Settings** → **Advanced** → **JDBC/ODBC**
3. Download: **Simba Spark ODBC Driver for Windows**
4. Run the `.msi` installer
5. Follow installation wizard (keep default options)
6. Restart PowerShell/Command Prompt after installation

---

## Step 3: Get Databricks Connection Details

Before configuring the DSN, you need these details from Databricks:

### How to Find Connection Details:
1. **Log into Databricks workspace**
2. Go to: **SQL Warehouses** (or **Compute** → **SQL Warehouses**)
3. Click on your warehouse name
4. Click the **"Connection Details"** tab

### Copy These Values:
```plaintext
Server hostname:    dbc-XXXXXXXX-XXXX.cloud.databricks.com
Port:               443
HTTP Path:          /sql/1.0/warehouses/xxxxxxxxxxxxx
```

### Get Personal Access Token:
1. Click your **profile icon** (top right)
2. Select **"User Settings"**
3. Go to **"Access tokens"** tab
4. Click **"Generate new token"**
5. Give it a name: `Portal_ODBC_Access`
6. Set expiration: `90 days` (or per your policy)
7. Click **"Generate"**
8. **COPY THE TOKEN** (you can only see it once!)
   - Save it in Notepad temporarily

---

## Step 4: Open ODBC Data Source Administrator

### Method 1: Via Run Dialog (Easiest)
1. Press `Windows + R`
2. Type: **`odbcad32.exe`**
3. Press Enter

### Method 2: Via Search
1. Press `Windows` key
2. Type: **ODBC Data Sources**
3. Select: **ODBC Data Sources (64-bit)**

### Method 3: Via PowerShell Command
```powershell
Start-Process odbcad32.exe
```

---

## Step 5: Create System DSN

### Why System DSN?
- **User DSN**: Only works for your Windows user account
- **System DSN**: Works for all users + services (better for applications)

### Steps:
1. In ODBC Administrator, click the **"System DSN"** tab
2. Click **"Add..."** button
3. Scroll and select: **"Simba Spark ODBC Driver"**
   - If you don't see it, the driver isn't installed (go back to Step 2)
4. Click **"Finish"**

---

## Step 6: Configure DSN Settings

A configuration window will open. Fill in these fields:

### **Tab 1: General**
```
Data Source Name:   DataBricks_For_DBX_APP_64B_PRD
Description:        Databricks Production - ADF Monitoring
```

### **Tab 2: Connection**
**Host**
```
[Paste Server hostname from Step 3]
Example: dbc-12345678-9abc.cloud.databricks.com
```

**Port**
```
443
```

**Database**
```
default
(or leave blank)
```

**Authentication:**
- Mechanism: **User Name and Password**

**User Name:**
```
token
```
(literally type the word "token")

**Password:**
```
[Paste your Personal Access Token from Step 3]
```

**Thrift Transport:**
```
HTTP
```

**HTTP Path:**
```
[Paste HTTP Path from Step 3]
Example: /sql/1.0/warehouses/abc123def456789
```

### **Tab 3: SSL Options**
Check these boxes:
- ✅ **Enable SSL**
- ✅ **Allow Self-Signed Certificates** (if you get SSL errors)
- ✅ **Allow Host Name CN Mismatch** (if you get SSL errors)

### **Tab 4: Advanced Options**
Leave defaults, or adjust:
```
Rows Fetched Per Block:  100000
Socket Timeout:           60
```

---

## Step 7: Test the Connection

1. Click the **"Test"** button (bottom of configuration window)

### ✅ Success:
```
Connection Successful
```
Click **"OK"** to save the DSN

### ❌ Failure: Common Issues

**Error: "Network timeout"**
- Check if you're on VPN (required for most corporate Databricks)
- Verify port 443 is not blocked by firewall

**Error: "Authentication failed"**
- Verify token hasn't expired
- Ensure User Name is literally "token" (not your username)
- Generate a new token and try again

**Error: "Host name not found"**
- Double-check Server hostname (no typos)
- Ensure you copied the full hostname

**Error: "SSL certificate verification failed"**
- Enable "Allow Self-Signed Certificates" in SSL Options tab
- Enable "Allow Host Name CN Mismatch"

---

## Step 8: Verify DSN in PowerShell

After saving, verify the DSN exists:

```powershell
Get-OdbcDsn -Name "DataBricks_For_DBX_APP_64B_PRD" -DsnType "System"
```

**Expected Output:**
```
Name                                DsnType Platform
----                                ------- --------
DataBricks_For_DBX_APP_64B_PRD     System  64-bit
```

---

## Step 9: Test Connection in Python

Run this test:

```powershell
cd C:\Users\ab64033\source\repos\infa_monitor_portal
python test_databricks_connection.py
```

**Expected Output:**
```
✅ pyodbc module found
🔌 Attempting to connect to DSN: DataBricks_For_DBX_APP_64B_PRD
✅ Databricks connection SUCCESSFUL!
✅ Test query result: (1,)

📊 Connection Info:
   Database: default
   Server: dbc-xxxxx.cloud.databricks.com
   Driver: Simba Spark ODBC Driver
```

---

## Complete! 🎉

Your DSN is now configured and the portal can connect to Databricks!

---

## Quick Reference Card

| Item | Value |
|------|-------|
| **DSN Name** | `DataBricks_For_DBX_APP_64B_PRD` |
| **Type** | System DSN |
| **Driver** | Simba Spark ODBC Driver |
| **Port** | 443 |
| **Transport** | HTTP |
| **SSL** | Enabled |
| **Auth** | Token (User: "token", Pass: PAT) |

---

## Troubleshooting Commands

### List all ODBC drivers:
```powershell
Get-OdbcDriver | Format-Table Name, Platform
```

### List all System DSNs:
```powershell
Get-OdbcDsn -DsnType System | Format-Table Name, DsnType, Platform
```

### Remove DSN (if you need to start over):
```powershell
Remove-OdbcDsn -Name "DataBricks_For_DBX_APP_64B_PRD" -DsnType "System"
```

### Open ODBC Administrator directly to System DSN tab:
```powershell
Start-Process odbcad32.exe -ArgumentList "/s"
```

---

## Still Having Issues?

1. **Check VPN**: Most corporate Databricks require VPN connection
2. **Token Expiration**: Tokens expire! Generate a new one
3. **Driver Version**: Ensure you have latest Simba Spark ODBC driver
4. **Contact IT**: They may need to provide specific connection settings
5. **Use User DSN**: If System DSN doesn't work, try User DSN tab instead

---

## Security Reminder 🔒

- ⚠️ **Never share your Personal Access Token**
- ⚠️ **Tokens are like passwords** - keep them secure
- ⚠️ **Don't commit tokens to Git**
- ✅ **Rotate tokens regularly** (every 90 days recommended)
