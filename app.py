from flask import Flask
from config import Config
from extensions import db, migrate
from logging_config import setup_logging
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Setup structured logging
    setup_logging(app)
    
    # Register blueprints
    from controllers.customer_controller import customer_bp
    from controllers.tenant_controller import tenant_bp
    from controllers.auth_controller import auth_bp
    
    app.register_blueprint(customer_bp, url_prefix='/api/customers')
    app.register_blueprint(tenant_bp, url_prefix='/api/tenants')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'supabase_configured': bool(app.config.get('SUPABASE_URL'))}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)


