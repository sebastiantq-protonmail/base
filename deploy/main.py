""" 
Developed by Sebastian T. Quintero.
Date: 4th of Jan, 2024.

This script compiles the APIs within the self-management directory 
and starts the services using Docker Compose.

Example of how to use the functions defined above:

```python
...
# Obtaining absolute paths to the API directories
api_updates_directory = get_absolute_path('self-management/api_updates')

# Stop and clean up any previous services
docker_compose_file = get_absolute_path('docker-compose.yml')
docker_compose_down(docker_compose_file)

# Build the Docker images for APIs
build_docker_image(api_updates_directory)

# Start the services with Docker Compose
docker_compose_up(docker_compose_file)
...
```
"""

import subprocess
import os
import logging

# Configure logging to file and stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("main.log"),
                              logging.StreamHandler()])

def get_absolute_path(relative_path):
    """
    Constructs an absolute path by joining the base path of the script with a relative path.
    
    Parameters:
    relative_path (str): The relative path to be joined with the base script path.
    
    Returns:
    str: The absolute path created from the base path and the relative path.
    """
    base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def build_docker_image(api_directory):
    """
    Builds a Docker image for the given API directory if a Dockerfile is found.
    
    Parameters:
    api_directory (str): The absolute path to the API directory where the Dockerfile is located.
    
    Raises:
    FileNotFoundError: If no Dockerfile is found in the API directory.
    subprocess.CalledProcessError: If the docker build command fails.
    """
    logging.info(f"Attempting to build Docker image for API located at {api_directory}...")
    try:
        process = subprocess.Popen(['docker', 'build', '-t', f"{os.path.basename(api_directory)}", '.'], 
                                    cwd=api_directory, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT, 
                                    text=True)
        
        # Show the output of the subprocess in real time
        for line in process.stdout:
            print(line, end='')
        
        # Wait for the process to finish and check the return code
        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, process.args)
        logging.info(f"Successfully built Docker image for {api_directory}")
    except FileNotFoundError:
        logging.error(f"No Dockerfile found for API in {api_directory}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to build Docker image for API in {api_directory}: {e}")

def docker_compose_down(compose_file):
    """
    Stops and removes the containers, networks, volumes, and images defined by the docker-compose.yml file.
    
    Parameters:
    compose_file (str): The absolute path to the docker-compose.yml file.
    
    Raises:
    subprocess.CalledProcessError: If the docker-compose down command fails.
    """
    logging.info(f"Stopping services and cleaning up with Docker Compose file located at {compose_file}...")
    try:
        process = subprocess.Popen(['docker-compose', '-f', compose_file, 'down'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True)

        # Show the output of the subprocess in real time
        for line in process.stdout:
            print(line, end='')

        # Wait for the process to finish and check the return code
        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, process.args)
        logging.info("Services stopped and cleaned up successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to stop services and clean up with Docker Compose: {e}")

def docker_compose_up(compose_file):
    """
    Starts the services defined in the docker-compose.yml file.
    
    Parameters:
    compose_file (str): The absolute path to the docker-compose.yml file.
    
    Raises:
    subprocess.CalledProcessError: If the docker-compose up command fails.
    """
    logging.info(f"Starting services with Docker Compose file located at {compose_file}...")
    try:
        process = subprocess.Popen(['docker-compose', '-f', compose_file, 'up', '-d'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True)

        # Show the output of the subprocess in real time
        for line in process.stdout:
            print(line, end='')

        # Wait for the process to finish and check the return code
        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, process.args)
        logging.info("Services started successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start services with Docker Compose: {e}")

def main():
    """
    Main execution function: builds the Docker images for the APIs and starts the services using Docker Compose.
    """
    try:
        # Stop and clean up any previous services
        docker_compose_file = get_absolute_path('docker-compose.yml')
        docker_compose_down(docker_compose_file)

        # Start the services with Docker Compose
        docker_compose_up(docker_compose_file)
    except Exception as e:
        logging.exception("An unexpected error occurred during the build and deployment process: %s", e)

if __name__ == "__main__":
    main()