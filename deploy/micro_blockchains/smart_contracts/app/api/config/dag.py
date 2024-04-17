from app.api.models.dag import DAGBlockchain

# Instantiating the blockchain
dag = DAGBlockchain()

def get_blockchain():
    return dag

def reset_blockchain():
    global dag
    dag = DAGBlockchain()