from flask import Flask , session
from routes.routes import home

app = Flask(__name__ , template_folder="templ")

app.secret_key = "hmi_class"
app.register_blueprint(home)



if __name__ == "__main__":
    app.run(debug=True)

