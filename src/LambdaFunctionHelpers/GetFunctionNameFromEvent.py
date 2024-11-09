from typing import List

def get_function_name_from_event(event: dict, accepted_functions: List[str]) -> str:
    # Check that function_name is in event
    if "function_name" not in event:
        raise Exception("Missing function_name")
        
    # Get function name
    function_name = event['function_name']
        
    # Check that function_name is in accepted functions
    if function_name not in accepted_functions:
        raise Exception(f"Invalid function_name {function_name}. Accepted functions {accepted_functions}")

    return function_name