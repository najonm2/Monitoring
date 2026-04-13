"""
Informatica PowerCenter Workflow Restart Service

This service provides functionality to restart Informatica PowerCenter workflows
directly from the portal using pmcmd (PowerCenter Command Line Program).

Features:
- Restart workflows from task level
- Restart from beginning
- Check workflow run status
- Support for different repositories and folders
"""

import subprocess
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class InformaticaRestartService:
    """
    Service to restart Informatica PowerCenter workflows using pmcmd
    """
    
    def __init__(self):
        """Initialize with credentials from settings"""
        self.pmcmd_path = getattr(settings, 'INFORMATICA_PMCMD_PATH', 'pmcmd')
        self.repository =getattr(settings, 'INFORMATICA_REPOSITORY', '')
        self.domain = getattr(settings, 'INFORMATICA_DOMAIN', '')
        self.integration_service = getattr(settings, 'INFORMATICA_INTEGRATION_SERVICE', '')
        self.username = getattr(settings, 'INFORMATICA_USERNAME', '')
        self.password = getattr(settings, 'INFORMATICA_PASSWORD', '')
        self.user_security_domain = getattr(settings, 'INFORMATICA_USER_SECURITY_DOMAIN', '')
    
    def is_configured(self) -> bool:
        """Check if all required configuration is present"""
        required_fields = [
            self.repository,
            self.domain,
            self.integration_service,
            self.username,
            self.password
        ]
        return all(required_fields)
    
    def restart_workflow(
        self,
        workflow_name: str,
        folder_name: str,
        restart_from_task: Optional[str] = None,
        wait: bool = False
    ) -> Dict[str, Any]:
        """
        Restart an Informatica workflow
        
        Args:
            workflow_name: Name of the workflow to restart
            folder_name: Folder containing the workflow
            restart_from_task: Optional task name to restart from (otherwise restarts from beginning)
            wait: Whether to wait for workflow to complete
            
        Returns:
            dict: Status and message of the operation
        """
        if not self.is_configured():
            return {
                'success': False,
                'message': 'Informatica connection not configured. Check settings.',
                'error': 'Missing configuration'
            }
        
        try:
            # Build pmcmd command
            cmd = [
                self.pmcmd_path,
                'startworkflow',
                '-sv', self.integration_service,
                '-d', self.domain,
                '-u', self.username,
                '-p', self.password,
                '-f', folder_name,
                workflow_name
            ]
            
            # Add restart from task if specified
            if restart_from_task:
                cmd.extend(['-from_task', restart_from_task])
            
            # Add wait flag if specified
            if wait:
                cmd.append('-wait')
            
            logger.info(f"Restarting workflow: {workflow_name} in folder: {folder_name}")
            
            # Execute command (hide password in logs)
            cmd_display = cmd.copy()
            pwd_index = cmd_display.index('-p') + 1
            cmd_display[pwd_index] = '****'
            logger.debug(f"Command: {' '.join(cmd_display)}")
            
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'Workflow "{workflow_name}" restarted successfully',
                    'output': result.stdout,
                    'workflow': workflow_name,
                    'folder': folder_name
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to restart workflow "{workflow_name}"',
                    'error': result.stderr or result.stdout,
                    'workflow': workflow_name,
                    'folder': folder_name
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': f'Workflow restart timed out after 5 minutes',
                'error': 'Timeout',
                'workflow': workflow_name
            }
        except FileNotFoundError:
            return {
                'success': False,
                'message': f'pmcmd not found. Check INFORMATICA_PMCMD_PATH in settings.',
                'error': 'pmcmd not found',
                'workflow': workflow_name
            }
        except Exception as e:
            logger.error(f"Error restarting workflow {workflow_name}: {str(e)}")
            return {
                'success': False,
                'message': f'Error restarting workflow: {str(e)}',
                'error': str(e),
                'workflow': workflow_name
            }
    
    def restart_session(
        self,
        workflow_name: str,
        session_name: str,
        folder_name: str,
        wait: bool = False
    ) -> Dict[str, Any]:
        """
        Restart a specific session (task) within a workflow
        
        Args:
            workflow_name: Name of the workflow containing the session
            session_name: Name of the session/task to restart
            folder_name: Folder containing the workflow
            wait: Whether to wait for task to complete
            
        Returns:
            dict: Status and message of the operation
        """
        if not self.is_configured():
            return {
                'success': False,
                'message': 'Informatica connection not configured. Check settings.',
                'error': 'Missing configuration'
            }
        
        try:
            # Build pmcmd starttask command
            cmd = [
                self.pmcmd_path,
                'starttask',
                '-sv', self.integration_service,
                '-d', self.domain,
                '-u', self.username,
                '-p', self.password,
                '-f', folder_name,
                '-w', workflow_name,
                session_name  # taskInstancePath
            ]
            
            # Add wait flag if specified
            if wait:
                cmd.insert(-1, '-wait')  # Insert before taskInstancePath
            
            logger.info(f"Restarting session: {session_name} in workflow: {workflow_name}, folder: {folder_name}")
            
            # Execute command (hide password in logs)
            cmd_display = cmd.copy()
            pwd_index = cmd_display.index('-p') + 1
            cmd_display[pwd_index] = '****'
            logger.debug(f"Command: {' '.join(cmd_display)}")
            
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'Session "{session_name}" restarted successfully in workflow "{workflow_name}"',
                    'output': result.stdout,
                    'workflow': workflow_name,
                    'session': session_name,
                    'folder': folder_name
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to restart session "{session_name}"',
                    'error': result.stderr or result.stdout,
                    'workflow': workflow_name,
                    'session': session_name,
                    'folder': folder_name
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': f'Session restart timed out after 5 minutes',
                'error': 'Timeout',
                'session': session_name
            }
        except FileNotFoundError:
            return {
                'success': False,
                'message': f'pmcmd not found. Check INFORMATICA_PMCMD_PATH in settings.',
                'error': 'pmcmd not found',
                'session': session_name
            }
        except Exception as e:
            logger.error(f"Error restarting session {session_name}: {str(e)}")
            return {
                'success': False,
                'message': f'Error restarting session: {str(e)}',
                'error': str(e),
                'session': session_name
            }
    
    def restart_with_options(
        self,
        workflow_name: str,
        folder_name: str,
        restart_option: int,
        session_name: Optional[str] = None,
        integration_service: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Restart workflow/session with 4 different options
        
        Args:
            workflow_name: Name of the workflow
            folder_name: Folder containing the workflow
            restart_option: 1=Restart Task, 2=Restart from Task, 3=Restart Workflow, 4=Recover Workflow
            session_name: Session/task name (required for options 1, 2, 4)
            integration_service: Integration Service name (defaults to settings if not provided)
            
        Returns:
            dict: Status and message of the operation
        """
        if not self.is_configured():
            return {
                'success': False,
                'message': 'Informatica connection not configured. Check settings.',
                'error': 'Missing configuration'
            }
        
        try:
            # Use provided integration_service or fall back to self.integration_service
            is_service = integration_service if integration_service else self.integration_service
            
            # Build base command args
            base_args = [
                '-sv', is_service,
                '-d', self.domain,
                '-u', self.username
            ]
            
            # Add user security domain if configured
            if self.user_security_domain:
                base_args.extend(['-usd', self.user_security_domain])
            
            base_args.extend(['-p', self.password, '-f', folder_name])
            
            # Option 1: Restart Task Only
            if restart_option == 1:
                if not session_name:
                    return {'success': False, 'message': 'Session name required for option 1'}
                    
                cmd = [self.pmcmd_path, 'starttask'] + base_args + [
                    '-w', workflow_name,
                    session_name
                ]
                action = f'Restarting task: {session_name}'
                
            # Option 2: Restart Workflow from Task
            elif restart_option == 2:
                if not session_name:
                    return {'success': False, 'message': 'Session name required for option 2'}
                    
                cmd = [self.pmcmd_path, 'startworkflow'] + base_args + [
                    '-startfrom', session_name,
                    workflow_name
                ]
                action = f'Restarting workflow from task: {session_name}'
                
            # Option 3: Restart Entire Workflow
            elif restart_option == 3:
                cmd = [self.pmcmd_path, 'startworkflow'] + base_args + [workflow_name]
                action = f'Restarting entire workflow: {workflow_name}'
                
            # Option 4: Recover Workflow from Task
            elif restart_option == 4:
                if not session_name:
                    return {'success': False, 'message': 'Session name required for option 4'}
                    
                cmd = [self.pmcmd_path, 'startworkflow'] + base_args + [
                    '-startfrom', session_name,
                    '-recovery',
                    workflow_name
                ]
                action = f'Recovering workflow from task: {session_name}'
                
            else:
                return {
                    'success': False,
                    'message': f'Invalid restart option: {restart_option}. Must be 1-4.'
                }
            
            logger.info(f"{action} in folder: {folder_name}")
            
            # Execute command (hide password in logs)
            cmd_display = cmd.copy()
            pwd_index = cmd_display.index('-p') + 1
            cmd_display[pwd_index] = '****'
            logger.debug(f"Command: {' '.join(cmd_display)}")
            
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'{action} completed successfully',
                    'output': result.stdout,
                    'workflow': workflow_name,
                    'session': session_name,
                    'folder': folder_name,
                    'option': restart_option
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed: {action}',
                    'error': result.stderr or result.stdout,
                    'workflow': workflow_name,
                    'session': session_name,
                    'folder': folder_name
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'message': f'Restart timed out after 5 minutes',
                'error': 'Timeout'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'message': f'pmcmd not found. Check INFORMATICA_PMCMD_PATH in settings.',
                'error': 'pmcmd not found'
            }
        except Exception as e:
            logger.error(f"Error during restart: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'error': str(e)
            }
    
    def get_workflow_status(
        self,
        workflow_name: str,
        folder_name: str
    ) -> Dict[str, Any]:
        """
        Get the current status of a workflow
        
        Args:
            workflow_name: Name of the workflow
            folder_name: Folder containing the workflow
            
        Returns:
            dict: Current status information
        """
        if not self.is_configured():
            return {
                'success': False,
                'message': 'Informatica connection not configured'
            }
        
        try:
            cmd = [
                self.pmcmd_path,
                'getworkflowdetails',
                '-sv', self.integration_service,
                '-d', self.domain,
                '-u', self.username,
                '-p', self.password,
                '-f', folder_name,
                workflow_name
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'status': result.stdout,
                    'workflow': workflow_name
                }
            else:
                return {
                    'success': False,
                    'message': 'Could not retrieve workflow status',
                    'error': result.stderr or result.stdout
                }
                
        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'error': str(e)
            }
    
    def stop_workflow(
        self,
        workflow_name: str,
        folder_name: str
    ) -> Dict[str, Any]:
        """
        Stop a running workflow
        
        Args:
            workflow_name: Name of the workflow to stop
            folder_name: Folder containing the workflow
            
        Returns:
            dict: Status of the operation
        """
        if not self.is_configured():
            return {
                'success': False,
                'message': 'Informatica connection not configured'
            }
        
        try:
            cmd = [
                self.pmcmd_path,
                'stopworkflow',
                '-sv', self.integration_service,
                '-d', self.domain,
                '-u', self.username,
                '-p', self.password,
                '-f', folder_name,
                workflow_name
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'Workflow "{workflow_name}" stopped successfully',
                    'workflow': workflow_name
                }
            else:
                return {
                    'success': False,
                    'message': f'Failed to stop workflow "{workflow_name}"',
                    'error': result.stderr or result.stdout
                }
                
        except Exception as e:
            logger.error(f"Error stopping workflow: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'error': str(e)
            }


# Helper function for easy access
def restart_workflow(workflow_name: str, folder_name: str, restart_from_task: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to restart a workflow
    
    Args:
        workflow_name: Name of the workflow
        folder_name: Folder name
        restart_from_task: Optional task to restart from
        
    Returns:
        dict: Operation result
    """
    service = InformaticaRestartService()
    return service.restart_workflow(workflow_name, folder_name, restart_from_task)


def restart_session(workflow_name: str, session_name: str, folder_name: str) -> Dict[str, Any]:
    """
    Convenience function to restart a session within a workflow
    
    Args:
        workflow_name: Name of the workflow
        session_name: Name of the session/task
        folder_name: Folder name
        
    Returns:
        dict: Operation result
    """
    service = InformaticaRestartService()
    return service.restart_session(workflow_name, session_name, folder_name)
