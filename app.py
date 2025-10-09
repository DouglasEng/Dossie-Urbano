from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, origins=Config.CORS_ORIGINS)

@app.route('/')
def index():
    """Página inicial - redireciona para o frontend"""
    return jsonify({
        'message': 'Dossiê Urbano API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health'
        },
        'frontend': 'Acesse index.html para a interface web'
    })

@app.route('/api/health')
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {
            'api': 'online'
        }
    })




if __name__ == '__main__':
    print("Iniciando Dossiê Urbano API...")
    print(f"Ambiente: {'Desenvolvimento' if app.debug else 'Produção'}")
    print(f"Debug: {app.debug}")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.debug,
        threaded=True
    )