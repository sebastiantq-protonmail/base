""" 
Developed by Sebastian T. Quintero.
Date: 4th of Jan, 2024.

This script acts as a watchdog for a web service, checking for updates on an Apache server,
handling the update process, and restarting the service by calling the main function from main.py.
"""

import os
import sys
import time
import logging

from main import main as start_services
from self_management.update_handler import check_for_updates, download_and_apply_update

# Configure logging to file and stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("watchdog.log"),
                              logging.StreamHandler()])

def restart_script():
    """Restart the current script using python."""
    os.execv(sys.executable, [sys.executable] + sys.argv)

    # ChatGTP Recommendation: 
    # TODO: Improve the update and deployment process for production environments.
    # Consider implementing a Continuous Integration and Continuous Deployment (CI/CD) pipeline
    # that can handle updates more robustly. This would involve automated testing, validation,
    # and the ability to roll back to previous versions if an update fails. The benefits include
    # minimizing downtime and ensuring that updates do not introduce regressions or new issues.
    # Tools like Jenkins, GitLab CI, GitHub Actions, or CircleCI can be utilized to set up these
    # workflows. Additionally, containerization with Docker and orchestration with Kubernetes
    # can provide an isolated and consistent environment for deployment, scaling, and management
    # of application instances.

def main():
    """
    Main execution function: starts the services, checks for updates periodically,
    and if an update is found, applies the update and restarts the services.
    """
    try:
        # Start the services initially
        logging.info("Starting services...")
        start_services()
        logging.info("Services started.")
        logging.info("The services will be checked for updates every minute.")

        # Main loop to check for updates periodically
        while True:
            if check_for_updates():
                logging.info("Update found! Applying update...")
                download_and_apply_update()
                logging.info("Update applied. Restarting services...")
                restart_script()
            
            # Wait some time before checking for updates again
            time.sleep(60) # Check for updates every minute
    except Exception as e:
        logging.exception("An unexpected error occurred: %s", e)

if __name__ == "__main__":
    main()
