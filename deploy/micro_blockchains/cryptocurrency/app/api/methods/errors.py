from fastapi import HTTPException, status
from logging import Logger
from app.api.config.exceptions import bugReportsInstance
from app.api.config.env import IS_PRODUCTION, JIRA_PROJECT_ID

def handle_error(e: Exception, logger: Logger):
    """
    Centralized error handler which logs the error and, if applicable, creates a JIRA bug report.

    Args:
    - e (Exception): The exception to handle.
    - logger (Logger): Logger instance to log the error.

    Raises:
    - HTTPException: With a 500 status code.
    """
    logger.error(f"Error : {str(e)}")
    if int(IS_PRODUCTION) and (not hasattr(e, 'status_code') or (hasattr(e, 'status_code') and e.status_code == 500)): # Handling HTTP and no HTTP exceptions
        logger.info("Creating incidence on JIRA.")
        bugReportsInstance.bugReports(JIRA_PROJECT_ID, "[DEVELOPER]", str(e))
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))