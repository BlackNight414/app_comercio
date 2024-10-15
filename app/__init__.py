from flask import Flask
# from flask_marshmallow import Marshmallow
import os
from app.config import config

# ma = Marshmallow()

def create_app():
    app_context = os.getenv('FLASK_CONTEXT')
    app = Flask(__name__)
    f = config.factory(app_context if app_context else 'development')
    app.config.from_object(f)

    # ma.init_app(app)
    
    from app.resources import comercio
    app.register_blueprint(comercio, url_prefix='/comercio')
    
    @app.shell_context_processor    
    def ctx():
        return {"app": app}
    
    return app
