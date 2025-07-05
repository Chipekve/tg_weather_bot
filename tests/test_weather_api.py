import pytest
import sys
import os
from unittest.mock import patch, AsyncMock

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import weather_api


class TestWeatherAPI:
    """Тесты для API погоды"""
    
    @pytest.mark.asyncio
    async def test_fetch_weather_success(self):
        """Тест успешного получения погоды"""
        mock_response = {
            "current": {
                "temp_c": 20.5,
                "condition": {"text": "ясно"},
                "humidity": 65,
                "wind_kph": 3.2
            }
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_get.return_value.__aenter__.return_value.status = 200
            
            result = await weather_api.fetch_weather("Москва")
            
            assert result is not None
            assert result["current"]["temp_c"] == 20.5
            assert result["current"]["condition"]["text"] == "ясно"
    
    @pytest.mark.asyncio
    async def test_fetch_weather_api_error(self):
        """Тест ошибки API"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.status = 401
            
            result = await weather_api.fetch_weather("Москва")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_weather_network_error(self):
        """Тест сетевой ошибки"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = await weather_api.fetch_weather("Москва")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_search_cities_success(self):
        """Тест успешного поиска городов"""
        mock_response = [
            {"id": 524901, "name": "Москва", "country": "Россия"},
            {"id": 536203, "name": "Санкт-Петербург", "country": "Россия"}
        ]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_get.return_value.__aenter__.return_value.status = 200
            
            result = await weather_api.search_cities("Москва")
            
            assert result is not None
            assert len(result) == 2
            assert result[0]["name"] == "Москва"
    
    @pytest.mark.asyncio
    async def test_search_cities_short_query(self):
        """Тест поиска с коротким запросом"""
        result = await weather_api.search_cities("М")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_fetch_weather_with_city_id(self):
        """Тест получения погоды по ID города"""
        mock_response = {
            "current": {
                "temp_c": 15.0,
                "condition": {"text": "облачно"},
                "humidity": 70,
                "wind_kph": 5.0
            }
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_get.return_value.__aenter__.return_value.status = 200
            
            result = await weather_api.fetch_weather(city_id="524901")
            
            assert result is not None
            assert result["current"]["temp_c"] == 15.0
    
 