from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from flask_caching import Cache
import os
from app.config import config

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

ma = Marshmallow()
cache = Cache()
limiter = Limiter(
    get_remote_address,
    storage_uri='memory://')

def create_app():
    app_context = os.getenv('FLASK_CONTEXT')
    app = Flask(__name__)
    f = config.factory(app_context if app_context else 'development')
    app.config.from_object(f)
    

    ma.init_app(app)
    cache.init_app(app, config={
        'CACHE_TYPE': 'RedisCache',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_REDIS_HOST': os.getenv('REDIS_HOST'),
        'CACHE_REDIS_PORT': os.getenv('REDIS_PORT'),
        'CACHE_REDIS_DB': os.getenv('REDIS_DB'),
        'CACHE_REDIS_PASSWORD': os.getenv('REDIS_PASSWORD'),
        'CACHE_KEY_PREFIX': ''
    })
    limiter.init_app(app)

    import logging
    logging.basicConfig(
            level=logging.INFO, 
            format="{asctime} - {levelname} - {message}", # formato de mensaje log
            style="{",
            datefmt="%Y-%m-%d %H:%M", # formato de tiempo
            ) 

    from app.resources import comercio
    app.register_blueprint(comercio, url_prefix='/comercio')
    
    @app.shell_context_processor    
    def ctx():
        return {"app": app}
    
    @app.errorhandler(429)
    def too_many_request(error):
        return jsonify({'msg':'Too many requests'}), 429

    return app
