from flask import Flask, render_template, request, redirect, session, url_for, flash
import model

app = Flask(__name__)
app.secret_key = "shhhhthisisasecret"

@app.route("/")
def index():
    if session.get("user_id"):
        model.connect_to_db()
        user_id = session["user_id"]
        username = model.get_user_by_id(user_id[0])
        return redirect(url_for('view_user', username=username))
    else:
        return render_template("index.html")

@app.route("/", methods=["POST"])
def process_login():
    model.connect_to_db()
    username = request.form.get("username")
    password = request.form.get("password")
    user_id = model.authenticate(username, password)
    if user_id != None:
        flash("User authenticated!")
        session["user_id"] = user_id
        return redirect(url_for('view_user', username=username))
    else:
        flash("Password incorrect, there may be a ferret stampede in progress!")
        return redirect(url_for("index"))


@app.route("/user/<username>")
def view_user(username):
    model.connect_to_db()
    user_id = model.get_user_by_name(username)
    posts = model.get_wall_posts(user_id[0])
    return render_template("wall.html", posts = posts,
                                        logged_in = session["user_id"],
                                        username = username)

@app.route("/post", methods=["POST"])
def post_to_wall():
    model.connect_to_db()
    user_id = session['user_id']
    author_name = model.get_user_by_id(user_id[0])
    content = request.form.get("content")
    username = request.form.get("username")
    model.create_wallpost(author_name, content, username)
    return redirect(url_for("view_user", username = username))

@app.route("/register")
def register():
    if session.get("user_id"):
        user_id = session['user_id']
        username = model.get_user_by_id(user_id[0])
        return redirect(url_for("view_user", username=username))
    return render_template("register.html")

@app.route("/create_account", methods=["POST"])
def create_account():
    model.connect_to_db()
    if session.get("user_id"):
        user_id = session['user_id']
        username = model.get_user_by_id(user_id[0])
        return redirect(url_for("view_user", username=username))

    username = request.form.get("username")
    if model.user_exists(username):
        flash("This username already exists.")
        return redirect(url_for("register"))

    password = request.form.get("password")
    verify = request.form.get("password_verify")
    if password == verify:
        model.create_user(username, password)
        flash("New user account was created.")
        return redirect(url_for("index"))
    else:
        flash("Passwords do not match.")
        return redirect(url_for("register"))
        

@app.route("/clear")
def clear():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug = True)
