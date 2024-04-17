import logging

from fastapi import APIRouter, HTTPException, Request, status
from slowapi.errors import RateLimitExceeded

# 
from app.api.config.env import API_NAME
from app.api.config.limiter import limiter
from app.api.config.logger import logger
from app.api.config.dag import dag

from app.api.models.responses import Response, ResponseError

from app.api.methods.errors import handle_error
from app.api.methods.wallets import generate_wallet

router = APIRouter()

@router.post('/generate/', 
            response_model=Response[dict], 
            status_code=status.HTTP_200_OK, 
            tags=["WALLETS"],
            responses={
                500: {"model": ResponseError, "description": "Internal server error."},
                429: {"model": ResponseError, "description": "Too many requests."},
                200: {"model": Response[dict], "description": "The keys were generated successfully."}
            })
@limiter.limit("5/minute")
def generate_wallet(request: Request):#, auth=Depends(auth_handler.authenticate)):
    """
    Generate a new post-quantum public-private key pair.

    Returns:
    - tuple[str, str]: The private and public keys
    """
    try:
        logger.info(f"Generating keys...")
        private_key, public_key = generate_wallet()
        return Response(data={ "public_key": public_key, "private_key": private_key }, message="The keys were generated successfully.")
    except RateLimitExceeded:
        raise HTTPException(status_code=429, detail="Too many requests.")
    except HTTPException:
        # This is to ensure HTTPException is not caught in the generic Exception
        raise
    except Exception as e:
        handle_error(e, logger)

# Endpoint to get the wallets balances
@router.get('/balances/', 
            response_model=Response[dict], 
            status_code=status.HTTP_200_OK, 
            tags=["WALLETS"],
            responses={
                500: {"model": ResponseError, "description": "Internal server error."},
                429: {"model": ResponseError, "description": "Too many requests."},
                200: {"model": Response[dict], "description": "The wallets balances were retrieved successfully."}
            })
@limiter.limit("5/minute")
def get_balances(request: Request):
    """
    Get the balances of all the wallets.

    Returns:
    - dict: The balances of all the wallets
    """
    try:
        logger.info(f"Getting balances...")
        return Response(data=dag.get_balances(), message="The wallets balances were retrieved successfully.")
    except RateLimitExceeded:
        raise HTTPException(status_code=429, detail="Too many requests.")
    except HTTPException:
        # This is to ensure HTTPException is not caught in the generic Exception
        raise
    except Exception as e:
        handle_error(e, logger)