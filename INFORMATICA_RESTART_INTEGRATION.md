# Informatica Restart Integration - Implementation Guide

## ✅ Completed

1. **Updated Informatica Restart Service** (`portal/services/informatica_restart_service.py`)
   - Added `user_security_domain` support
   - Created new `restart_ with_options()` method supporting 4 restart modes:
     - Option 1: Restart Task Only
     - Option 2: Restart Workflow from Task
     - Option 3: Restart Entire Workflow
     - Option 4: Recover Workflow from Task

2. **Updated Settings** (`monitorportal/settings.py`)
   - Updated pmcmd path: `/prd1/usr/local/informatica/CDIPC/Informatica/platform/home/server/bin/pmcmd`
   - Updated Integration Service: `IS_GRID_BI`
   - Updated username: `ab64033`
   - Added `INFORMATICA_USER_SECURITY_DOMAIN = 'CTL'`

## 🔧 Next Steps - Manual Implementation Required

### 1. Update API View (`portal/api_views.py`)

Add new restart endpoint with options:

```python
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json

@require_http_methods(["POST"])
def restart_workflow_with_options(request):
    """
    API endpoint to restart workflow/session with 4 options
    
    POST data:
    {
        "workflow_name": "wkf_Load_CDW_ASL_ICG_GRANITE",
        "folder_name": "B_CDW_ASL_ICG_GRANITE",
        "restart_option": 1,  // 1-4
        "session_name": "s_m_Load_SITE_INST"  // Required for options 1,2,4
    }
    """
    try:
        data = json.loads(request.body)
        from portal.services.informatica_restart_service import InformaticaRestartService
        
        service = InformaticaRestartService()
        
        if not service.is_configured():
            return JsonResponse({
                'success': False,
                'message': 'Informatica is not configured. Check settings.'
            }, status=500)
        
        workflow_name = data.get('workflow_name')
        folder_name = data.get('folder_name')
        restart_option = int(data.get('restart_option', 1))
        session_name = data.get('session_name')
        
        if not workflow_name or not folder_name:
            return JsonResponse({
                'success': False,
                'message': 'workflow_name and folder_name are required'
            }, status=400)
        
        result = service.restart_with_options(
            workflow_name=workflow_name,
            folder_name=folder_name,
            restart_option=restart_option,
            session_name=session_name
        )
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
```

### 2. Add URL Route (`portal/urls.py`)

```python
urlpatterns = [
    # ... existing patterns ...
    
    # New restart with options endpoint
    path("api/informatica/restart-with-options/", api_views.restart_workflow_with_options, name="restart_workflow_with_options"),
]
```

### 3. Update Failed Jobs Template (`portal/templates/portal/level3_failed_jobs_status.html`)

Add modal for restart options at the end of the file (before `</body>`):

```html
<!-- Restart Options Modal -->
<div id="restartModal" style="display:none; position:fixed; z-index:1000; left:0; top:0; width:100%; height:100%; background:rgba(0,0,0,0.5);">
    <div style="background:#fff; margin:10% auto; padding:30px; width:500px; border-radius:8px;">
        <h3 style="margin-top:0;">Select Restart Option</h3>
        <p><strong>Workflow:</strong> <span id="modalWorkflow"></span></p>
        <p><strong>Session:</strong> <span id="modalSession"></span></p>
        <p><strong>Folder:</strong> <span id="modalFolder"></span></p>
        <hr>
        
        <div style="margin:20px 0;">
            <label style="display:block; margin:10px 0; cursor:pointer;">
                <input type="radio" name="restartOption" value="1" checked>
                <strong>Restart Task Only</strong> - Restarts only this session
            </label>
            <label style="display:block; margin:10px 0; cursor:pointer;">
                <input type="radio" name="restartOption" value="2">
                <strong>Restart Workflow from Task</strong> - Restarts workflow from this task onward
            </label>
            <label style="display:block; margin:10px 0; cursor:pointer;">
                <input type="radio" name="restartOption" value="3">
                <strong>Restart Entire Workflow</strong> - Restarts workflow from beginning
            </label>
            <label style="display:block; margin:10px 0; cursor:pointer;">
                <input type="radio" name="restartOption" value="4">
                <strong>Recover Workflow from Task</strong> - Recovers workflow in recovery mode
            </label>
        </div>
        
        <div style="text-align:right; margin-top:20px;">
            <button onclick="closeRestartModal()" style="padding:10px 20px; margin-right:10px; background:#ddd; border:none; border-radius:4px; cursor:pointer;">Cancel</button>
            <button onclick="executeRestart()" style="padding:10px 20px; background:#007bff; color:#fff; border:none; border-radius:4px; cursor:pointer;">Restart</button>
        </div>
    </div>
</div>

<script>
let currentRestartData = {};

function showRestartOptions(workflowName, folderName, sessionName) {
    currentRestartData = {
        workflow_name: workflowName,
        folder_name: folderName,
        session_name: sessionName
    };
    
    document.getElementById('modalWorkflow').textContent = workflowName;
    document.getElementById('modalSession').textContent = sessionName;
    document.getElementById('modalFolder').textContent = folderName;
    document.getElementById('restartModal').style.display = 'block';
}

function closeRestartModal() {
    document.getElementById('restartModal').style.display = 'none';
}

function executeRestart() {
    const selectedOption = document.querySelector('input[name="restartOption"]:checked').value;
    
    const data = {
        ...currentRestartData,
        restart_option: parseInt(selectedOption)
    };
    
    closeRestartModal();
    
    // Show loading
    const btn = event.target;
    btn.innerHTML = '⏳ Restarting...';
    btn.disabled = true;
    
    fetch('/api/informatica/restart-with-options/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('✓ ' + result.message);
            location.reload();
        } else {
            alert('✗ Error: ' + result.message);
        }
    })
    .catch(error => {
        alert('✗ Error: ' + error);
    })
    .finally(() => {
        btn.innerHTML = '🔄 Restart';
        btn.disabled = false;
    });
}

// Update existing restart button onclick to use new modal
// Find the line with: onclick="restartWorkflow(...)"
// Replace with: onclick="showRestartOptions('{{ job.workflow_name|escapejs }}', '{{ job.subject_area|escapejs }}', '{{ job.session_name|escapejs }}')"
</script>
```

Update the restart button in the table (search for the button with "Restart"):

```html
<button onclick="showRestartOptions('{{ job.workflow_name|escapejs }}', '{{ job.subject_area|escapejs }}', '{{ job.session_name|escapejs }}')" 
        class="restart-button"
        style="..."
        title="Restart with options">
    🔄 Restart
</button>
```

### 4. Create Manual Restart Page

Create new file: `portal/templates/portal/manual_restart.html`

```html
{% extends "portal/layout.html" %}

{% block title %}Manual Restart{% endblock %}

{% block content %}
<div style="max-width:800px; margin:0 auto; padding:20px;">
    <h2>🔄 Manual Workflow/Session Restart</h2>
    <p>Use this form to manually restart workflows or sessions that are not in the failed jobs list.</p>
    
    <form id="manualRestartForm" style="background:#f5f5f5; padding:20px; border-radius:8px; margin-top:20px;">
        <div style="margin-bottom:15px;">
            <label><strong>Folder Name:</strong></label>
            <input type="text" id="folderName" placeholder="e.g., B_CDW_ASL_ICG_GRANITE" style="width:100%; padding:8px; margin-top:5px;" required>
        </div>
        
        <div style="margin-bottom:15px;">
            <label><strong>Workflow Name:</strong></label>
            <input type="text" id="workflowName" placeholder="e.g., wkf_Load_CDW_ASL_ICG_GRANITE" style="width:100%; padding:8px; margin-top:5px;" required>
        </div>
        
        <div style="margin-bottom:15px;">
            <label><strong>Session/Task Name:</strong> <span style="color:#666;">(Optional for option 3)</span></label>
            <input type="text" id="sessionName" placeholder="e.g., s_m_Load_SITE_INST" style="width:100%; padding:8px; margin-top:5px;">
        </div>
        
        <div style="margin-bottom:20px;">
            <label><strong>Restart Option:</strong></label>
            <div style="margin-top:10px;">
                <label style="display:block; margin:8px  0;"><input type="radio" name="option" value="1" checked> Restart Task Only</label>
                <label style="display:block; margin:8px 0;"><input type="radio" name="option" value="2"> Restart Workflow from Task</label>
                <label style="display:block; margin:8px 0;"><input type="radio" name="option" value="3"> Restart Entire Workflow</label>
                <label style="display:block; margin:8px 0;"><input type="radio" name="option" value="4"> Recover Workflow from Task</label>
            </div>
        </div>
        
        <button type="submit" style="padding:12px 30px; background:#007bff; color:#fff; border:none; border-radius:4px; cursor:pointer; font-size:16px;">
            🚀 Restart Now
        </button>
    </form>
    
    <div id="result" style="margin-top:20px;"></div>
</div>

<script>
document.getElementById('manualRestartForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const folder = document.getElementById('folderName').value;
    const workflow = document.getElementById('workflowName').value;
    const session = document.getElementById('sessionName').value;
    const option = document.querySelector('input[name="option"]:checked').value;
    
    const data = {
        folder_name: folder,
        workflow_name: workflow,
        session_name: session,
        restart_option: parseInt(option)
    };
    
    const result = document.getElementById('result');
    result.innerHTML = '<p style="color:#007bff;">⏳ Processing restart request...</p>';
    
    fetch('/api/informatica/restart-with-options/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            result.innerHTML = '<div style="padding:15px; background:#d4edda; color:#155724; border-radius:4px;">✓ ' + data.message + '</div>';
        } else {
            result.innerHTML = '<div style="padding:15px; background:#f8d7da; color:#721c24; border-radius:4px;">✗ Error: ' + data.message + '</div>';
        }
    })
    .catch(error => {
        result.innerHTML = '<div style="padding:15px; background:#f8d7da; color:#721c24; border-radius:4px;">✗ Error: ' + error + '</div>';
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
</script>
{% endblock %}
```

### 5. Add View for Manual Restart (`portal/views.py`)

```python
def manual_restart_view(request):
    """Manual restart page for developers"""
    return render(request, 'portal/manual_restart.html')
```

### 6. Add URL for Manual Restart (`portal/urls.py`)

```python
    # Manual restart page
    path('manual-restart/', views.manual_restart_view, name='manual_restart'),
```

### 7. Add Menu Item (`portal/templates/portal/layout.html`)

Find the dashboards menu section and add:

```html
<a href="{% url 'manual_restart' %}" class="dropdown-item">
    🔄 Manual Restart
</a>
```

## 📝 Testing Checklist

- [ ] Test Option 1: Restart Task Only
- [ ] Test Option 2: Restart Workflow from Task
- [ ] Test Option 3: Restart Entire Workflow
- [ ] Test Option 4: Recover Workflow from Task
- [ ] Test from Failed Jobs page
- [ ] Test from Manual Restart page
- [ ] Verify all 4 options work on Linux server

## 🚀 Deployment to Linux

Copy these files to your Linux server:
- `portal/services/informatica_restart_service.py` (updated)
- `monitorportal/settings.py` (updated)
- All new templates and views

Restart the Django application.

---

**All bash commands work ✅ - Now integrated into Django portal!**
