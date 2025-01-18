from typing import Optional
from AWS.Lambda import LambdaEvent
from AWS.Cognito import CognitoUser
import requests
from pydantic import BaseModel

class ScrapePageResponse(BaseModel):
    page_content: str

def scrape_page_handler(lambda_event: LambdaEvent, user: Optional[CognitoUser]) -> ScrapePageResponse: 
    # Get the path parameters
    link = lambda_event.requestParameters.get("link")
    if not link:
        raise Exception("link is required", 400)
    
    # Make the GET request
    response = requests.get(f"https://r.jina.ai/{link}")
    
    # Check for request success
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page: {response.status_code}", response.status_code)
    
    # Extract the page content
    page_content = response.text

    # Return the page content in the response
    return ScrapePageResponse(page_content=page_content)
