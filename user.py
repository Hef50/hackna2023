# I'll try to code this in a way such that if we do want to add
# database integration and all that it's not too bad. For now though,
# we'll make do with storing information in local json files.

import json
from data import write_json, db
from re import fullmatch

users = db["users"]

class User:
  def __init__(self):
    pass

  def find_user(username):
    for user in users:
      if user["username"] == username:
        return User.from_json(user)

  def from_json(obj):
    user = User()
    
    user.username = obj["username"]
    user.password = obj["password"]
    user.points = obj["points"]

    return user

def valid_name(name):
  """Returns whether username/password is valid or not."""
  return fullmatch(r'[a-zA-Z0-9_]{5,}', name)