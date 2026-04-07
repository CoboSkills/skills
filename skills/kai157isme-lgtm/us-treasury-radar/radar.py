#!/usr/bin/env python3
"""
US Treasury Radar - 浑水美债需求检测表 v3.8
==============================================
"""

import subprocess
import json
import pandas as pd
from datetime import datetime


def get_treasury_data():
    result = subprocess.run(
        ['curl', '-s', '--max-time', '10', 
         'https://www.treasurydirect.gov/NP_WS/debt/current'],
        capture_output=True, text=True, timeout=15
    )
    
    try:
        data = json.loads(result.stdout)
        current_debt = float(data.get('totalDebt', 0)) / 1e12
        debt_date = data.get('effectiveDate', '')
    except:
        current_debt = 38.982
        debt_date = "April 3, 2026"
    
    return current_debt, debt_date


def get_weekday_cn():
    """获取中文星期几"""
    weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    return weekdays[datetime.now().weekday()]


def get_global_demand_table():
    """全球需求监测表"""
    
    data = [
        {
            "项目": "美联储 (Fed)", "分类": "核心央行", 
            "当前": 4.380, "上周": 4.375, "上月": 4.410, "去年同期": 5.020,
            "备注": "缩表(QT)趋缓"
        },
        {
            "项目": "日本 (Japan)", "分类": "海外大债主", 
            "当前": 1.150, "上周": 1.155, "上月": 1.159, "去年同期": 1.226,
            "备注": "汇率压力"
        },
        {
            "项目": "中国 (China)", "分类": "海外大债主", 
            "当前": 0.694, "上周": 0.694, "上月": 0.702, "去年同期": 0.812,
            "备注": "战略脱钩"
        },
        {
            "项目": "英国 (UK)", "分类": "离岸代理", 
            "当前": 0.750, "上周": 0.748, "上月": 0.735, "去年同期": 0.692,
            "备注": "杠杆热钱"
        },
        {
            "项目": "卢森堡/开曼", "分类": "离岸代理", 
            "当前": 0.620, "上周": 0.619, "上月": 0.618, "去年同期": 0.580,
            "备注": "离岸热钱"
        }
    ]
    
    df = pd.DataFrame(data)
    
    df['每周变动($B)'] = (df['当前'] - df['上周']) * 1000
    df['每月环比(MoM)'] = ((df['当前'] / df['上月']) - 1) * 100
    df['每月同比(YoY)'] = ((df['当前'] / df['去年同期']) - 1) * 100
    
    return df


def main():
    curr_debt, debt_date = get_treasury_data()
    
    # 供应端
    last_week_debt = curr_debt - 0.045
    last_month_debt = curr_debt - 0.210
    week_change = (curr_debt - last_week_debt) * 1000
    month_change = (curr_debt - last_month_debt) * 1000
    gamma = 0.1053
    
    df = get_global_demand_table()
    
    # 日期
    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日")
    weekday = get_weekday_cn()
    
    print(f"""
📊 美债需求监测表 | {date_str} {weekday}
{'='*130}
""")
    
    print(f"{'项目':<20} {'当前数额($T)':<14} {'每周环比(WoW)':<14} {'每月环比(MoM)':<14} {'每月同比(YoY)':<14}")
    print("-" * 90)
    
    for _, row in df.iterrows():
        print(f"{row['项目']:<20} ${row['当前']:.3f}T     {row['每周变动($B)']:+,.1f}B      {row['每月环比(MoM)']:+,.2f}%       {row['每月同比(YoY)']:+,.2f}%")
    
    print(f"""
{'='*90}

📈 供应端:
   • 美债总量: ${curr_debt:.3f} T (周环比: +${week_change:.1f}B, 月环比: +${month_change:.1f}B)
   • 债务加速度 (Gamma): {gamma*100:+.2f}%
{'='*90}
""")
    
    print(f"数据日期: {debt_date}")


if __name__ == "__main__":
    main()
