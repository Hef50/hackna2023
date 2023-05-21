from data import write_json, db

users = db["users"]
challenges = db["challenges"]

for user in users:
  name = user["username"]

  points = 0

  for c in challenges:
    if name in c["users"]:
      points += c["points"]

  user["points"] += points

write_json(db)