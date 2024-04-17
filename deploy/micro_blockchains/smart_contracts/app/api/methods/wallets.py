# methods/wallets.py

import oqs
import base64

def encode(data):
    """Codify a data in Base64."""
    return base64.b64encode(data).decode()

def decode(data):
    """Decodify a Base64 encoded data."""
    return base64.b64decode(data)

def generate_wallet():
    """ Generate a new post-quantum public-private key pair. """
    kemalg = "Kyber512"
    with oqs.KeyEncapsulation(kemalg) as client:
        with oqs.KeyEncapsulation(kemalg) as server:
            public_key_client = client.generate_keypair()
            secret_key_client = client.export_secret_key()
    return encode(secret_key_client), encode(public_key_client)

def sign_transaction(transaction_hash, secret_key):
    """ Sign a transaction with a post-quantum private key. """
    sigalg = "Dilithium2"
    signature = None
    secret_key = decode(secret_key)
    
    with oqs.Signature(sigalg) as signer:
        with oqs.Signature(sigalg) as verifier:
            signer = oqs.Signature(sigalg, secret_key)

            # signer signs the message
            signature = signer.sign(transaction_hash.encode())

    return encode(signature)
    
def verify_signature(transaction_hash, signature, public_key):
    """ Verify the signature of a transaction with a post-quantum public key. """
    sigalg = "Dilithium2"
    is_valid = False
    public_key = decode(public_key)
    signature = decode(signature)
    with oqs.Signature(sigalg) as signer:
        with oqs.Signature(sigalg) as verifier:
            # verifier verifies the signature
            is_valid = verifier.verify(transaction_hash, signature, public_key)

    return is_valid
