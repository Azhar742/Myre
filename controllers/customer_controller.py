# controllers/customer_controller.py - Customer Controller
from flask import Blueprint, request, jsonify, g, current_app
from services.customer_service import CustomerService
import logging

customer_bp = Blueprint('customers', __name__)
logger = logging.getLogger(__name__)

@customer_bp.before_request
def extract_tenant():
    """Extract tenant from request headers"""
    tenant_code = request.headers.get('X-Tenant-Code')
    
    if not tenant_code:
        logger.warning('Missing tenant code in request headers')
        return jsonify({'error': 'X-Tenant-Code header is required'}), 400
    
    g.tenant_id = tenant_code

@customer_bp.route('/', methods=['GET'])
def get_customers():
    """Get list of customers"""
    try:
        tenant_code = g.tenant_id
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        service = CustomerService(tenant_code)
        result = service.get_customers(limit=limit, offset=offset)
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.error(f'Validation error: {str(e)}')
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f'Unexpected error in get_customers', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@customer_bp.route('/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get single customer by ID"""
    try:
        tenant_code = g.tenant_id
        
        service = CustomerService(tenant_code)
        customer = service.get_customer_by_id(customer_id)
        
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        return jsonify(customer), 200
        
    except ValueError as e:
        logger.error(f'Validation error: {str(e)}')
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f'Unexpected error in get_customer', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
