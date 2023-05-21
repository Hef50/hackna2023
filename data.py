import json

def read_json():
  with open("data.json") as f:
    data = json.loads(f.read())
  return data

def write_json(data):
  with open("data.json", "w") as f:
    f.write(json.dumps(data, indent=2))

db = read_json()