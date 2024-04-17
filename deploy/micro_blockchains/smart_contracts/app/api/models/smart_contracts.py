import base64
import marshal
import dis
import types

from typing import Optional
from pydantic import BaseModel

class SmartContract(BaseModel):
    """
    The SmartContract class is a contract that contains a dictionary of functions.

    Args:
    - bytecode: Optional[str]: Base64 encoded bytecode (bytes)
    - state: dict: The state of the contract.
    """
    bytecode: Optional[str] = "" # Base64 encoded bytecode (bytes)
    state: dict = {}
    
    def extract_functions(self) -> dict:
        """
        Extract all functions from the contract's bytecode.
        """
        functions = {}
        
        # Deserialize the bytecode
        serialized_bytecode = base64.b64decode(self.bytecode)
        bytecode = marshal.loads(serialized_bytecode)

        for instruction in dis.get_instructions(bytecode):
            if instruction.opname == "LOAD_GLOBAL":
                function_name = instruction.argval
                function_code = self.extract_function_code(function_name)
                functions[function_name] = function_code
        return functions
    
    def extract_function_code(self, function_name) -> list[types.CodeType]:
        """
        Extract a function's code from the contract's bytecode.
        """
        function_code = []
        function_started = False
        
        # Deserialize the bytecode
        serialized_bytecode = base64.b64decode(self.bytecode)
        bytecode = marshal.loads(serialized_bytecode)

        for instruction in dis.get_instructions(bytecode):
            if instruction.opname == "LOAD_GLOBAL":
                if instruction.argval == function_name:
                    function_started = True
            if function_started:
                function_code.append(instruction)
            if instruction.opname == "RETURN_VALUE":
                function_started = False
        return function_code