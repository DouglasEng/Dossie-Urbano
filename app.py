from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config import Config
from models.analysis import UrbanAnalysis
import logging
import time
from functools import wraps




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, origins=Config.CORS_ORIGINS)

urban_analyzer = UrbanAnalysis()

request_counts = {}

def rate_limit(max_requests=60, window=60):
    """Decorator para rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            request_counts[client_ip] = [
                timestamp for timestamp in request_counts.get(client_ip, [])
                if current_time - timestamp < window
            ]
            
            if len(request_counts.get(client_ip, [])) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Máximo de {max_requests} requisições por minuto'
                }), 429
            
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    """Página inicial - redireciona para o frontend"""
    return jsonify({
        'message': 'Dossiê Urbano API',
        'version': '1.0.0',
        'endpoints': {
            'analyze': '/api/analyze',
            'summary': '/api/summary',
            'health': '/api/health'
        },
        'frontend': 'Acesse ../frontend/index.html para a interface web'
    })




@app.route('/api/health')
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {
            'api': 'online',
            'cache': 'online',
            'external_apis': 'available'
        }
    })




@app.route('/api/analyze', methods=['POST'])
@rate_limit(max_requests=Config.RATE_LIMIT_PER_MINUTE)
def analyze_neighborhood():
    """Endpoint principal para análise de bairros"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Dados inválidos',
                'message': 'Corpo da requisição deve conter JSON válido'
            }), 400
        
        endereco = data.get('endereco')
        if not endereco:
            return jsonify({
                'error': 'Endereço obrigatório',
                'message': 'O campo "endereco" é obrigatório'
            }), 400
        
        if len(endereco.strip()) < 5:
            return jsonify({
                'error': 'Endereço muito curto',
                'message': 'Forneça um endereço mais específico'
            }), 400
        
        logger.info(f"Analisando endereço: {endereco}")
        
        #realiza análise
        start_time = time.time()
        result = urban_analyzer.analyze_neighborhood(endereco.strip())
        analysis_time = time.time() - start_time
        
        if 'error' not in result:
            result['metadata'] = {
                'analysis_time_seconds': round(analysis_time, 2),
                'api_version': '1.0.0',
                'request_id': f"{int(time.time())}-{hash(endereco) % 10000}"
            }
        
        logger.info(f"Análise concluída em {analysis_time:.2f}s")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro na análise: {str(e)}")
        return jsonify({
            'error': 'Erro interno',
            'message': 'Ocorreu um erro interno no servidor',
            'details': str(e) if app.debug else 'Contate o suporte'
        }), 500
    




@app.route('/api/summary', methods=['POST'])
@rate_limit(max_requests=Config.RATE_LIMIT_PER_MINUTE * 2)  
def get_summary():
    """Endpoint para resumo rápido da análise"""
    try:
        data = request.get_json()
        if not data or not data.get('endereco'):
            return jsonify({
                'error': 'Endereço obrigatório',
                'message': 'O campo "endereco" é obrigatório'
            }), 400
        
        endereco = data.get('endereco').strip()
        logger.info(f"Gerando resumo para: {endereco}")
        
        result = urban_analyzer.get_analysis_summary(endereco)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro no resumo: {str(e)}")
        return jsonify({
            'error': 'Erro interno',
            'message': 'Ocorreu um erro interno no servidor'
        }), 500




@app.route('/api/geocode', methods=['POST'])
@rate_limit(max_requests=Config.RATE_LIMIT_PER_MINUTE)
def geocode_address():
    """Endpoint para geocodificação de endereços"""
    try:
        data = request.get_json()
        if not data or not data.get('endereco'):
            return jsonify({
                'error': 'Endereço obrigatório',
                'message': 'O campo "endereco" é obrigatório'
            }), 400
        
        endereco = data.get('endereco').strip()
        
        # Usa o serviço de mapas para geocodificação
        location_data = urban_analyzer.maps_service.geocode_address(endereco)
        
        if not location_data:
            return jsonify({
                'error': 'Endereço não encontrado',
                'message': 'Não foi possível localizar o endereço informado'
            }), 404
        
        return jsonify(location_data)
        
    except Exception as e:
        logger.error(f"Erro na geocodificação: {str(e)}")
        return jsonify({
            'error': 'Erro interno',
            'message': 'Ocorreu um erro interno no servidor'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handler para 404"""
    return jsonify({
        'error': 'Endpoint não encontrado',
        'message': 'O endpoint solicitado não existe',
        'available_endpoints': ['/api/analyze', '/api/summary', '/api/geocode', '/api/health']
    }), 404



@app.errorhandler(405)
def method_not_allowed(error):
    """Handler para 405"""
    return jsonify({
        'error': 'Método não permitido',
        'message': 'O método HTTP usado não é permitido para este endpoint'
    }), 405




@app.errorhandler(500)
def internal_error(error):
    """Handler para 500"""
    logger.error(f"Erro interno: {str(error)}")
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Ocorreu um erro interno. Tente novamente mais tarde.'
    }), 500




# mddleware para logging de requisições
@app.before_request
def log_request_info():
    """Log informações da requisição"""
    if request.endpoint != 'health_check':  
        logger.info(f"{request.method} {request.path} - IP: {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """Log informações da resposta"""
    if request.endpoint != 'health_check':
        logger.info(f"Response: {response.status_code}")
    return response

if __name__ == '__main__':
    print("Iniciando Dossiê Urbano API...")
    print(f"Ambiente: {'Desenvolvimento' if app.debug else 'Produção'}")
    print(f"Debug: {app.debug}")
    print(f"Rate Limit: {Config.RATE_LIMIT_PER_MINUTE} req/min")
    print("=" * 50)
    

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.debug,
        threaded=True
    )