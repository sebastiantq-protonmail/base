from typing import Union, Generic, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

DataT = TypeVar('DataT') # Declare type variable for generic data type

class ResponseError(BaseModel):
    """
    Data model for API error responses.
    
    Whenever the API encounters an error, be it a user-made error, a server error, or any other type of error,
    it will respond with this model. Having a standardized error response format ensures that clients can
    easily understand and handle errors consistently. The `detail` attribute provides a descriptive message 
    about the specific error, aiding in debugging and issue resolution.
    """
    detail: str

class Response(GenericModel, Generic[DataT]):
    """
    Data model for API responses.
    
    Whenever the API responds with data, it will use this model to wrap the data. This ensures that the 
    response is standardized and easy to understand for clients. The `data` attribute contains the actual 
    data being returned, and can be of any type.
    """
    message: Union[str, dict] # Message attribute can be a string or a dictionary
    data: DataT