# models/dag.py

from copy import deepcopy
import json
import os
import networkx as nx

from threading import Thread
from datetime import datetime
from pydantic import BaseModel, Field

# Import the Transaction model
from app.api.models.transaction import Transaction, TransactionCreate

# Import the send_ghost_transaction funcion from methods
from app.api.methods.ghost_transactions import send_ghost_transaction

# Import GENESIS wallet's keys
from app.api.config.env import GENESIS_PUBLIC_KEY, GENESIS_PRIVATE_KEY

class DAGBlockchain(BaseModel):
    """
    DAGBlockchain Model (Directed Acyclic Graph) to represent a blockchain with a DAG structure.

    Args:
    - graph: nx.DiGraph
    - nonce_registry: dict
    - balances: dict

    Returns:
    - DAGBlockchain: A new instance of the DAGBlockchain model
    """
    graph: nx.DiGraph = Field(default_factory=nx.DiGraph, description="The graph representing the DAG.")
    nonce_registry: dict = Field(default_factory=dict, description="A simple registry of nonces for each sender.")
    balances: dict = Field(default_factory=dict, description="A registry to keep track of balances for each address.")

    def __init__(self, **data):
        """
        Constructor for the DAGBlockchain model. It initializes the graph with a genesis transaction.

        Args:
        - data: dict

        Returns:
        - None
        """
        super().__init__(**data)
        # Check if the JSON file exists
        if os.path.isfile(self.get_json_file_path()):
            self.load_dag_from_json()
            self.rebuild_states_from_graph()
        else:
            # Create the genesis transaction
            genesis_transaction = Transaction(sender=GENESIS_PUBLIC_KEY,
                                              recipient=GENESIS_PUBLIC_KEY,
                                              amount=0.0,
                                              created=datetime.now())
            genesis_transaction.sign_transaction(GENESIS_PRIVATE_KEY)
            genesis_transaction.nonce = self.nonce_registry.get(genesis_transaction.sender, 0) + 1
            genesis_transaction.id = genesis_transaction.generate_transaction_id()

            # Add the genesis transaction to the graph
            self.graph.add_node(node_for_adding=genesis_transaction.id, transaction=genesis_transaction)

        # Once the DAG is initialized, start to send ghost transactions in background
        self.start_ghost_transactions()

    def get_balances(self):
        """
        Get the balances for each address in the blockchain.
        """
        return self.balances

    def is_acyclic(self):
        """
        Check if the DAG is acyclic.
        """
        return nx.is_directed_acyclic_graph(self.graph)

    def get_json_file_path(self):
        """
        Get the JSON file path.
        """
        actual_file_path = os.path.realpath(__file__)
        actual_directory_path = os.path.dirname(actual_file_path)
        
        # Split the path into components
        actual_path_components = actual_directory_path.split(os.sep)

        # Modify the last component to change the directory
        # We want to change the directory from "models" to "shared"
        actual_path_components[-1] = "shared"

        # Join the components back together
        shared_directory_path = os.sep.join(actual_path_components)

        # Return the path to the JSON file
        shared_directory_path = os.path.join(shared_directory_path, "dag.json")

        return shared_directory_path

    def save_dag_to_json(self) -> None:
        """
        Function to save the DAG to a JSON file.
        """
        # Create a structure to save nodes and edges
        data = {
            "nodes": [],
            "edges": []
        }

        # Iterate nodes and save relevant transactions information
        for node in self.graph.nodes(data=True):
            node_data = deepcopy(node[1]['transaction'].__dict__)
            # Convert datetime to string to serialize
            node_data['created'] = node_data['created'].isoformat()
            if node_data['processed']:
                node_data['processed'] = node_data['processed'].isoformat()
            data["nodes"].append(node_data)

        # Save the edges
        data["edges"] = list(self.graph.edges())
        
        # Write the JSON file
        with open(self.get_json_file_path(), 'w') as f:
            json.dump(data, f, indent=4)

    def load_dag_from_json(self) -> None:
        """
        Function to load the DAG from a JSON file.
        """
        # Read the JSON file
        with open(self.get_json_file_path(), 'r') as f:
            data = json.load(f)
        
        self.graph.clear()

        # Rebuild the nodes (transactions)
        for node_data in data["nodes"]:
            # Convert the strings to datetime
            node_data['created'] = datetime.fromisoformat(node_data['created'])
            if node_data['processed']:
                node_data['processed'] = datetime.fromisoformat(node_data['processed'])
            # Add the node to the graph
            self.graph.add_node(node_data['id'], transaction=Transaction(**node_data))
        
        # Add the edges
        self.graph.add_edges_from(data["edges"])

    def rebuild_states_from_graph(self) -> None:
        """
        Function to rebuild the DAG Blockchain state from the JSON file.
        """
        # Ordenar las transacciones por fecha de creación
        transactions = sorted(
            [data['transaction'] for node, data in self.graph.nodes(data=True)],
            key=lambda tx: tx.created
        )

        for transaction in transactions:
            self.process_transaction(transaction)

    def start_ghost_transactions(self):
        """
        Start the send_ghost_transaction in a new thread to send the ghost transactions in background.
        This function is used to mantains the network activity and validate all the transactions.
        """
        # Start the send_ghost_transaction function in a new thread
        ghost_thread = Thread(target=send_ghost_transaction, args=(self,))
        ghost_thread.daemon = True # Ensure that the thread finishes when main program is finished
        ghost_thread.start()

    def add_transaction(self, transaction: TransactionCreate, parent_ids: list = None) -> bool:
        """
        Add a new transaction to the blockchain.

        Args:
        - transaction: Transaction
        - parent_ids: list

        Returns:
        - bool: True if the transaction was added successfully, False otherwise
        """
        # Create a new Transaction instance from the TransactionCreate model
        transaction = Transaction(**transaction.dict())

        # Update the nonce for the sender on the transaction
        transaction.nonce = self.nonce_registry.get(transaction.sender, 0) + 1
        
        # If the transaction is not valid, return False
        if not self.is_transaction_valid(transaction):
            return False
        
        if parent_ids is None:
            parent_ids = self.determine_parents_for_transaction(transaction)
        
        transaction.parents = parent_ids
        transaction.id = transaction.generate_transaction_id()

        # Add the transaction to the graph
        self.graph.add_node(node_for_adding=transaction.id, transaction=transaction)

        # Create edges between the transaction and its parents
        for parent_id in parent_ids:
            parent_transaction = self.graph.nodes[parent_id]['transaction']

            # Update the nonce for the sender on the parent_transaction
            parent_transaction.nonce = self.nonce_registry.get(parent_transaction.sender, 0) + 1

            parent_is_valid_transaction = self.is_transaction_valid(parent_transaction)

            if parent_is_valid_transaction:
                self.graph.add_edge(transaction.id, parent_id)

                # If the parent transaction has been validated exactly 4 times, process it
                if self.graph.in_degree(parent_id) >= 4 and parent_transaction.processed is None:
                    transaction_processed = self.process_transaction(parent_transaction)

                    # If the transaction can't be processed, remove it from DAG
                    if not transaction_processed:
                        self.graph.remove_node(parent_id)

                    # Update the nonce registry for the sender
                    self.nonce_registry[parent_transaction.sender] = self.nonce_registry.get(parent_transaction.sender, 0) + 1
            else:
                print(f"Transacción padre {parent_id} no es válida")

                # Remove the parent transaction from the graph if it has no children
                if self.graph.out_degree(parent_id) == 0:
                    self.graph.remove_node(parent_id)

        return True

    def is_transaction_valid(self, transaction: Transaction) -> bool:
        """
        Validate a transaction before adding it to the blockchain.

        Args:
        - transaction: Transaction

        Returns:
        - bool: True if the transaction is valid, False otherwise
        """
        if not transaction.is_signature_valid():
            print(f"Firma inválida para la transacción {transaction.id}")
            return False
        
        # If the sender is the genesis public key, the transaction is valid
        if transaction.sender == GENESIS_PUBLIC_KEY:
            return True

        # Verify that the nonce is correct
        expected_nonce = self.nonce_registry.get(transaction.sender, 0) + 1
        if transaction.nonce != expected_nonce:
            print(f"Nonce incorrecto. Se esperaba {expected_nonce} pero se recibió {transaction.nonce}")
            return False
        
        # If passed all checks, return True
        return True

    def determine_parents_for_transaction(self, transaction: Transaction) -> list:
        """
        Determine the parents for a new transaction.

        Args:
        - transaction: Transaction

        Returns:
        - list: A list of transaction IDs for the parents of the new transaction
        """
        # Find all transactions with in-degree less than 4
        potential_parents = [node for node in self.graph.nodes if self.graph.in_degree(node) < 10]

        # Ensure that the transaction is not its own parent
        potential_parents = [tx_id for tx_id in potential_parents if tx_id != transaction.id]

        # Return the last two transactions with the lowest in-degree
        return potential_parents[-10:]

    def process_transaction(self, transaction: Transaction) -> bool:
        """
        Process a transaction by updating the balances of the sender and recipient.

        When a transaction is processed, the amount is subtracted from the sender's balance and added to the recipient's balance.

        Args:
        - transaction: Transaction

        Returns:
        - bool
        """
        try:
            # If the sender is not the genesis public key, subtract the amount from the sender's balance
            if transaction.sender != GENESIS_PUBLIC_KEY:
                # Verify that the sender has enough balance to send the amount
                sender_balance = self.balances.get(transaction.sender, 0)
                if sender_balance < transaction.amount:
                    print(f"El remitente {transaction.sender} no tiene suficiente saldo para enviar {transaction.amount}")
                    return False

                self.balances[transaction.sender] -= transaction.amount
            
            # Add the amount to the recipient's balance
            self.balances[transaction.recipient] = self.balances.get(transaction.recipient, 0) + transaction.amount
        
            # Mark the transaction as processed
            transaction.processed = datetime.utcnow()

            return True
        except Exception as e:
            print(f"Error al procesar la transacción {transaction.id}: {e}")
            return False
        
    class Config:
        """
        Pydantic configuration for the DAGBlockchain model.
        
        Args:
        - arbitrary_types_allowed: bool
        """
        arbitrary_types_allowed = True