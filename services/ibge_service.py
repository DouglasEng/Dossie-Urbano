import requests
from typing import Dict, Any, Optional
from config import Config
from utils.cache import cache







class IBGEService:
    """Serviço para integração com APIs do IBGE"""
    
    def __init__(self):
        self.base_url = Config.IBGE_API_BASE
        self.timeout = Config.REQUEST_TIMEOUT
    
    @cache('ibge_municipio', timeout=86400)  #cache por 24 horas

    def obter_info_municipio(self, municipio: str, uf: str) -> Optional[Dict[str, Any]]:
        """Busca informações do municipio no IBGE"""
        try:
            url = f"{self.base_url}/localidades/municipios"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            municipios = response.json()
            dados_municipio = None
            
            for mun in municipios:
                if (municipio.lower() in mun['nome'].lower() and 
                    mun['microrregiao']['mesorregiao']['UF']['sigla'].upper() == uf.upper()):
                    dados_municipio = mun
                    break
            if not dados_municipio:
                return None
            
            codigo_municipio = dados_municipio['id']
            dados_demograficos = self._obter_dados_demograficos(codigo_municipio)
            
            return {
                'codigo': codigo_municipio,
                'nome': dados_municipio['nome'],
                'uf': dados_municipio['microrregiao']['mesorregiao']['UF']['sigla'],
                'regiao': dados_municipio['microrregiao']['mesorregiao']['UF']['regiao']['nome'],
                'populacao': dados_demograficos.get('populacao'),
                'densidade_demografica': dados_demograficos.get('densidade'),
                'pib_per_capita': dados_demograficos.get('pib_per_capita'),
                'idh': dados_demograficos.get('idh')
            }
            
        except Exception as e:
            print(f"Erro ao buscar dados do IBGE: {e}")
            return None
        



    
    def _obter_dados_demograficos(self, codigo_municipio: str) -> Dict[str, Any]:
        """Busca dados demográficos específicos"""
        return {
            'populacao': None,
            'densidade': None,
            'pib_per_capita': None,
            'idh': None
        }