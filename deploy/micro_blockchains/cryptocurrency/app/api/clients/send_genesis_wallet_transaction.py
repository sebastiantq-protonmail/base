import requests

from datetime import datetime

from app.api.models.transaction import TransactionCreate

from app.api.config.env import LOCALHOST_SERVER_URL, \
                               API_NAME, \
                               GENESIS_PUBLIC_KEY, \
                               GENESIS_PRIVATE_KEY, \
                               SEBASTIAN_PUBLIC_KEY \

# Definir la URL del endpoint
ENDPOINT_URL = f"{LOCALHOST_SERVER_URL}api/v1/{API_NAME}/transactions/"

def send_transaction(sender, sender_private_key, recipient, amount, created=None):
    # Establecer la marca de tiempo de la transacción si no se proporciona
    if created is None:
        created = datetime.utcnow()

    # Crear el cuerpo de la solicitud
    transaction_data = TransactionCreate(
        sender=sender,
        recipient=recipient,
        amount=amount,
        created=created
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
send_transaction(GENESIS_PUBLIC_KEY, GENESIS_PRIVATE_KEY, SEBASTIAN_PUBLIC_KEY, 100)
