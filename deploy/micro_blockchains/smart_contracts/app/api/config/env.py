import os

# Basic configuration
API_NAME = os.getenv('API_NAME')
JWT_SECRET = os.getenv('JWT_SECRET') # The JWT secret string
MONGO_CLIENT = os.getenv('MONGO_CLIENT') # Something like: mongodb://[username:password@]host1[:port1][,...hostN[:portN]][/[defaultauthdb][?options]]
DB_NAME = os.getenv('DB_NAME')
PRODUCTION_SERVER_URL = os.getenv('PRODUCTION_SERVER_URL')
DEVELOPMENT_SERVER_URL = os.getenv('DEVELOPMENT_SERVER_URL')
LOCALHOST_SERVER_URL = os.getenv('LOCALHOST_SERVER_URL')
IS_PRODUCTION = os.getenv('IS_PRODUCTION') # Boolean to determine if is prod environment or nah

# IncidentsBug library configuration
JIRA_PROJECT_ID = os.getenv('JIRA_PROJECT_ID')
RABBIT_USER = os.getenv('RABBIT_USER') # Your Jira credentials
RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD')
RABBITMQ_IP = os.getenv('RABBITMQ_IP') # Ask someone for the assigned server for this project
RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE')

# N8 configuration
N8_IP = os.getenv('N8_IP')
N8_USER = os.getenv('N8_USER')
N8_PASSWORD = os.getenv('N8_PASSWORD')

# MQTT Broker configuration
MQTT_BROKER_USERNAME = os.getenv('MQTT_BROKER_USERNAME')
MQTT_BROKER_PASSWORD = os.getenv('MQTT_BROKER_PASSWORD')

# DAG configuration
GENESIS_PRIVATE_KEY = os.getenv('GENESIS_PRIVATE_KEY')
GENESIS_PUBLIC_KEY = os.getenv('GENESIS_PUBLIC_KEY')

# 
SEBASTIAN_PRIVATE_KEY = os.getenv('SEBASTIAN_PRIVATE_KEY')
SEBASTIAN_PUBLIC_KEY = os.getenv('SEBASTIAN_PUBLIC_KEY')