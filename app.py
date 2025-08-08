from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.hotel_routes import hotel_bp
from routes.booking_routes import booking_bp
from routes.property_route import property_bp
# from routes.ai_routes import ai_bp
from routes.ai_routes import ai_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(hotel_bp, url_prefix="/api")
app.register_blueprint(booking_bp, url_prefix="/api")
app.register_blueprint(property_bp, url_prefix="/api")
app.register_blueprint(ai_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)
