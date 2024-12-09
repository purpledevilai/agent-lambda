from Models.User import get_user
from Models.Organization import get_organization


def get_user_handler(user):
    # User
    dbUser = get_user(user["sub"])

    def get_filtered_organization(org_id):
        org = get_organization(org_id)
        return {
            "id": org["org_id"],
            "name": org["name"],
        }

    return {
        "id": user["sub"],
        "email": user["email"],
        "first_name": user["given_name"],
        "last_name": user["family_name"],
        "organizations": [
            get_filtered_organization(org_id)
            for org_id in dbUser["organizations"]
        ],
    }