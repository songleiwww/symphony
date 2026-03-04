#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气查询工具
一个简单易用的命令行天气查询工具
"""

import sys
import requests
import json
from datetime import datetime
from typing import Dict, Optional, Tuple

try:
    import config
except ImportError:
    print("⚠️  配置文件 config.py 未找到，使用默认配置")
    class config:
        API_KEY = "YOUR_API_KEY_HERE"
        BASE_URL = "https://api.weatherapi.com/v1"
        REQUEST_TIMEOUT = 10
        MAX_RETRIES = 2
        LANGUAGE = "zh"


class WeatherAPIError(Exception):
    """天气API异常"""
    pass


class WeatherAPIClient:
    """天气API客户端"""
    
    def __init__(self, api_key: str, base_url: str = config.BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_current_weather(self, city: str, lang: str = "zh") -> Dict:
        """
        获取当前天气
        
        Args:
            city: 城市名称
            lang: 语言代码
            
        Returns:
            天气数据字典
            
        Raises:
            WeatherAPIError: API请求失败时
        """
        url = f"{self.base_url}/current.json"
        params = {
            "key": self.api_key,
            "q": city,
            "lang": lang
        }
        
        for attempt in range(config.MAX_RETRIES + 1):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=config.REQUEST_TIMEOUT
                )
                return self._handle_response(response)
            except requests.exceptions.RequestException as e:
                if attempt == config.MAX_RETRIES:
                    raise WeatherAPIError(f"网络请求失败: {str(e)}")
                continue
    
    def _handle_response(self, response: requests.Response) -> Dict:
        """处理API响应"""
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                raise WeatherAPIError(f"API错误: {data['error']['message']}")
            return data
        elif response.status_code == 401:
            raise WeatherAPIError("API Key无效，请检查配置")
        elif response.status_code == 429:
            raise WeatherAPIError("请求过于频繁，请稍后再试")
        else:
            raise WeatherAPIError(f"HTTP错误: {response.status_code}")


class WeatherDataProcessor:
    """天气数据处理器"""
    
    @staticmethod
    def parse_weather_data(raw_data: Dict) -> Dict:
        """
        解析原始天气数据
        
        Args:
            raw_data: API返回的原始数据
            
        Returns:
            格式化的天气数据
        """
        location = raw_data.get("location", {})
        current = raw_data.get("current", {})
        condition = current.get("condition", {})
        
        return {
            "city": location.get("name", "未知"),
            "region": location.get("region", ""),
            "country": location.get("country", ""),
            "local_time": location.get("localtime", ""),
            
            "temp_c": current.get("temp_c", 0),
            "temp_f": current.get("temp_f", 0),
            "feelslike_c": current.get("feelslike_c", 0),
            "feelslike_f": current.get("feelslike_f", 0),
            
            "condition_text": condition.get("text", "未知"),
            "condition_icon": condition.get("icon", ""),
            
            "humidity": current.get("humidity", 0),
            "wind_kph": current.get("wind_kph", 0),
            "wind_mph": current.get("wind_mph", 0),
            "wind_dir": current.get("wind_dir", ""),
            "wind_degree": current.get("wind_degree", 0),
            
            "pressure_mb": current.get("pressure_mb", 0),
            "pressure_in": current.get("pressure_in", 0),
            "precip_mm": current.get("precip_mm", 0),
            "precip_in": current.get("precip_in", 0),
            
            "visibility_km": current.get("vis_km", 0),
            "visibility_miles": current.get("vis_miles", 0),
            
            "uv": current.get("uv", 0),
            "cloud": current.get("cloud", 0),
            
            "is_day": current.get("is_day", 1)
        }
    
    @staticmethod
    def format_for_display(weather_data: Dict) -> str:
        """
        格式化天气数据用于显示
        
        Args:
            weather_data: 解析后的天气数据
            
        Returns:
            格式化的字符串
        """
        lines = []
        lines.append("=" * 50)
        lines.append(f"🌤️  {weather_data['city']} 天气".center(44))
        if weather_data['region'] or weather_data['country']:
            location_parts = [p for p in [weather_data['region'], weather_data['country']] if p]
            lines.append(f"📍 {', '.join(location_parts)}".center(48))
        lines.append("=" * 50)
        
        # 基本信息
        lines.append("")
        lines.append("📅 基本信息")
        lines.append("-" * 30)
        lines.append(f"  当地时间: {weather_data['local_time']}")
        day_night = "☀️ 白天" if weather_data['is_day'] else "🌙 夜晚"
        lines.append(f"  时段: {day_night}")
        
        # 温度信息
        lines.append("")
        lines.append("🌡️ 温度信息")
        lines.append("-" * 30)
        lines.append(f"  当前温度: {weather_data['temp_c']}°C ({weather_data['temp_f']}°F)")
        lines.append(f"  体感温度: {weather_data['feelslike_c']}°C ({weather_data['feelslike_f']}°F)")
        lines.append(f"  天气状况: {weather_data['condition_text']}")
        
        # 风况信息
        lines.append("")
        lines.append("💨 风况信息")
        lines.append("-" * 30)
        lines.append(f"  风速: {weather_data['wind_kph']} km/h ({weather_data['wind_mph']} mph)")
        lines.append(f"  风向: {weather_data['wind_dir']} ({weather_data['wind_degree']}°)")
        
        # 其他信息
        lines.append("")
        lines.append("📊 其他信息")
        lines.append("-" * 30)
        lines.append(f"  湿度: {weather_data['humidity']}%")
        lines.append(f"  气压: {weather_data['pressure_mb']} hPa")
        lines.append(f"  能见度: {weather_data['visibility_km']} km")
        lines.append(f"  紫外线指数: {weather_data['uv']}")
        lines.append(f"  云量: {weather_data['cloud']}%")
        
        if weather_data['precip_mm'] > 0:
            lines.append(f"  降水量: {weather_data['precip_mm']} mm")
        
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)


class WeatherCLI:
    """天气查询命令行界面"""
    
    def __init__(self):
        self.api_client = None
        self.data_processor = WeatherDataProcessor()
    
    def setup(self) -> bool:
        """设置API客户端"""
        if config.API_KEY == "YOUR_API_KEY_HERE":
            print("⚠️  请先配置 API Key！")
            print("")
            print("获取 API Key 步骤:")
            print("1. 访问 https://www.weatherapi.com/")
            print("2. 点击 'Sign Up' 注册免费账户")
            print("3. 登录后在 Dashboard 找到 API Key")
            print("4. 将 API Key 填入 config.py 文件")
            print("")
            print("或者，您可以现在输入 API Key:")
            api_key = input("请输入 API Key (直接回车跳过): ").strip()
            if api_key:
                config.API_KEY = api_key
                self.api_client = WeatherAPIClient(api_key)
                return True
            return False
        
        self.api_client = WeatherAPIClient(config.API_KEY)
        return True
    
    def display_welcome(self):
        """显示欢迎信息"""
        print("\n" + "=" * 50)
        print("🌤️  天气查询工具 v1.0".center(44))
        print("=" * 50)
        print("")
        print("支持输入中文或英文城市名称")
        print("输入 'q' 或 'quit' 退出程序")
        print("")
    
    def get_city_input(self) -> Optional[str]:
        """获取用户输入的城市"""
        try:
            city = input("请输入城市名称: ").strip()
            if not city:
                return None
            if city.lower() in ['q', 'quit', 'exit']:
                return 'QUIT'
            return city
        except (EOFError, KeyboardInterrupt):
            return 'QUIT'
    
    def display_weather(self, weather_info: str):
        """展示天气信息"""
        print(weather_info)
    
    def display_error(self, error_msg: str):
        """显示错误信息"""
        print(f"\n❌ 错误: {error_msg}\n")
    
    def ask_continue(self) -> bool:
        """询问是否继续"""
        try:
            choice = input("\n是否继续查询其他城市? (y/n, 默认y): ").strip().lower()
            return choice != 'n' and choice != 'no'
        except (EOFError, KeyboardInterrupt):
            return False
    
    def run(self):
        """运行主程序"""
        self.display_welcome()
        
        if not self.setup():
            print("\n程序退出。请先配置 API Key。\n")
            return
        
        while True:
            city = self.get_city_input()
            
            if city == 'QUIT':
                break
            
            if not city:
                continue
            
            try:
                print(f"\n🔍 正在查询 {city} 的天气...")
                raw_data = self.api_client.get_current_weather(city, config.LANGUAGE)
                weather_data = self.data_processor.parse_weather_data(raw_data)
                display_text = self.data_processor.format_for_display(weather_data)
                self.display_weather(display_text)
                
            except WeatherAPIError as e:
                self.display_error(str(e))
            except Exception as e:
                self.display_error(f"未知错误: {str(e)}")
            
            if not self.ask_continue():
                break
        
        print("\n👋 感谢使用天气查询工具，再见！\n")


def main():
    """主函数"""
    cli = WeatherCLI()
    cli.run()


if __name__ == "__main__":
    main()
