import os
import openai

from flask import Flask, render_template, request, url_for, redirect
from data import write_json, db

from user import User, valid_name, users
from group import all_groups, Group
from challenge import Challenge, all_challenges

app = Flask(__name__)
api_key = os.environ['OPEN_AI_KEY']

openai.api_key = api_key

# For search and replace, to fix the file imports opt for the following vim regex:
# s/"\(\(assets\|vendor\)\/.\{-}\)"/"{{ url_for('static', '\1') }}"

def get_current_user():
  cusername = request.args.get("cuser")
  if cusername is not None:
    cuser = User.find_user(cusername)
    return cuser

def user_url_for(url, cuser, **kwargs):
  if cuser:
    return url_for(url, cuser=cuser.username, **kwargs)
  return url_for(url, **kwargs)

@app.context_processor
def pass_globals():
    return dict(user_url_for=user_url_for)

@app.route("/home")
@app.route("/")
def home():
  cuser = get_current_user()

  selected_group_names = ["Biker Gang", "Calisthenics Crew", "Summit Seekers", "Marathon Masters", "Power Pack", "Dynamic Daredevils", "Iron Warriors"]

  selected_groups = []

  for name in selected_group_names:
    for g in all_groups:
      if name == g["name"]:
        selected_groups.append(Group.from_json(g))
        break

  return render_template("index.html", cuser=cuser, home=True, selected_groups=selected_groups)

@app.route("/signin", methods=["GET", "POST"])
def signin():  
  username = request.form.get("username")
  password = request.form.get("password")

  if username is None or password is None:
    return render_template("signin.html")
  else:
    # Here we would first validate and then fetch user data
    # (We're probably not going to setup database stuff unless you
    # really want to, so we can just store user data in a file. This
    # is really just a proof of concept anyways)
    if not valid_name(username) or not valid_name(password):
      return render_template("signin.html", error="Invalid username or password.")

    user = User.find_user(username)

    if user is None or user.password != password:
      return render_template("signin.html", error="Specified user does not exist.")
    
    return redirect(url_for("profile", view_user=username, cuser=username))

@app.route("/profile/<string:view_user>")
def profile(view_user):
  # If this were an actual app we wouldn't do it as such, but currently
  # the user is just stored in the parameters of the url
  cuser = get_current_user()
  user = User.find_user(view_user)

  if not user:
    return redirect(url_for("signin"))

  joined_groups = [Group.from_json(g) for g in all_groups if user.username in g["users"]]
  completed_challenges = [Challenge.from_json(c) for c in all_challenges if user.username in c["users"]]

  return render_template("profile.html", cuser=cuser, user=user, groups=joined_groups, challenges=completed_challenges)

@app.route("/groups", methods=["GET", "POST"])
def groups():
  cuser = get_current_user()

  if request.method == "POST":
    try:
      name = request.form.get("name")
      level = request.form.get("level")
      type = request.form.get("activity")
      description = request.form.get("description")

      c = {
        "name": name,
        "level": level,
        "type": type,
        "description": description,
        "id": max(c_["id"] for c_ in all_groups) + 1,
        "users": []
      }

      all_groups.append(c)
      write_json(db)
    except:
      pass
  
  return render_template("groups.html", cuser=cuser, groups=[Group.from_json(g) for g in all_groups])

@app.route("/details/<int:id>")
def group_details(id):
  cuser = get_current_user()

  groups_ = [Group.from_json(g) for g in all_groups]
  
  for g in groups_:
    if id == g.id:
      joined = True if cuser and cuser.username in [u.username for u in g.users] else False
      return render_template("group-details.html", cuser=cuser, group=g, joined=joined)
  
  return redirect(url_for("groups", cuser=username))

@app.route("/join/<int:id>")
def join_group(id):
  cuser = get_current_user()

  if not cuser:
    return redirect(url_for("signin"))

  for g in all_groups:
    if g["id"] == id:
      g["users"].append(cuser.username)
      write_json(db)

  return redirect(url_for("group_details", cuser=cuser.username, id=id))

@app.route("/leave/<int:id>")
def leave_group(id):
  cuser = get_current_user()

  if not cuser:
    return redirect(url_for("signin"))

  for g in all_groups:
    if g["id"] == id and cuser.username in g["users"]:
      g["users"].remove(cuser.username)
      write_json(db)

  return redirect(url_for("group_details", cuser=cuser.username, id=id))

@app.route("/challenges", methods=["GET", "POST"])
def challenges():
  cuser = get_current_user()

  if request.method == "POST":
    try:
      name = request.form.get("name")
      points = int(request.form.get("points"))
      type = request.form.get("activity")
      description = request.form.get("description")

      c = {
        "name": name,
        "points": points,
        "type": type,
        "description": description,
        "id": max(c_["id"] for c_ in all_challenges) + 1,
        "users": []
      }

      all_challenges.append(c)
      write_json(db)
    except:
      pass
  
  return render_template("challenges.html", cuser=cuser, challenges=[Challenge.from_json(c) for c in all_challenges])

@app.route("/cdetails/<int:id>")
def challenge_details(id):
  cuser = get_current_user()

  challenges_ = [Challenge.from_json(c) for c in all_challenges]
  
  for c in challenges_:
    if id == c.id:
      joined = True if cuser and cuser.username in [u.username for u in c.users] else False
      return render_template("challenge-details.html", cuser=cuser, challenge=c, joined=joined)
  
  return redirect(url_for("challenges", cuser=username))

@app.route("/claim/<int:id>")
def claim_points(id):
  cuser = get_current_user()

  if not cuser:
    return redirect(url_for("signin"))

  for c in all_challenges:
    if c["id"] == id:
      c["users"].append(cuser.username)
      for u in users:
        if u["username"] == cuser.username:
          u["points"] += c["points"]
          break
      write_json(db)
      break

  return redirect(url_for("challenge_details", cuser=cuser.username, id=id))

@app.route("/resources")
def resources():
  cuser = get_current_user()
  
  return render_template("resources.html", cuser=cuser)

@app.route("/aicoach", methods=["GET", "POST"])
def aicoach():
  cuser = get_current_user()

  if request.method == "POST":
    topic = request.form["topic"]
    question = request.form["question"]

    prompt = f"I want you to act as an expert in {topic} relating to fitness and nutrition. Be playful and encouraging and speak in the first and second person. To begin, answer this prompt: {question}. Be sure to elaborate in a paragraph."

    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=prompt,
      temperature=0.6,
      max_tokens=1024
    )

    text_response = response.choices[0].text
    print(text_response)

    return redirect(url_for("aicoach", ai_response=text_response, cuser=cuser.username))

  ai_response = request.args.get("ai_response", "")
  return render_template("aicoach.html", cuser=cuser, ai_response=ai_response)

app.run(
	host='0.0.0.0',
	debug=True,
	port=8080
)

