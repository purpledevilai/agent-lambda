from Models.Organization import create_organization, associate_user_with_organization
from Models.User import associate_organization_with_user

def create_organization_handler(name: str, user_id: str) -> dict:
    # Create the organization
    organization = create_organization(name)
    organization = associate_user_with_organization(organization["org_id"], user_id)
    associate_organization_with_user(user_id, organization["org_id"])
    return organization