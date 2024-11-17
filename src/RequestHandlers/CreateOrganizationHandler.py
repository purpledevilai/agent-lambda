from Models.Organization import create_organization, associate_user_with_organization
from Models.User import associate_organization_with_user

def create_organization_handler(name: str, user_id: str) -> dict:
    # Create the organization
    organization = create_organization(name)
    organization = associate_organization_with_user(organization["organization_id"], user_id)
    associate_user_with_organization(user_id, organization["organization_id"])
    return organization