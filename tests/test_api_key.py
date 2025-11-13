import json
import unittest
import sys
sys.path.append("../")
from tests.helper_funcs import create_request
from tests.config import access_token
from src.lambda_function import lambda_handler
from src.AWS import Cognito
from src.Models import APIKey, User, Agent

class TestAPIKey(unittest.TestCase):
    
    def test_generate_api_key(self):
        """Test generating an API key"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        body = {
            "org_id": org_id
        }
        
        request = create_request(
            method="POST",
            path="/generate-api-key",
            headers={"Authorization": access_token},
            body=body
        )
        
        result = lambda_handler(request, None)
        self.assertEqual(result["statusCode"], 200)
        
        res_body = json.loads(result["body"])
        self.assertIn("api_key_id", res_body)
        self.assertIn("token", res_body)
        self.assertEqual(res_body["org_id"], org_id)
        self.assertTrue(res_body["valid"])
        
        # Store for cleanup
        api_key_id = res_body["api_key_id"]
        
        # Clean up
        APIKey.delete_api_key(api_key_id)
    
    def test_generate_api_key_unauthorized_email(self):
        """Test that non-authorized emails cannot generate API keys"""
        # This test would need a different user token
        # For now, we'll skip this as it requires a different test user
        pass
    
    def test_authenticate_with_api_key(self):
        """Test authenticating with an API key"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # First, generate an API key
        api_key = APIKey.create_api_key(org_id=org_id)
        
        try:
            # Use the API key token to access a protected endpoint
            request = create_request(
                method="GET",
                path="/agents",
                headers={"Authorization": api_key.token},
                body={}
            )
            
            result = lambda_handler(request, None)
            self.assertEqual(result["statusCode"], 200)
            
            # The request should succeed because the API key is valid
            res_body = json.loads(result["body"])
            self.assertIn("agents", res_body)
            
        finally:
            # Clean up
            APIKey.delete_api_key(api_key.api_key_id)
    
    def test_revoked_api_key_fails(self):
        """Test that a revoked API key cannot authenticate"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Generate an API key
        api_key = APIKey.create_api_key(org_id=org_id)
        
        try:
            # Revoke it
            APIKey.revoke_api_key(api_key.api_key_id)
            
            # Try to use it
            request = create_request(
                method="GET",
                path="/agents",
                headers={"Authorization": api_key.token},
                body={}
            )
            
            result = lambda_handler(request, None)
            self.assertEqual(result["statusCode"], 401)
        finally:
            # Clean up
            APIKey.delete_api_key(api_key.api_key_id)
    
    def test_api_key_can_create_agent(self):
        """Test that an API key can be used to create an agent"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        # Generate an API key
        api_key = APIKey.create_api_key(org_id=org_id)
        
        try:
            # Use API key to create an agent
            agent_body = {
                "agent_name": "api-key-test-agent",
                "agent_description": "Agent created by API key",
                "prompt": "You are a helpful assistant",
                "org_id": org_id,
                "is_public": False,
                "agent_speaks_first": False
            }
            
            request = create_request(
                method="POST",
                path="/agent",
                headers={"Authorization": api_key.token},
                body=agent_body
            )
            
            result = lambda_handler(request, None)
            self.assertEqual(result["statusCode"], 200)
            
            res_body = json.loads(result["body"])
            self.assertIn("agent_id", res_body)
            self.assertEqual(res_body["agent_name"], "api-key-test-agent")
            
            # Clean up agent
            Agent.delete_agent(res_body["agent_id"])
            
        finally:
            # Clean up API key
            APIKey.delete_api_key(api_key.api_key_id)
    
    def test_api_key_org_isolation(self):
        """Test that API key can only access resources from its org"""
        # This would require creating resources in different orgs
        # Skipping for now as it requires more complex setup
        pass
    
    def test_validate_api_key(self):
        """Test the validate_api_key function"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        api_key = APIKey.create_api_key(org_id=org_id)
        
        try:
            # Valid key should return True
            self.assertTrue(APIKey.validate_api_key(api_key.token))
            
            # Revoked key should return False
            APIKey.revoke_api_key(api_key.api_key_id)
            self.assertFalse(APIKey.validate_api_key(api_key.token))
            
            # Invalid token should return False
            self.assertFalse(APIKey.validate_api_key("invalid-token"))
        finally:
            # Clean up
            APIKey.delete_api_key(api_key.api_key_id)
    
    def test_get_api_key_contents(self):
        """Test extracting contents from API key"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        api_key = APIKey.create_api_key(org_id=org_id)
        
        try:
            contents = APIKey.get_api_key_contents(api_key.token)
            self.assertEqual(contents["api_key_id"], api_key.api_key_id)
            self.assertEqual(contents["org_id"], org_id)
        finally:
            APIKey.delete_api_key(api_key.api_key_id)
    
    def test_user_get_with_api_key(self):
        """Test that User.get_user() works with API key ID"""
        
        # Set up
        cognito_user = Cognito.get_user_from_cognito(access_token)
        user = User.get_user(cognito_user.sub)
        org_id = user.organizations[0]
        
        api_key = APIKey.create_api_key(org_id=org_id)
        
        try:
            # Get "user" using API key ID
            mocked_user = User.get_user(api_key.api_key_id)
            
            # Should return a mocked User with the API key's org
            self.assertEqual(mocked_user.user_id, api_key.api_key_id)
            self.assertEqual(mocked_user.organizations, [org_id])
        finally:
            APIKey.delete_api_key(api_key.api_key_id)


