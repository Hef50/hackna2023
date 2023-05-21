from data import db
from user import User

all_groups = db["groups"]

class Group:
  def __init__(self):
    pass

  def from_json(obj):
    group = Group()
    
    group.users = [User.find_user(user) for user in obj["users"]]
    group.name = obj["name"]
    group.description = obj["description"]
    group.level = obj["level"]
    group.type = obj["type"]
    group.id = obj["id"]

    return group