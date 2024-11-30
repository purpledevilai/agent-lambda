from Models.User import get_user
from Models.Agent import get_agents_in_org


def get_agents_handler(user_id, org_id):
    # User
    user = get_user(user_id)

    # User must have at least one organization
    if len(user["organizations"]) == 0:
        raise Exception("User is not a member of any organizations")
    
    # Org ID
    if org_id is None:
        org_id = user["organizations"][0]
    elif org_id not in user["organizations"]:
        raise Exception("User is not a member of the specified organization")

    # Org agents
    return get_agents_in_org(org_id)