#!/usr/bin/python3.11
# -*- coding: utf-8 -*-
"""
全球财报智能下载器 v1.0
- ✅ 自动识别市场（A 股/港股/美股）
- ✅ 自动选择合适的爬虫
- ✅ 自动下载所需文件
- ✅ 支持股票代码/公司名称
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Optional, Tuple

# 添加脚本路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class GlobalFinancialDownloader:
    """全球财报智能下载器"""
    
    def __init__(self):
        # 加载外部映射配置（使用 Skill 目录内的配置文件）
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.mapping_file = os.path.join(script_dir, 'stock_mapping.json')
        self.stock_market_map = {}
        self.name_stock_map = {}
        self.report_type_map = {
            'annual': {'cn': 'annual', 'hk': 'financial', 'us': '10-K'},
            '年报': {'cn': 'annual', 'hk': 'financial', 'us': '10-K'},
            'interim': {'cn': 'interim', 'hk': 'financial', 'us': '10-Q'},
            '中报': {'cn': 'interim', 'hk': 'financial', 'us': '10-Q'},
            '半年报': {'cn': 'interim', 'hk': 'financial', 'us': '10-Q'},
            'quarterly': {'cn': 'regular', 'hk': 'quarterly', 'us': '10-Q'},
            '季报': {'cn': 'regular', 'hk': 'quarterly', 'us': '10-Q'},
            '10-k': {'cn': 'annual', 'hk': 'financial', 'us': '10-K'},
            '10-q': {'cn': 'regular', 'hk': 'quarterly', 'us': '10-Q'},
            'all': {'cn': 'regular', 'hk': 'financial', 'us': 'all'},
            '全部': {'cn': 'regular', 'hk': 'financial', 'us': 'all'},
        }
        self.script_paths = {
            'cninfo_api_scraper': '/root/.openclaw/workspace/scripts/cninfo_api_scraper.py',
            'hkex_auto_scraper_v3': '/root/.openclaw/workspace/scripts/hkex_auto_scraper_v3.py',
            'sec_edgar_scraper': '/root/.openclaw/workspace/scripts/sec_edgar_scraper.py',
        }
        self.load_mapping()
    
    def load_mapping(self):
        """加载股票映射配置"""
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # A 股
            for code, cn_name, en_name in data.get('cn_stocks', {}).get('stocks', []):
                self.stock_market_map[code] = {'market': 'CN', 'name': en_name, 'script': 'cninfo_api_scraper'}
                self.name_stock_map[cn_name] = code
                self.name_stock_map[en_name] = code
            
            # 港股
            for code, cn_name, en_name in data.get('hk_stocks', {}).get('stocks', []):
                self.stock_market_map[code] = {'market': 'HK', 'name': en_name, 'script': 'hkex_auto_scraper_v3'}
                self.name_stock_map[cn_name] = code
                self.name_stock_map[en_name] = code
            
            # 美股
            for code, cn_name, en_name in data.get('us_stocks', {}).get('stocks', []):
                self.stock_market_map[code] = {'market': 'US', 'name': en_name, 'script': 'sec_edgar_scraper'}
                self.name_stock_map[cn_name] = code
                self.name_stock_map[en_name] = code
            
            print(f"✅ 加载映射：{len(self.stock_market_map)} 家公司")
            
        except Exception as e:
            print(f"⚠️ 加载映射失败：{e}，使用默认映射")
            # 使用默认映射（向后兼容）
            self.load_default_mapping()
    
    def load_default_mapping(self):
        """加载默认映射（硬编码）"""
        # 默认映射保持不变...
        self.stock_market_map = {
            '600519': {'market': 'CN', 'name': '贵州茅台', 'script': 'cninfo_api_scraper'},
            '00700': {'market': 'HK', 'name': 'tencent', 'script': 'hkex_auto_scraper_v3'},
            'AAPL': {'market': 'US', 'name': 'apple', 'script': 'sec_edgar_scraper'},
        }
        self.name_stock_map = {
            '贵州茅台': '600519',
            '腾讯': '00700',
            '苹果': 'AAPL',
        }
        
        # 报告类型映射
        self.report_type_map = {
            'annual': {'cn': 'annual', 'hk': 'financial', 'us': '10-K'},
            '年报': {'cn': 'annual', 'hk': 'financial', 'us': '10-K'},
            'interim': {'cn': 'interim', 'hk': 'financial', 'us': '10-Q'},
            '中报': {'cn': 'interim', 'hk': 'financial', 'us': '10-Q'},
            '半年报': {'cn': 'interim', 'hk': 'financial', 'us': '10-Q'},
            'quarterly': {'cn': 'regular', 'hk': 'quarterly', 'us': '10-Q'},
            '季报': {'cn': 'regular', 'hk': 'quarterly', 'us': '10-Q'},
            '10-k': {'cn': 'annual', 'hk': 'financial', 'us': '10-K'},
            '10-q': {'cn': 'regular', 'hk': 'quarterly', 'us': '10-Q'},
            'all': {'cn': 'regular', 'hk': 'financial', 'us': 'all'},
            '全部': {'cn': 'regular', 'hk': 'financial', 'us': 'all'},
        }
        
        # 脚本路径
        self.script_paths = {
            'cninfo_api_scraper': '/root/.openclaw/workspace/scripts/cninfo_api_scraper.py',
            'hkex_auto_scraper_v3': '/root/.openclaw/workspace/scripts/hkex_auto_scraper_v3.py',
            'sec_edgar_scraper': '/root/.openclaw/workspace/scripts/sec_edgar_scraper.py',
        }
    
    def identify_stock(self, identifier: str) -> Optional[Dict]:
        """识别股票代码和市场"""
        identifier = identifier.strip().upper()
        
        # 直接是股票代码
        if identifier in self.stock_market_map:
            return self.stock_market_map[identifier]
        
        # 是公司名称
        if identifier in self.name_stock_map:
            stock_code = self.name_stock_map[identifier]
            return self.stock_market_map.get(stock_code)
        
        # 尝试小写匹配（港股）
        identifier_lower = identifier.lower()
        for code, info in self.stock_market_map.items():
            if code.lower() == identifier_lower:
                return info
        
        return None
    
    def get_report_type(self, report_type: str, market: str) -> str:
        """获取对应市场的报告类型"""
        report_type = report_type.lower().strip()
        
        if report_type in self.report_type_map:
            return self.report_type_map[report_type].get(market, report_type)
        
        return report_type
    
    def download(self, stock_identifier: str, from_year: int, to_year: int,
                report_type: str = 'annual', download_pdf: bool = True) -> bool:
        """智能下载财报"""
        print("=" * 80)
        print("🌍 全球财报智能下载器 v1.0")
        print("=" * 80)
        print()
        
        # Step 1: 识别股票
        print(f"📝 识别股票：{stock_identifier}")
        stock_info = self.identify_stock(stock_identifier)
        
        if not stock_info:
            print(f"❌ 无法识别股票：{stock_identifier}")
            print("💡 支持的股票:")
            print("   A 股：600519 (贵州茅台), 000001 (平安银行)")
            print("   港股：00700 (腾讯), 09988 (阿里巴巴)")
            print("   美股：AAPL (苹果), MSFT (微软), GOOGL (谷歌)")
            return False
        
        market = stock_info['market']
        stock_code = list(self.stock_market_map.keys())[list(self.stock_market_map.values()).index(stock_info)]
        company_name = stock_info['name']
        script = stock_info['script']
        
        print(f"   ✅ 市场：{market}")
        print(f"   ✅ 代码：{stock_code}")
        print(f"   ✅ 公司：{company_name}")
        print(f"   ✅ 脚本：{script}")
        print()
        
        # Step 2: 转换报告类型
        target_type = self.get_report_type(report_type, market)
        print(f"📊 报告类型：{report_type} → {target_type} ({market})")
        print()
        
        # Step 3: 选择并执行脚本
        script_path = self.script_paths.get(script)
        if not script_path or not os.path.exists(script_path):
            print(f"❌ 脚本不存在：{script_path}")
            return False
        
        print(f"🚀 执行下载：{script_path}")
        print()
        
        # 构造命令
        if market == 'CN':
            cmd = f"/usr/local/bin/python3.11 {script_path} --stock={stock_code} --name={company_name} --from={from_year} --to={to_year} --type={target_type}"
        elif market == 'HK':
            cmd = f"/usr/local/bin/python3.11 {script_path} --stock={stock_code} --name={company_name} --from={from_year} --to={to_year} --type={target_type}"
        elif market == 'US':
            cmd = f"/usr/local/bin/python3.11 {script_path} --ticker={stock_code} --name={company_name} --from={from_year} --to={to_year} --type={target_type}"
        else:
            print(f"❌ 未知市场：{market}")
            return False
        
        if download_pdf:
            cmd += " --pdf"
        
        # 执行
        print(f"执行命令：{cmd}")
        print()
        
        os.system(cmd)
        
        print()
        print("=" * 80)
        print("✅ 下载完成！")
        print("=" * 80)
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='全球财报智能下载器 v1.0')
    parser.add_argument('stock', type=str, help='股票代码或公司名称')
    parser.add_argument('--from', dest='from_year', type=int, default=2020, help='开始年份')
    parser.add_argument('--to', dest='to_year', type=int, default=2025, help='结束年份')
    parser.add_argument('--type', dest='report_type', type=str, default='年报',
                       help='报告类型：年报/中报/季报/annual/interim/quarterly/10-K/10-Q')
    parser.add_argument('--pdf', dest='download_pdf', action='store_true', default=True,
                       help='下载 PDF 文件（默认下载）')
    parser.add_argument('--no-pdf', dest='download_pdf', action='store_false',
                       help='不下载 PDF 文件')
    
    args = parser.parse_args()
    
    downloader = GlobalFinancialDownloader()
    
    downloader.download(
        stock_identifier=args.stock,
        from_year=args.from_year,
        to_year=args.to_year,
        report_type=args.report_type,
        download_pdf=args.download_pdf
    )


if __name__ == "__main__":
    main()
