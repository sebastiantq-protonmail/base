import requests

from datetime import datetime

# Import the server URL and the API name
from app.api.config.env import DEVELOPMENT_SERVER_URL, \
                               API_NAME, \
                               GENESIS_PUBLIC_KEY, \
                               GENESIS_PRIVATE_KEY, \
                               SEBASTIAN_PUBLIC_KEY, \
                               SEBASTIAN_PRIVATE_KEY

# Import the TransactionCreate model to create the transaction data
from app.api.models.transaction import TransactionCreate, OperationType

# Definir la URL del endpoint
ENDPOINT_URL = f"{DEVELOPMENT_SERVER_URL}api/v1/{API_NAME}/transactions/"

def send_transaction(sender, sender_private_key, payload, operation_type, created=None, contract_address=None):
    # Establecer la marca de tiempo de la transacción si no se proporciona
    if created is None:
        created = datetime.utcnow()

    # Crear el cuerpo de la solicitud
    transaction_data = TransactionCreate(
        sender=sender,
        payload=payload,
        contract_address=contract_address,
        operation_type=operation_type
    )
    transaction_data.sign_transaction(sender_private_key)
    
    # Convertir datetime a str
    transaction_data.created = transaction_data.created.isoformat()

    # Realizar la solicitud POST al endpoint
    response = requests.post(ENDPOINT_URL, json=transaction_data.dict())

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        print("Transacción enviada con éxito.")
        print("Respuesta:", response.json())
    else:
        print("Error al enviar la transacción.")
        print("Código de estado:", response.status_code)
        print("Respuesta:", response.text)

# Ejemplo de uso
def main():
    while True:
        print("1. Deploy Smart Contract")
        print("2. Call Smart Contract")
        print("0. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            smart_contract_file = input("Enter the smart contract file: ")
            payload = ""
            with open(smart_contract_file, "r") as file:
                payload = file.read()

            send_transaction(SEBASTIAN_PUBLIC_KEY, SEBASTIAN_PRIVATE_KEY, payload, OperationType.DEPLOY)
        elif choice == '2':
            contract_address = input("Enter contract address: ")
            payload = input("Enter the function signature: ")

            send_transaction(SEBASTIAN_PUBLIC_KEY, SEBASTIAN_PRIVATE_KEY, payload, OperationType.CALL, contract_address=contract_address)
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

#main()