import time
import hashlib

# Voting structure
class Voting:
    def __init__(self, creator, vote_type, options, public, deadline, weight_by_token):
        self.creator = creator
        self.vote_type = vote_type  # 'binary' o 'multiple'
        self.options = options if vote_type == 'multiple' else ['yes', 'no']
        self.public = public
        self.deadline = deadline
        self.weight_by_token = weight_by_token
        self.voters = {} # Dict to store the voters and their votes
        self.results = None

global_voting_counter = 0  # Global counter for votings

# Function to create a new voting
def create_voting(creator, vote_type, options, public, deadline, weight_by_token):
    """
    Create a new voting in the system.

    Parameters:
    creator (str): Public key of the voting creator.
    vote_type (str): Type of voting ('si_no' or 'multiple').
    options (list): Options for voting, applicable for 'multiple' type.
    public (bool): True for public voting, False for private.
    deadline (int): Timestamp for the voting deadline.
    weight_by_token (bool): True if the vote weight depends on token amount.

    Returns:
    str: ID of the created voting.
    """
    global global_voting_counter

    if vote_type not in ['binary', 'multiple']:
        raise ValueError("Invalid voting type. Choose 'binary' or 'multiple'.")

    #if deadline <= int(time.time()):
    #    raise ValueError("The deadline must be set in the future.")

    # Increment the global counter
    global_voting_counter += 1

    # Create a unique hash ID for the voting
    voting_id = hashlib.sha256(f"{creator}{vote_type}{options}{public}{deadline}{global_voting_counter}".encode()).hexdigest()

    new_voting = Voting(creator, vote_type, options, public, deadline, weight_by_token)
    state["votings"][voting_id] = new_voting

    return voting_id

# Function to add voters in batch
def add_voters_batch(voting_id, voters, assigned_tokens, public_key):
    """
    Add a batch of voters to a specific voting.

    Parameters:
    voting_id (str): ID of the voting.
    voters (list): List of public keys of the voters.
    assigned_tokens (int): Number of tokens assigned to each voter.
    public_key (str): Public key of the user calling the function.

    Returns:
    bool: True if the voters were added successfully, False otherwise.
    """
    # Check if the voting exists
    voting = state["votings"].get(voting_id)
    if not voting:
        raise ValueError("Voting not found.")

    # Check if the request is made by the voting creator
    if voting.creator != public_key:
        raise PermissionError("Only the voting creator can add voters.")

    # Add the voters
    for voter in voters:
        voting.voters[voter] = {
            "tokens": assigned_tokens,
            "has_voted": False
        }

    return True

# Function to add a voter to a voting
def add_voter(voting_id, voter, assigned_tokens, public_key):
    """
    Add a voter to a specific voting.

    Parameters:
    voting_id (str): ID of the voting.
    voter (str): Public key of the voter.
    assigned_tokens (int): Number of tokens assigned to the voter.
    public_key (str): Public key of the user calling the function.
    
    Returns:
    bool: True if the voter was added successfully, False otherwise.
    """
    # Check if the voting exists
    voting = state["votings"].get(voting_id)
    if not voting:
        raise ValueError("Voting not found.")

    # Check if the request is made by the voting creator
    if voting.creator != public_key:
        raise PermissionError("Only the voting creator can add voters.")

    # Add the voter
    voting.voters[voter] = {
        "tokens": assigned_tokens,
        "has_voted": False
    }

    return True

# Function to vote in a voting considering public and private voting types
def vote(voting_id, voter, vote):
    """
    Cast a vote in a specific voting, considering public and private voting types.

    Parameters:
    voting_id (str): ID of the voting.
    voter (str): Public key of the voter.
    vote: Vote cast by the voter, can be encrypted for private votings.

    Returns:
    bool: True if the vote was cast successfully, False otherwise.
    """
    # Check if the voting exists and is open
    voting = state["votings"].get(voting_id)
    if not voting:
        raise ValueError("Voting not found.")
    if int(time.time()) > voting.deadline:
        raise ValueError("The voting period has ended.")

    # Check if the voter is eligible and has not voted
    if voter not in voting.voters or voting.voters[voter]["has_voted"]:
        raise PermissionError("Voter is not eligible or has already voted.")

    # Encrypt the vote for private votings
    if not voting.public:
        vote = encrypt_vote(vote)

    # Cast the vote
    voting.voters[voter]["vote"] = vote
    voting.voters[voter]["has_voted"] = True

    return True

# Function to encrypt a vote (placeholder, needs proper encryption implementation)
def encrypt_vote(vote):
    """
    Encrypt a vote for private voting.

    Parameters:
    vote: Vote to be encrypted.

    Returns:
    Encrypted vote.
    """
    # This is a placeholder for encryption logic
    return "encrypted_" + str(vote)

# Function to decrypt a vote (simulated decryption)
def decrypt_vote(encrypted_vote):
    """
    Decrypt a vote for private voting.

    Parameters:
    encrypted_vote: Encrypted vote.

    Returns:
    Decrypted vote.
    """
    return encrypted_vote.replace("encrypted_", "")

# Function to show the results of a voting
def show_results(voting_id):
    """
    Calculate and display the results of a specific voting.

    Parameters:
    voting_id (str): ID of the voting.

    Returns:
    dict: A dictionary with the results of the voting.
    """
    # Check if the voting exists
    voting = state["votings"].get(voting_id)
    if not voting:
        raise ValueError("Voting not found.")

    # Check if the voting period has ended
    if int(time.time()) <= voting.deadline:
        raise ValueError("The voting is still ongoing.")

    # Initialize the results dictionary
    results = {option: 0 for option in voting.options}

    # Calculate the results
    for voter, info in voting.voters.items():
        if info["has_voted"]:
            vote = info["vote"]

            # Decrypt the vote for private votings
            if not voting.public:
                vote = decrypt_vote(vote)

            vote_weight = info["tokens"] if voting.weight_by_token else 1
            results[vote] += vote_weight

    # Store the results in the voting object
    voting.results = results

    return results

# Function to assign tokens to a voter
def assign_tokens(voting_id, voter, amount, public_key):
    """
    Assign tokens to a voter in a specific voting.

    Parameters:
    voting_id (str): ID of the voting.
    voter (str): Public key of the voter.
    amount (int): Number of tokens to assign.
    public_key (str): Public key of the user calling the function.

    Returns:
    bool: True if tokens were assigned successfully, False otherwise.
    """
    voting = state["votings"].get(voting_id)
    if not voting:
        raise ValueError("Voting not found.")
    if int(time.time()) > voting.fecha_limite:
        raise ValueError("The voting period has ended.")

    if voting.creator != public_key:
        raise PermissionError("Only the voting creator can assign tokens.")

    if voter not in voting.voters:
        raise ValueError("Voter not found in the voting.")

    voting.voters[voter]["tokens"] = amount
    return True

def initialize_smart_contract():
    """
    Initialize the global state of the smart contract.

    Returns:
    None
    """
    # Global structure to store the state of the smart contract
    if "votings" not in state:
        state["votings"] = {}

    if "tokens" not in state:
        state["tokens"] = {}