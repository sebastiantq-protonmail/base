from datetime import datetime
import logging

from fastapi import APIRouter, HTTPException, Request, status
from slowapi.errors import RateLimitExceeded

# 
from app.api.config.env import API_NAME
from app.api.config.limiter import limiter
from app.api.config.logger import logger
from app.api.config.dag import dag

from app.api.models.transaction import Transaction, TransactionCreate
from app.api.models.responses import Response, ResponseError

from app.api.methods.errors import handle_error

router = APIRouter()

# Endpoint to send a new transaction
@router.post('/', 
            response_model=Response[tuple[str, dict]], 
            status_code=status.HTTP_200_OK, 
            tags=["TRANSACTIONS"],
            responses={
                500: {"model": ResponseError, "description": "Internal server error."},
                429: {"model": ResponseError, "description": "Too many requests."},
                200: {"model": Response[tuple[str, dict]], "description": "The transaction was created successfully."}
            })
@limiter.limit("5/minute")
def send_transaction(request: Request, transaction: TransactionCreate):
    """
    Send a new transaction and add it to the DAG.

    Args:
    - transaction: Transaction

    Returns:
    - tuple[str, dict]: The transaction sended with the transaction id
    """
    try:
        logger.info(f"Creating transaction: {transaction}")
        
        # Set the created timestamp
        transaction.created = datetime.utcnow()

        valid = dag.add_transaction(transaction)

        # Calculate the transaction hash
        transaction_id = transaction.generate_transaction_id()

        if not valid:
            logger.error(f"The transaction from {transaction.sender} is not valid.")
            raise HTTPException(status_code=400, detail="The transaction is not valid.")
        
        return Response(data=(transaction_id, transaction.dict()), message="The transaction was created successfully.")
    except RateLimitExceeded:
        raise HTTPException(status_code=429, detail="Too many requests.")
    except HTTPException:
        # This is to ensure HTTPException is not caught in the generic Exception
        raise
    except Exception as e:
        handle_error(e, logger)