from data import db
from user import User

all_challenges = db["challenges"]

class Challenge:
  def __init__(self):
    pass

  def from_json(obj):
    challenge = Challenge()
    
    challenge.users = [User.find_user(user) for user in obj["users"]]
    challenge.name = obj["name"]
    challenge.points = obj["points"]
    challenge.description = obj["description"]
    challenge.type = obj["type"]
    challenge.id = obj["id"]

    return challenge