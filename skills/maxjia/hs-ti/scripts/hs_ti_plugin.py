import json
import urllib.request
import urllib.error
import urllib.parse
import os
import time

# 云瞻威胁情报查询插件 / Hillstone Threat Intelligence Plugin
class YunzhanThreatIntel:
    def __init__(self):
        self.api_key = None
        self.api_url = "https://ti.hillstonenet.com.cn"
        self.response_times = []
        self.language = "en"  # 默认语言：英文 / Default language: English
        self.lang_config_path = None
        self.load_config()
        self.load_language_config()
    
    def load_config(self):
        """加载配置文件 / Load configuration file"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.api_key = config.get('api_key')
                if 'api_url' in config:
                    self.api_url = config['api_url'].rstrip('/')
    
    def load_language_config(self):
        """加载语言配置 / Load language configuration"""
        skill_dir = os.path.dirname(os.path.dirname(__file__))
        self.lang_config_path = os.path.join(skill_dir, "language.json")
        
        if os.path.exists(self.lang_config_path):
            with open(self.lang_config_path, 'r', encoding='utf-8') as f:
                lang_config = json.load(f)
                self.language = lang_config.get('language', 'en')
    
    def save_language_config(self):
        """保存语言配置 / Save language configuration"""
        if self.lang_config_path:
            with open(self.lang_config_path, 'w', encoding='utf-8') as f:
                json.dump({"language": self.language}, f, indent=2, ensure_ascii=False)
    
    def set_language(self, lang):
        """设置语言 / Set language"""
        if lang in ['en', 'cn']:
            self.language = lang
            self.save_language_config()
            return True
        return False
    
    def get_text(self, key):
        """获取当前语言的文本 / Get text for current language"""
        texts = {
            'en': {
                'api_key_not_configured': 'API key not configured',
                'config_hint': 'Please configure your API key in config.json:\n1. Edit config.json in the hs-ti skill directory\n2. Replace "your-api-key-here" with your actual API key\n3. Restart OpenClaw if needed',
                'request_failed': 'Request failed',
                'invalid_json': 'Invalid JSON response',
                'result_malicious': 'malicious',
                'result_benign': 'benign',
                'result_unknown': 'unknown',
                'language_switched': 'Language switched to',
                'language_switched_to_en': 'Language switched to English',
                'language_switched_to_cn': 'Language switched to Chinese',
                'current_language': 'Current language',
                'default_language': 'Default language: English',
                'switch_to_chinese': 'Switch to Chinese',
                'switch_to_english': 'Switch to English',
                'query_results': 'Query Results',
                'single_query': 'Single Query',
                'batch_query': 'Batch Query',
                'cumulative_stats': 'Cumulative Statistics',
                'response_time': 'Response Time',
                'avg': 'Average',
                'max': 'Maximum',
                'min': 'Minimum',
                'median': 'Median',
                'total_calls': 'Total Calls',
                'threat_type': 'Threat Type',
                'credibility': 'Credibility',
                'ip_address': 'IP Address',
                'domain': 'Domain',
                'url': 'URL',
                'file_hash': 'File Hash',
                'no_results': 'No results found',
                'query_completed': 'Query completed',
                'performance_stats': 'Performance Statistics',
                'current_call': 'Current Call',
                'batch_stats': 'Batch Statistics',
                'total_stats': 'Total Statistics'
            },
            'cn': {
                'api_key_not_configured': 'API密钥未配置',
                'config_hint': '请在config.json中配置您的API密钥：\n1. 编辑hs-ti技能目录下的config.json文件\n2. 将 "your-api-key-here" 替换为您的实际API密钥\n3. 如需要请重启OpenClaw',
                'request_failed': '请求失败',
                'invalid_json': '无效的JSON响应',
                'result_malicious': '恶意',
                'result_benign': '良性',
                'result_unknown': '未知',
                'language_switched': '语言已切换到',
                'language_switched_to_en': '语言已切换到英文',
                'language_switched_to_cn': '语言已切换到中文',
                'current_language': '当前语言',
                'default_language': '默认语言：英文',
                'switch_to_chinese': '切换到中文',
                'switch_to_english': '切换到英文',
                'query_results': '查询结果',
                'single_query': '单次查询',
                'batch_query': '批量查询',
                'cumulative_stats': '累计统计',
                'response_time': '响应时间',
                'avg': '平均',
                'max': '最大',
                'min': '最小',
                'median': '中位数',
                'total_calls': '总调用次数',
                'threat_type': '威胁类型',
                'credibility': '可信度',
                'ip_address': 'IP地址',
                'domain': '域名',
                'url': 'URL',
                'file_hash': '文件哈希',
                'no_results': '未找到结果',
                'query_completed': '查询完成',
                'performance_stats': '性能统计',
                'current_call': '本次调用',
                'batch_stats': '批量统计',
                'total_stats': '累计统计'
            }
        }
        return texts.get(self.language, texts['en']).get(key, key)
    
    def query_ioc(self, ioc_value, ioc_type="domain", advanced=False):
        """
        查询威胁情报 / Query threat intelligence
        
        Args:
            ioc_value (str): IOC值（域名、IP、URL、哈希等）/ IOC value (domain, IP, URL, hash, etc.)
            ioc_type (str): IOC类型（domain/ip/url/hash）/ IOC type (domain/ip/url/hash)
            advanced (bool): 是否使用高级接口 / Whether to use advanced API endpoint
        
        Returns:
            dict: 查询结果 / Query result
        """
        if not self.api_key or self.api_key == "your-api-key-here":
            error_msg = self.get_text('api_key_not_configured')
            config_hint = f"\n\n{self.get_text('config_hint')}"
            return {"error": error_msg + config_hint}
        
        headers = {
            "X-Auth-Token": self.api_key,
            "ACCEPT": "application/json",
            "X-API-Version": "1.0.0",
            "X-API-Language": self.language
        }
        
        # 映射 ioc_type 到 API 端点 / Map ioc_type to API endpoint
        type_mapping = {
            "ip": "ip",
            "domain": "domain", 
            "url": "url",
            "hash": "file",
            "md5": "file",
            "sha1": "file",
            "sha256": "file"
        }
        
        endpoint = type_mapping.get(ioc_type.lower(), "domain")
        
        # 根据advanced参数选择接口类型 / Choose API endpoint based on advanced parameter
        if advanced:
            url = f"{self.api_url}/api/{endpoint}/detail"
        else:
            url = f"{self.api_url}/api/{endpoint}/reputation"
        
        start_time = time.time()
        try:
            url_with_params = f"{url}?key={urllib.parse.quote(ioc_value)}"
            request = urllib.request.Request(url_with_params, headers=headers)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                response_time_ms = int((time.time() - start_time) * 1000)
                self.response_times.append(response_time_ms)
                
                data = response.read().decode('utf-8')
                result = json.loads(data)
                result['response_time_ms'] = response_time_ms
                return result
            
        except urllib.error.URLError as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            return {"error": f"{self.get_text('request_failed')}: {str(e)}", "response_time_ms": response_time_ms}
        except json.JSONDecodeError:
            response_time_ms = int((time.time() - start_time) * 1000)
            return {"error": self.get_text('invalid_json'), "response_time_ms": response_time_ms}
    
    def batch_query(self, iocs):
        """
        批量查询威胁情报 / Batch query threat intelligence
        
        Args:
            iocs (list): IOC列表，每个元素为 {"value": "ioc_value", "type": "ioc_type"}
                IOC list, each element is {"value": "ioc_value", "type": "ioc_type"}
        
        Returns:
            dict: 包含结果和统计信息 / Dictionary containing results and statistics
        """
        results = []
        batch_times = []
        
        for ioc in iocs:
            result = self.query_ioc(ioc["value"], ioc["type"])
            response_time = result.get('response_time_ms', 0)
            batch_times.append(response_time)
            
            results.append({
                "ioc": ioc["value"],
                "type": ioc["type"],
                "result": result,
                "response_time_ms": response_time
            })
        
        # 计算本次批量统计 / Calculate batch statistics
        if batch_times:
            batch_avg = sum(batch_times) / len(batch_times)
            batch_max = max(batch_times)
            batch_min = min(batch_times)
            batch_median = sorted(batch_times)[len(batch_times) // 2]
        else:
            batch_avg = batch_max = batch_min = batch_median = 0
        
        # 计算累计统计 / Calculate cumulative statistics
        if self.response_times:
            total_avg = sum(self.response_times) / len(self.response_times)
            total_max = max(self.response_times)
            total_min = min(self.response_times)
            total_median = sorted(self.response_times)[len(self.response_times) // 2]
            total_calls = len(self.response_times)
        else:
            total_avg = total_max = total_min = total_median = total_calls = 0
        
        return {
            "results": results,
            "batch_stats": {
                "batch_avg_ms": round(batch_avg, 2),
                "batch_max_ms": batch_max,
                "batch_min_ms": batch_min,
                "batch_median_ms": batch_median
            },
            "total_stats": {
                "total_calls": total_calls,
                "total_avg_ms": round(total_avg, 2),
                "total_max_ms": total_max,
                "total_min_ms": total_min,
                "total_median_ms": total_median
            }
        }

# 全局实例 / Global instance
yunzhan_intel = YunzhanThreatIntel()