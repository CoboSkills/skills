#!/usr/bin/env python3
"""
玄机子·掌纹图片压缩与分析脚本
专门用于压缩掌纹图片（保持原貌），然后进行天机分析
"""

import sys
import os
import json
import base64
import time
from PIL import Image
import requests

def get_openclaw_config_path():
    """获取OpenClaw配置路径，支持多种环境"""
    # 方法1: 环境变量
    env_path = os.getenv('OPENCLAW_CONFIG_PATH')
    if env_path:
        return env_path
    
    # 方法2: 用户主目录
    home_path = os.path.expanduser('~/.openclaw/openclaw.json')
    if os.path.exists(home_path):
        return home_path
    
    # 方法3: 默认路径（仅用于开发）
    return '/tmp/openclaw_test_config.json'

def compress_image_keep_original(image_path, max_dimension=1024, quality=85):
    """
    压缩图片但保持原貌
    保持原始比例，只减小尺寸和文件大小
    """
    print(f"📸 压缩图片: {os.path.basename(image_path)}")
    print(f"   原则: 保持原貌，只减小尺寸")
    
    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            original_format = img.format
            original_mode = img.mode
            
            print(f"   原始尺寸: {original_width}x{original_height}")
            print(f"   原始格式: {original_format}")
            print(f"   原始模式: {original_mode}")
            
            # 计算压缩后的尺寸（保持比例）
            if max(original_width, original_height) > max_dimension:
                ratio = max_dimension / max(original_width, original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                
                # 使用高质量重采样保持清晰度
                compressed_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"   压缩后尺寸: {new_width}x{new_height}")
                print(f"   压缩比例: {ratio:.2%}")
            else:
                # 图片已经小于最大尺寸，不改变尺寸
                compressed_img = img.copy()
                new_width, new_height = original_width, original_height
                print(f"   尺寸不变: {new_width}x{new_height} (已小于{max_dimension}px)")
            
            # 保存压缩后的图片（保持原格式）
            compressed_path = f"/tmp/compressed_palm_{int(time.time())}.jpg"
            
            # 保持原始格式，优化保存参数
            save_params = {
                'quality': quality,
                'optimize': True,
                'progressive': True  # 渐进式JPEG，更好加载
            }
            
            compressed_img.save(compressed_path, 'JPEG', **save_params)
            
            # 对比文件大小
            original_size = os.path.getsize(image_path)
            compressed_size = os.path.getsize(compressed_path)
            compression_ratio = compressed_size / original_size
            
            print(f"✅ 压缩完成:")
            print(f"   原始文件: {original_size:,} 字节")
            print(f"   压缩后文件: {compressed_size:,} 字节")
            print(f"   压缩率: {compression_ratio:.2%}")
            print(f"   保存路径: {compressed_path}")
            
            # 验证图片质量（简单检查）
            with Image.open(compressed_path) as check_img:
                check_size = check_img.size
                if check_size == (new_width, new_height):
                    print(f"   验证通过: 尺寸保持正确")
                else:
                    print(f"   ⚠️ 尺寸验证异常: {check_size} != {new_width}x{new_height}")
            
            return compressed_path
            
    except Exception as e:
        print(f"❌ 图片压缩失败: {type(e).__name__}: {e}")
        return None

def get_api_key_from_global():
    """从全局配置获取API密钥"""
    # 动态获取OpenClaw配置路径
    config_path = get_openclaw_config_path()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        providers = config.get("models", {}).get("providers", {})
        
        # 尝试从volcengine读取
        volcengine = providers.get("volcengine", {})
        api_key = volcengine.get("apiKey", "")
        
        if api_key:
            # [安全] 已移除API密钥打印
            return api_key
        
        # 尝试从doubao读取
        doubao = providers.get("doubao", {})
        api_key = doubao.get("apiKey", "")
        
        if api_key:
            # [安全] 已移除API密钥打印
            return api_key
        
        print("❌ 未找到API密钥")
        return None
        
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return None

def analyze_palm_with_tianji(image_path, gender="male", hand="left"):
    """
    使用天机系统分析掌纹
    gender: male/female (男性/女性)
    hand: left/right (左手/右手)
    """
    print(f"\n🧭 启动玄机子·天机掌纹分析")
    print(f"   性别: {gender}")
    print(f"   手掌: {hand}手")
    print("=" * 60)
    
    # 获取API密钥
    api_key = get_api_key_from_global()
    if not api_key:
        return None
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    print(f"📊 图片数据: {len(image_data):,} 字节")
    print(f"   Base64长度: {len(image_base64):,} 字符")
    
    # 天机专业分析提示词（针对男性左手）
    prompt = f"""【玄机子·天机掌纹专业分析指令】

你作为玄机子（风水大师智慧助手），请对这张{gender}性{hand}手掌纹图片进行专业、详细的天机分析。

## 重要背景信息：
- **性别**: {gender}性
- **手掌**: {hand}手（{'先天之手，代表天赋潜能' if hand == 'left' else '后天之手，代表后天发展'}）
- **图片状态**: 已专业压缩，保持原始比例和内容，确保掌纹细节完整

## 分析要求：

### 一、基础识别（基于完整掌纹图片）
1. 手掌整体特征（手型、大小、比例、皮肤状态）
2. 主要掌纹线完整识别（生命线、智慧线、感情线、事业线、财运线）
3. 特殊纹路和标记（十字纹、星纹、三角纹、岛纹、链状纹等）
4. 手指特征（长度、形状、关节状态）

### 二、传统掌相学专业解读（{gender}性特点）
1. **性格特征深度分析**：基于完整掌纹特征的个性解读
2. **健康状况全面评估**：生命线及相关纹路的健康提示（考虑{gender}性生理特点）
3. **事业发展详细分析**：事业线、智慧线的职业倾向和发展潜力
4. **感情婚姻深度解读**：感情线、婚姻线的情感状态和关系模式
5. **财运趋势综合分析**：财运线及相关纹路的财富运势和理财能力

### 三、五行八卦对应分析
1. 手掌各区域完整五行属性评估
2. 掌纹特征的八卦方位完整对应（乾、坤、震、巽、坎、离、艮、兑）
3. 五行平衡状态与针对性调理建议（针对{gender}性体质特点）

### 四、天机·综合运势评估
1. 当前运势状态全面评估
2. 优势领域与发展详细建议
3. 需要注意的方面与具体化解方法
4. 人生阶段发展与最佳时机把握

### 五、专业建议（{gender}性专属）
1. 事业发展具体方向建议（考虑{gender}性社会角色和发展特点）
2. 感情婚姻经营实用建议
3. 健康养生具体指导（{gender}性健康重点和养护方法）
4. 个人成长详细规划

## 报告格式要求：

请以"玄机子·天机掌纹分析报告（{gender}性{hand}手·完整原貌）"为标题，包含以下章节：

### 一、掌纹基础识别（完整原貌分析）
### 二、传统掌相学专业解读（{gender}性特点）
### 三、五行八卦对应分析
### 四、天机·综合运势评估
### 五、玄机子·专业建议（{gender}性专属）
### 六、重要说明

请确保分析：
1. 基于完整掌纹图片，不遗漏任何重要特征
2. 专业详实，结合{gender}性生理和心理特点
3. 积极正面，提供具体可操作的建��性建议
4. 结构清晰，易于理解
5. 在最后添加"重要说明"，明确此为传统文化娱乐参考

现在开始分析："""

    # 准备API请求
    api_request = {
        "model": "doubao-seed-2-0-pro-260215",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 4500,
        "temperature": 0.7
    }
    
    # 调用API
    print("🚀 调用天机·豆包视觉模型...")
    api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            api_url,
            headers=headers,
            json=api_request,
            timeout=180
        )
        elapsed_time = time.time() - start_time
        
        print(f"✅ API响应时间: {elapsed_time:.2f}秒")
        print(f"📡 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                analysis = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                # [安全] 已移除API密钥打印}, 输出{usage.get('completion_tokens')}, 总计{usage.get('total_tokens')}")
                
                return {
                    "success": True,
                    "analysis": analysis,
                    "response_time": elapsed_time,
                    "usage": usage,
                    "image_size": f"{Image.open(image_path).size[0]}x{Image.open(image_path).size[1]}"
                }
            else:
                return {
                    "success": False,
                    "error": "API响应格式异常"
                }
        else:
            return {
                "success": False,
                "error": f"API调用失败: {response.status_code}",
                "response_text": response.text[:500]
            }
            
    except requests.exceptions.Timeout:
        return {"success": False, "error": "API调用超时（180秒）"}
    except Exception as e:
        return {"success": False, "error": f"调用过程中出现错误: {type(e).__name__}: {e}"}

def save_analysis_report(analysis_result, original_image, compressed_image, gender, hand):
    """保存分析报告"""
    timestamp = int(time.time())
    report_file = f"/tmp/tianji_palm_analysis_{gender}_{hand}_compressed_{timestamp}.txt"
    
    with Image.open(original_image) as orig_img:
        orig_size = orig_img.size
        orig_file_size = os.path.getsize(original_image)
    
    with Image.open(compressed_image) as comp_img:
        comp_size = comp_img.size
        comp_file_size = os.path.getsize(compressed_image)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("玄机子·天机掌纹专业分析报告（完整原貌压缩版）\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"分析时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"性别: {gender}性\n")
        f.write(f"手掌: {hand}手\n")
        f.write(f"原始图片: {os.path.basename(original_image)}\n")
        f.write(f"原始尺寸: {orig_size[0]}x{orig_size[1]} 像素\n")
        f.write(f"原始文件大小: {orig_file_size:,} 字节\n")
        f.write(f"压缩后图片: {os.path.basename(compressed_image)}\n")
        f.write(f"压缩后尺寸: {comp_size[0]}x{comp_size[1]} 像素\n")
        f.write(f"压缩后文件大小: {comp_file_size:,} 字节\n")
        f.write(f"压缩率: {comp_file_size/orig_file_size:.2%}\n")
        f.write(f"分析工具: 豆包视觉模型 + 玄机子天机系统\n")
        f.write(f"响应时间: {analysis_result.get('response_time', 0):.2f}秒\n")
        f.write("\n" + "=" * 70 + "\n\n")
        f.write(analysis_result["analysis"])
        f.write("\n" + "=" * 70)
    
    return report_file

def main():
    """主函数"""
    print("=" * 70)
    print("🧭 玄机子·掌纹压缩与分析系统（保持原貌版）")
    print("=" * 70)
    
    # 参数设置
    original_image = "/tmp/test_images/example_palm.jpg"
    gender = "male"  # 男性
    hand = "left"    # 左手
    max_dimension = 1024  # 最大边长
    quality = 85     # JPEG质量
    
    if not os.path.exists(original_image):
        print(f"❌ 图片不存在: {original_image}")
        return
    
    print(f"📸 原始图片: {os.path.basename(original_image)}")
    
    # 1. 压缩图片（保持原貌）
    print("\n" + "=" * 70)
    print("🔄 开始压缩图片（保持原貌原则）")
    print("-" * 40)
    
    compressed_image = compress_image_keep_original(original_image, max_dimension, quality)
    
    if not compressed_image:
        print("❌ 图片压缩失败，无法继续分析")
        return
    
    # 2. 使用天机分析
    print("\n" + "=" * 70)
    analysis_result = analyze_palm_with_tianji(compressed_image, gender, hand)
    
    print("\n" + "=" * 70)
    print("分析结果:")
    print("=" * 70)
    
    if analysis_result and analysis_result["success"]:
        print("✅ 天机分析成功！")
        print(f"⏱️  响应时间: {analysis_result.get('response_time', 0):.2f}秒")
        
        print("\n" + "=" * 70)
        print(f"🧭 玄机子·天机掌纹分析报告（{gender}性{hand}手·完整原貌）")
        print("=" * 70)
        
        # 显示分析报告
        analysis = analysis_result["analysis"]
        print(analysis)
        
        print("\n" + "=" * 70)
        
        # 保存报告
        report_file = save_analysis_report(analysis_result, original_image, compressed_image, gender, hand)
        print(f"\n💾 完整报告已保存到: {report_file}")
        print("💡 报告包含：专业压缩 + 完整原貌分析 + 传统掌相学 + 五行八卦 + 综合运势")
        
        # 显示压缩效果
        print("\n📊 压缩效果对比（保持原貌）:")
        with Image.open(original_image) as orig_img:
            orig_size = orig_img.size
        with Image.open(compressed_image) as comp_img:
            comp_size = comp_img.size
        
        print(f"   原始: {orig_size[0]}x{orig_size[1]}像素, {os.path.getsize(original_image):,}字节")
        print(f"   压缩后: {comp_size[0]}x{comp_size[1]}像素, {os.path.getsize(compressed_image):,}字节")
        print(f"   尺寸保持: {orig_size[0]/orig_size[1]:.3f}:1 → {comp_size[0]/comp_size[1]:.3f}:1")
        print(f"   原貌保持: ✅ 比例不变，内容完整，细节保留")
        
    else:
        print("❌ 天机分析失败")
        if analysis_result:
            print(f"错误: {analysis_result.get('error', '未知错误')}")
        
        print("\n💡 备选方案：基于压缩图片的初步分析")
        print("-" * 40)
        print(f"根据压缩处理：")
        print(f"1. {gender}性{hand}手掌纹（完整原貌）")
        print(f"2. 专业压缩保持比例和内容")
        print(f"3. 优化文件大小便于API传输")
        print()
        print(f"玄机子原则：")
        print(f"- 保持图片原貌，不剪裁不扭曲")
        print(f"- 优化传输效率，不损失分析质量")
        print(f"- 基于完整掌纹进行专业分析")
        print(f"- 提供具体可操作建议")
        print()
        print(f"如需更详细分析，请确保：")
        print(f"1. 图片清晰度足够")
        print(f"2. 手掌完全展开")
        print(f"3. 光线均匀，无阴影反光")