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

router = APIRouter()

# Endpoint to get the smart contracts
@router.get('/', 
            response_model=Response[dict], 
            status_code=status.HTTP_200_OK, 
            tags=["WALLETS"],
            responses={
                500: {"model": ResponseError, "description": "Internal server error."},
                429: {"model": ResponseError, "description": "Too many requests."},
                200: {"model": Response[dict], "description": "The smart contracts were retrieved successfully."}
            })
#@limiter.limit("5/minute")
def get_smart_contracts(request: Request):
    """
    Endpoint to get the smart contracts.
    
    Args:
    - request: Request
    
    Returns:
    - Response[dict]: The smart contracts were retrieved successfully.
    """
    try:
        # Get the smart contracts
        smart_contracts = dag.python_virtual_machine.get_smart_contracts()
        
        # Return the smart contracts
        return Response(data=smart_contracts, message="The smart contracts were retrieved successfully.")
    except RateLimitExceeded:
        raise HTTPException(status_code=429, detail="Too many requests.")
    except HTTPException:
        # This is to ensure HTTPException is not caught in the generic Exception
        raise
    except Exception as e:
        handle_error(e, logger)

# Endpoint to get a smart contract by its address
@router.get('/{contract_address}/', 
            response_model=Response[dict], 
            status_code=status.HTTP_200_OK, 
            tags=["WALLETS"],
            responses={
                500: {"model": ResponseError, "description": "Internal server error."},
                429: {"model": ResponseError, "description": "Too many requests."},
                200: {"model": Response[dict], "description": "The smart contract was retrieved successfully."}
            })
#@limiter.limit("5/minute")
def get_smart_contract(contract_address: str, request: Request):
    """
    Endpoint to get a smart contract by its address.
    
    Args:
    - contract_address: str
    - request: Request
    
    Returns:
    - Response[dict]: The smart contract was retrieved successfully.
    """
    try:
        # Get the smart contract
        smart_contract = dag.python_virtual_machine.get_smart_contract(contract_address)
        
        if len(smart_contract) == 0:
            raise HTTPException(status_code=404, detail="The smart contract was not found.")

        # Return the smart contract
        return Response(data=smart_contract, message="The smart contract was retrieved successfully.")
    except RateLimitExceeded:
        raise HTTPException(status_code=429, detail="Too many requests.")
    except HTTPException:
        # This is to ensure HTTPException is not caught in the generic Exception
        raise
    except Exception as e:
        handle_error(e, logger)