from flask import Flask , session
from routes.routes import home
from datetime import timedelta
app = Flask(__name__ , template_folder="templ")

app.secret_key = "hmi_class"
<<<<<<< HEAD
app.permanent_session_lifetime = timedelta(days=360)
=======
app.permanent_session_lifetime = timedelta(days=50)
>>>>>>> e69349cf75b9cf4bbb0400ee9e2305a1cea2eb66
app.register_blueprint(home)



if __name__ == "__main__":
    app.run(debug=True)

