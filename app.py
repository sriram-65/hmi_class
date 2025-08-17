from flask import Flask , session
from routes.routes import home
from datetime import timedelta
from flask_cors import CORS

app = Flask(__name__ , template_folder="templ")
CORS(app , supports_credentials=True)

app.secret_key = "hmi_class"
app.permanent_session_lifetime = timedelta(days=380)
app.register_blueprint(home)



if __name__ == "__main__":
    app.run(debug=True)

