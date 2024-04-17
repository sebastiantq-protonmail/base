import json
import time
from app.api.clients.deploy_smart_contract import send_transaction, SEBASTIAN_PRIVATE_KEY, SEBASTIAN_PUBLIC_KEY, GENESIS_PRIVATE_KEY, GENESIS_PUBLIC_KEY

from app.api.methods.wallets import encode

from app.api.models.transaction import OperationType

CONTRACT_ADDRESS="816ae56259aabfee7a0d77d749218ac27d237bb80cebcc96147094ffaf04d650"

def initialize_smart_contract():
    payload = {
        "function_signature": "initialize_smart_contract",
        "args": [],
        "kwargs": {}
    }
    send_transaction(SEBASTIAN_PUBLIC_KEY, SEBASTIAN_PRIVATE_KEY, payload, OperationType.CALL, contract_address=CONTRACT_ADDRESS)

def create_voting_client():
    vote_type = input("Enter voting type ('binary' or 'multiple'): ")
    options = input("Enter voting options (comma-separated) for 'multiple' type or leave blank: ").split(",") if vote_type == "multiple" else None
    public = input("Is the voting public? (yes/no): ").lower() == "yes"
    deadline = int(time.time()) + int(input("Enter voting duration in seconds: "))
    weight_by_token = input("Does vote weight depend on token amount? (yes/no): ").lower() == "yes"
    
    payload = {
        "function_signature": "create_voting",
        "args": [SEBASTIAN_PUBLIC_KEY, vote_type, options, public, deadline, weight_by_token],
        "kwargs": {}
    }
    send_transaction(SEBASTIAN_PUBLIC_KEY, SEBASTIAN_PRIVATE_KEY, payload, OperationType.CALL, contract_address=CONTRACT_ADDRESS)

def add_voter_client():
    voting_id = input("Enter voting ID: ")
    voter = input("Enter voter's public key: ")
    assigned_tokens = int(input("Enter number of tokens assigned to the voter: "))

    payload = {
        "function_signature": "add_voter",
        "args": [voting_id, voter, assigned_tokens, SEBASTIAN_PUBLIC_KEY],
        "kwargs": {}
    }
    send_transaction(SEBASTIAN_PUBLIC_KEY, SEBASTIAN_PRIVATE_KEY, payload, OperationType.CALL, contract_address=CONTRACT_ADDRESS)

# Paso 1: Cargar los documentos del archivo JSON
def cargar_documentos(ruta_json='/home/bassee/proyecto_base/deploy/micro_blockchains/smart_contracts/app/api/clients/documentos.json'):
    with open(ruta_json, 'r') as archivo:
        documentos = json.load(archivo)
    return documentos

# Paso 2 y 3: Modificar add_voter_client para aceptar parámetros y definir la nueva función
def add_voters_client_modificado(voting_id, voters, assigned_tokens=1):
    payload = {
        "function_signature": "add_voters_batch",
        "args": [voting_id, voters, assigned_tokens, SEBASTIAN_PUBLIC_KEY],
        "kwargs": {}
    }
    send_transaction(SEBASTIAN_PUBLIC_KEY, SEBASTIAN_PRIVATE_KEY, payload, OperationType.CALL, contract_address=CONTRACT_ADDRESS)

def vote_client():
    voting_id = input("Enter voting ID: ")
    vote = input("Enter your vote: ")
    
    payload = {
        "function_signature": "vote",
        "args": [voting_id, SEBASTIAN_PUBLIC_KEY, vote],
        "kwargs": {}
    }
    send_transaction(SEBASTIAN_PUBLIC_KEY, SEBASTIAN_PRIVATE_KEY, payload, OperationType.CALL, contract_address=CONTRACT_ADDRESS)

def show_results_client():
    voting_id = input("Enter voting ID: ")

    payload = {
        "function_signature": "show_results",
        "args": [voting_id],
        "kwargs": {}
    }
    send_transaction(SEBASTIAN_PUBLIC_KEY, SEBASTIAN_PRIVATE_KEY, payload, OperationType.CALL, contract_address=CONTRACT_ADDRESS)

def assign_tokens_client():
    voting_id = input("Enter voting ID: ")
    voter = input("Enter voter's public key: ")
    amount = int(input("Enter number of tokens to assign: "))
    
    payload = {
        "function_signature": "assign_tokens",
        "args": [voting_id, voter, amount, SEBASTIAN_PUBLIC_KEY],
        "kwargs": {}
    }
    send_transaction(SEBASTIAN_PUBLIC_KEY, SEBASTIAN_PRIVATE_KEY, payload, OperationType.CALL, contract_address=CONTRACT_ADDRESS)

# Integration of the Smart Contract functions in the menu
def menu():
    while True:
        print("0. Initialize smart contract")
        print("1. Create Voting")
        print("2. Add Voter")
        print("3. Cast Vote")
        print("4. Show Voting Results")
        print("5. Assign Tokens")
        print("6. Add Voters in Batch")
        print("7. Send ghost transaction")
        print("8. Exit")

        choice = input("Enter your choice: ")
        
        if choice == '0':
            initialize_smart_contract()
        elif choice == '1':
            create_voting_client()
        elif choice == '2':
            add_voter_client()
        elif choice == '3':
            vote_client()
        elif choice == '4':
            show_results_client()
        elif choice == '5':
            assign_tokens_client()
        elif choice == '6':
            documentos = cargar_documentos()  # Cargar documentos al iniciar el menú
            voting_id = input("Enter voting ID: ")  # Solicitar el voting ID una sola vez

            add_voters_client_modificado(voting_id, documentos)
        elif choice == '7':
            send_transaction(GENESIS_PUBLIC_KEY, GENESIS_PRIVATE_KEY, encode(b""), OperationType.CALL)
        elif choice == '8':
            break
        else:
            print("Invalid choice. Please try again.")

menu()