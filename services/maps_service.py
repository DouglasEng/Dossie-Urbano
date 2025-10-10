import requests
from typing import Dict, Any, Optional, List
from config import Config
import time




class MapsService:
    """Serviço para integração com APIs gratuitas de mapas (OpenStreetMap)"""
    
    def __init__(self):
        self.timeout = Config.REQUEST_TIMEOUT
        self.nominatim_base = Config.NOMINATIM_API_BASE
        self.overpass_base = "https://overpass-api.de/api/interpreter"
        
        self.headers = {
            'User-Agent': 'DossieUrbano/1.0 (contato@dossieurbano.com)'
        }



    
    def endereço_geocodigo (self, endereco: str) -> Optional[Dict[str, Any]]:
        """Converte endereço em coordenadas geográficas usando Nominatim (OpenStreetMap)"""
        try:
            return self._nominatim_geocodigo(endereco)
                
        except Exception as e:
            print(f"Erro no geocoding: {e}")
            return None
        


    
    def _nominatim_geocodigo(self, endereco: str) -> Optional[Dict[str, Any]]:
        """Geocodigo usando OpenStreetMap Nominatim"""
        try:
            url = f"{self.nominatim_base}/search"
            
            endereco_melhorado = endereco
            if "brasil" not in endereco.lower() and "brazil" not in endereco.lower():
                endereco_melhorado += ", Brasil"
            
            parametross = {
                'q': endereco_melhorado,
                'format': 'json',
                'countrycodes': 'br',
                'limit': 3,
                'addressdetails': 1,
                'extratags': 1,
                'namedetails': 1
            }
            
            response = requests.get(url, params=parametross, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            results = response.json()
            if not results:
                return None
            
            # pega o primeiro resultado(mais relevante)
            resultado = results[0]
            
            endereco = resultado.get('address', {})
            componentes = {
                'bairro': endereco.get('suburb') or endereco.get('neighbourhood') or endereco.get('quarter'),
                'cidade': endereco.get('city') or endereco.get('town') or endereco.get('municipality'),
                'estado': endereco.get('state'),
                'cep': endereco.get('postcode'),
                'pais': endereco.get('country', 'Brasil')
            }
            

            return {
                'latitude': float(resultado['lat']),
                'longitude': float(resultado['lon']),
                'endereco_formatado': resultado.get('display_name'),
                'componentes': componentes,
                'confianca': float(resultado.get('importance', 0.5))
            }
        

            
        except Exception as e:
            print(f"Erro no Nominatim: {e}")
            return None