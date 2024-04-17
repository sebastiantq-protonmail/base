import base64
from datetime import datetime
import marshal
import hashlib

from pydantic import BaseModel

from app.api.models.smart_contracts import SmartContract

class PythonVirtualMachine(BaseModel):
    deployed_smart_contracts: dict[str, SmartContract] = {}
    
    def get_smart_contracts(self) -> dict:
        """
        Get all the smart contracts.

        Returns:
        - dict
        """
        return self.deployed_smart_contracts

    def get_smart_contract(self, contract_address: str) -> dict:
        """
        Get a smart contract by its address.

        Args:
        - contract_address: str

        Returns:
        - dict
        """
        if contract_address in self.deployed_smart_contracts:
            return self.deployed_smart_contracts[contract_address]
        else:
            return {}

    def deploy_contract(self, contract_code: str, created: datetime) -> str:
        """
        Deploy a new contract to the VM. 
        Returns the contract's bytecode and an address (for this example, the address is just the bytecode's hash).
        """
        try:
            # Compile the contract
            bytecode = compile(contract_code, '<string>', 'exec')
            serialized_bytecode = marshal.dumps(bytecode)

            # TODO: Check if the contract has already been deployed
            # TODO: Add a timestamp to the contract's bytecode to avoid collisions
            #contract_address = hashlib.sha256(contract_code.encode()).hexdigest() # DEPRECATED by unsecure
            
            # Generate a unique address for the contract with Bytecode and Created
            contract_address = hashlib.sha256(serialized_bytecode + str(created).encode()).hexdigest()
            
            # Encode bytecode to base64 and create a new SmartContract instance
            base64_encoded_bytecode = base64.b64encode(serialized_bytecode).decode('utf-8')
            new_contract = SmartContract(bytecode=base64_encoded_bytecode)
            self.deployed_smart_contracts[contract_address] = new_contract

            return contract_address
        except Exception as e:
            print("Error deploying contract!", e)

    def execute_contract(self, contract_address: str, function_signature: str, args, kwargs):
        """
        Execute a function on a deployed contract.
        """
        # Check if the contract exists
        if contract_address not in self.deployed_smart_contracts:
            raise Exception("Contract not found!")
        
        print(f"Executing contract {contract_address}...")

        # Prepare the environment
        contract_state = self.deployed_smart_contracts[contract_address].state
        print("Initial Global State:", contract_state)
        
        global_env = {
            "state": contract_state,
            "__name__": "__main__"
        }

        # Decode the bytecode from base64 before deserializing
        serialized_bytecode = base64.b64decode(self.deployed_smart_contracts[contract_address].bytecode)
        bytecode = marshal.loads(serialized_bytecode)

        # Execute the bytecode to define the contract
        exec(bytecode, global_env)

        print("New Global State:", global_env['state'])
        
        # Extract the function from the bytecode based on its signature and execute it
        if function_signature in global_env:
            print(f"Executing function {function_signature}...")
            function = global_env[function_signature]
            result = function(*args, **kwargs)
            return result
        else:
            raise Exception(f"Function {function_signature} not found in contract!")