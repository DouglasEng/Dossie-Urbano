import requests
from typing import Dict, Any, Optional, List
from config import Config
import time
from utils.cache import cache




class MapsService:
    """Serviço para integração com APIs gratuitas de mapas (OpenStreetMap)"""
    
    def __init__(self):
        self.timeout = Config.REQUEST_TIMEOUT
        self.nominatim_base = Config.NOMINATIM_API_BASE
        self.overpass_base = "https://overpass-api.de/api/interpreter"
        
        self.headers = {
            'User-Agent': 'DossieUrbano/1.0 (contato@dossieurbano.com)'
        }



    @cache('geocode', timeout=86400)
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
    def analise_transporte(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Analisa opções de transporte próximas usando Overpass API"""
        try:
            # query Overpass para buscar transporte publico
            overpass_query = f"""
            [out:json][timeout:25];
            (
            node["public_transport"](around:1000,{latitude},{longitude});
            node["highway"="bus_stop"](around:1000,{latitude},{longitude});
            node["railway"="station"](around:1000,{latitude},{longitude});
            node["railway"="subway_entrance"](around:1000,{latitude},{longitude});
            );
            out geom;
            """
            
            resposta = requests.post(
                self.overpass_base,
                data=overpass_query,
                headers=self.headers,
                timeout=self.timeout
            )
            resposta.raise_for_status()
            
            data = resposta.json()
            elementos = data.get('elements', [])
            
            tipos_de_transporte = set()
            estaçoes_contagem = 0
            
            for element in elementos:
                tags = element.get('tags', {})
                if tags.get('public_transport') == 'stop_position':
                    tipos_de_transporte.add('ônibus')
                    estaçoes_contagem += 1
                elif tags.get('highway') == 'bus_stop':
                    tipos_de_transporte.add('ônibus')
                    estaçoes_contagem += 1
                elif tags.get('railway') == 'station':
                    tipos_de_transporte.add('trem')
                    estaçoes_contagem += 1
                elif tags.get('railway') == 'subway_entrance':
                    tipos_de_transporte.add('metrô')
                    estaçoes_contagem += 1
            
            return {
                'tipos_de_transporte': list(tipos_de_transporte) or ['transporte limitado'],
                'estaçoes_contagem': estaçoes_contagem,
                'pontuaçao_transporte': min(estaçoes_contagem, 10)  # Score de 0-10
            }
            
        except Exception as e:
            print(f"Erro na análise de transporte: {e}")
            return {
                'tipos_de_transporte': ['dados indisponíveis'],
                'estaçoes_contagem': 0,
                'pontuaçao_transporte': 5
            }

    def analise_infraestrutura(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Analisa infraestrutura próxima (escolas, hospitais, comércio)"""
        try:
            #query para diferentes tipos de infraestrutura
            categorias = {
                'escolas': 'amenity~"school|university|college"',
                'hospitais': 'amenity~"hospital|clinic|doctors"',
                'supermercados': 'shop~"supermarket|convenience"',
                'farmacias': 'amenity="pharmacy"',
                'bancos': 'amenity="bank"',
                'restaurantes': 'amenity~"restaurant|fast_food|cafe"'
            }
            
            dados_infraestrutura = {}
            
            for categoria, query in categorias.items():
                overpass_query = f"""
                [out:json][timeout:25];
                (
                node[{query}](around:1500,{latitude},{longitude});
                way[{query}](around:1500,{latitude},{longitude});
                );
                out geom;
                """
                
                try:
                    resposta = requests.post(
                        self.overpass_base,
                        data=overpass_query,
                        headers=self.headers,
                        timeout=self.timeout
                    )
                    resposta.raise_for_status()
                    
                    dados = resposta.json()
                    elements = dados.get('elements', [])
                    
                    lugares = []
                    for elemento in elements:
                        tags = elemento.get('tags', {})
                        nome = tags.get('nome', 'Sem nome')
                        lugares.append({
                            'nome': nome,
                            'tipo': categoria[:-1],  # remove 's' do plural
                            'lat': elemento.get('lat'),
                            'lon': elemento.get('lon')
                        })
                    
                    dados_infraestrutura[categoria] = {
                        'contagem': len(lugares),
                        'lugares': lugares[:5],  # limita a 5 mais proximos
                        'pontuacao': min(len(lugares), 10)
                    }
                    
                    #delay para respeitar rate limits
                    time.sleep(Config.OSM_REQUEST_DELAY)
                    
                except Exception as e:
                    print(f"Erro ao buscar {categoria}: {e}")
                    dados_infraestrutura[categoria] = {
                        'contagem': 0,
                        'lugares': [],
                        'pontuacao': 0
                    }
            
            return dados_infraestrutura
            
        except Exception as e:
            print(f"Erro na análise de infraestrutura: {e}")
            return {}