# methods/ghost_transactions.py

import time
import networkx as nx
import matplotlib.pyplot as plt

from datetime import datetime

# Import GENESIS wallet's keys
from app.api.config.env import GENESIS_PUBLIC_KEY, GENESIS_PRIVATE_KEY

# Import Transaction model
from app.api.models.transaction import TransactionCreate, OperationType

# Import encode and decode methods
from app.api.methods.wallets import encode

def send_ghost_transaction(dag) -> None:
    """
    Function to send ghost transactions to the DAG to validate unvalidated transactions.
    
    Args:
    - dag: DAGBlockchain
    
    Returns:
    - None
    """
    while True:
        try:
            #print("Creando transacción fantasma...")

            new_tx = TransactionCreate(sender=GENESIS_PUBLIC_KEY,
                                       recipient=GENESIS_PUBLIC_KEY,
                                       payload=encode(b""),
                                       operation_type=OperationType.CALL,
                                       created=datetime.utcnow())
            new_tx.sign_transaction(GENESIS_PRIVATE_KEY)
            valid = dag.add_transaction(new_tx)

            #print(f"Transacción fantasma creada: {new_tx.created}")
            
            if not valid:
                print(f"Transacción inválida: {new_tx}")
        except Exception as e:
            print(f"Error: {e}")
            
        dag.save_dag_to_json()

        # DAGBlockchain graph visualization
        #nx.draw(dag.graph, with_labels=False, font_weight='bold', node_size=700, node_color='lightblue')
        #plt.show()

        #print("Sleping...")
        time.sleep(60)