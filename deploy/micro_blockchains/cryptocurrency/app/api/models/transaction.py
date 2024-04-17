# models/transaction.py

import oqs

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from hashlib import sha256

# Import the GENESIS_PUBLIC_KEY from the config.envs file
from app.api.config.env import GENESIS_PUBLIC_KEY

# Import the keys methods
from app.api.methods.wallets import encode, decode

class TransactionCreate(BaseModel):
    """
    TransactionCreate Model
    
    Args:
    - sender: str
    - amount: float
    - recipient: str
    - signature: str
    - created: datetime
    """
    sender: str = Field(default=..., description="The public key of the sender")
    amount: float = Field(default=..., description="The amount of the transaction")
    recipient: str = Field(default=..., description="The public key of the recipient")
    signature: Optional[str] = Field(default=None, description="The signature of the transaction")
    created: Optional[datetime] = Field(default_factory=datetime.utcnow, description="The timestamp of the transaction")

    @validator('amount')
    def amount_must_be_positive(cls, value, values, **kwargs):
        """
        Validate that the amount is greater than 0
        
        Args:
        - value: float
        - values: dict
        - kwargs: dict
        
        Returns:
        - float

        Raises:
        - ValueError
        """
        if (values.get('sender') != GENESIS_PUBLIC_KEY and \
            values.get('recipient') != GENESIS_PUBLIC_KEY and \
            values.get('signature') != "") and \
           (value <= 0):
            raise ValueError('Amount must be greater than 0')
        
        return value

    def generate_transaction_id(self) -> str:
        """
        Generate the HASH of the transaction with the following fields:
        - sender
        - amount
        - recipient
        - created

        Returns:
        - str
        """
        transaction_content = f"{self.sender}{self.amount}{self.recipient}".encode()
        return sha256(transaction_content).hexdigest()

    def sign_transaction(self, private_key_str) -> None:
        """
        Sign the transaction with the private key
        
        Args:
        - private_key_str: str
        """
        sigalg = "Dilithium2"
        transaction_content = f"{self.sender}{self.amount}{self.recipient}"
        private_key_str = decode(private_key_str)
        
        with oqs.Signature(sigalg) as signer:
            with oqs.Signature(sigalg) as verifier:
                signer = oqs.Signature(sigalg, private_key_str)

                # signer signs the message
                self.signature = encode(signer.sign(transaction_content.encode())) # Sign and encode to Base64

    class Config:
        """
        Pydantic Config
        
        Args:
        - arbitrary_types_allowed: bool
        - json_encoders: dict
        """
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        schema_extra = {
            "example": {
                "sender": "public_key",
                "amount": 0.0,
                "recipient": "public_key",
                "signature": "signature",
            }
        }

class Transaction(TransactionCreate):
    """
    Transaction Model
    
    Args:
    - id: str
    - nonce: int
    - parents: list
    - created: datetime
    - processed: datetime

    Returns:
    - Transaction: A new instance of the Transaction model
    """
    id: str = Field(default=None, description="The ID of the transaction")
    nonce: int = Field(default_factory=int, description="The nonce of the transaction")
    parents: list = Field(default_factory=list)
    processed: datetime = Field(default=None, description="The timestamp of the transaction processing")

    def is_signature_valid(self) -> bool:
        """
        Check if the signature is valid

        Returns:
        - bool

        Raises:
        - BadSignatureError
        """
        sigalg = "Dilithium2"
        is_valid = False
        public_key = decode(self.sender) # Decode the public key from Base64
        signature = decode(self.signature)

        transaction_content = f"{self.sender}{self.amount}{self.recipient}".encode()

        with oqs.Signature(sigalg) as signer:
            with oqs.Signature(sigalg) as verifier:
                # verifier verifies the signature
                is_valid = verifier.verify(transaction_content, signature, public_key)

        return is_valid
            
    class Config:
        """
        Pydantic Config
        
        Args:
        - arbitrary_types_allowed: bool
        - json_encoders: dict
        """
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }