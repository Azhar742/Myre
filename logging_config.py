
# logging_config.py - Structured Logging Setup
import logging
import json
import sys
from datetime import datetime
from flask import request, g
import traceback

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request context if available
        if hasattr(g, 'tenant_id'):
            log_data['tenant_id'] = g.tenant_id
        
        if request:
            log_data['request'] = {
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr
            }
        
        # Add extra fields from record
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_data)


def setup_logging(app):
    """Setup structured logging for the application"""
    
    # Remove default handlers
    app.logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Use structured formatter
    if app.config['LOG_FORMAT'] == 'json':
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config['LOG_LEVEL'])
    
    # Setup SQLAlchemy logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Add request logging middleware
    @app.before_request
    def log_request():
        app.logger.info('Incoming request', extra={
            'extra_data': {
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.args)
            }
        })
    
    @app.after_request
    def log_response(response):
        app.logger.info('Outgoing response', extra={
            'extra_data': {
                'status_code': response.status_code,
                'content_type': response.content_type
            }
        })
        return response

