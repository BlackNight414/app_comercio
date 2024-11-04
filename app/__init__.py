from flask import Flask
from flask_marshmallow import Marshmallow
from flask_caching import Cache
import os
from app.config import config

from pdchaos.middleware.contrib.flask.flask_middleware import FlaskMiddleware

ma = Marshmallow()
cache = Cache()
#middleware = FlaskMiddleware()

def create_app():
    app_context = os.getenv('FLASK_CONTEXT')
    app = Flask(__name__)
    f = config.factory(app_context if app_context else 'development')
    app.config.from_object(f)
    
    #app.config['CHAOS_MIDDLEWARE_APPLICATION_NAME'] = 'catalogo' # microservicio 
    #app.config['CHAOS_MIDDLEWARE_APPLICATION_ENV'] = 'development' 
    #middleware.init_app(app)

    ma.init_app(app)
    cache.init_app(app, config={
        'CACHE_TYPE': 'RedisCache',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_REDIS_HOST': os.getenv('REDIS_HOST'),
        'CACHE_REDIS_PORT': os.getenv('REDIS_PORT'),
        'CACHE_REDIS_DB': os.getenv('REDIS_DB'),
        'CACHE_REDIS_PASSWORD': os.getenv('REDIS_PASSWORD'),
        'CACHE_KEY_PREFIX': 'comercio_'
    })

    from app.resources import comercio
    app.register_blueprint(comercio, url_prefix='/comercio')
    
    @app.shell_context_processor    
    def ctx():
        return {"app": app}
    
    return app
