#!/usr/bin/env python3
"""
Pure Wan Fridge Gourmet - 纯血万相冰箱盲盒
基于 Wan2.7/Wan2.1 视觉大模型的烹饪灵感触发器

本脚本 100% 使用 Wan2.1 API（阿里云 DashScope），未调用任何第三方 LLM。
支持异步任务提交和轮询查询。
支持参数：菜系、难易程度、烹饪时间
"""

import os
import sys
import base64
import json
import time
import requests
from typing import Optional, Dict, Any


class WanFridgeGourmet:
    """
    纯血万相冰箱盲盒核心类
    
    使用 Wan2.1 Image-to-Image API（阿里云 DashScope）将冰箱照片转化为米其林级美食概念图
    支持菜系、难易程度、烹饪时间等参数定制
    """
    
    # 菜系提示词映射
    CUISINE_PROMPTS = {
        "chinese": {
            "name": "中式料理",
            "prompt": "Chinese cuisine style, traditional Chinese ceramic plate, precise knife work, steam wisps, soy sauce glaze, scallion garnish, wok hei aroma visualized, traditional meets contemporary presentation"
        },
        "western": {
            "name": "西式料理", 
            "prompt": "Western cuisine style, elegant white porcelain plate, butter sauce, herb garnish, roasted vegetables, classic fine dining presentation"
        },
        "japanese": {
            "name": "日式料理",
            "prompt": "Japanese kaiseki-style, minimalist plating, zen aesthetic, seasonal ingredients, ceramic dishware, soft natural lighting, delicate presentation"
        },
        "french": {
            "name": "法式料理",
            "prompt": "French haute cuisine, artistic sauce drizzles, microgreens garnish, white porcelain, fine dining atmosphere, sophisticated plating"
        },
        "italian": {
            "name": "意式料理",
            "prompt": "Italian trattoria style, rustic family-style plating, rich tomato sauces, fresh herbs, wooden table background, warm golden lighting"
        },
        "korean": {
            "name": "韩式料理",
            "prompt": "Korean cuisine style, sizzling hot plate, gochujang glaze, sesame seeds garnish, colorful banchan arrangement, modern Korean presentation"
        },
        "thai": {
            "name": "泰式料理",
            "prompt": "Thai cuisine style, vibrant tropical colors, coconut curry sauce, fresh lime and chili garnish, banana leaf plating, exotic presentation"
        },
        "fusion": {
            "name": "融合料理",
            "prompt": "Fusion cuisine combining Eastern and Western techniques, unexpected flavor pairings, avant-garde plating, dramatic shadows, innovative presentation"
        }
    }
    
    # 难易程度提示词映射
    DIFFICULTY_PROMPTS = {
        "easy": {
            "name": "简单快手",
            "prompt": "Simple home cooking style, minimal preparation steps, easy-to-find ingredients, straightforward plating, beginner-friendly dish"
        },
        "medium": {
            "name": "适中难度",
            "prompt": "Intermediate cooking level, balanced technique and flavor, moderate preparation complexity, appealing presentation"
        },
        "hard": {
            "name": "挑战级",
            "prompt": "Advanced culinary technique, complex preparation steps, professional chef-level execution, sophisticated molecular gastronomy elements"
        }
    }
    
    # 烹饪时间提示词映射
    TIME_PROMPTS = {
        "quick": {
            "name": "快手菜（15分钟内）",
            "prompt": "Quick 15-minute recipe, stir-fry or raw preparation, fresh ingredients, minimal cooking time, fast casual style"
        },
        "moderate": {
            "name": "适中（30-45分钟）",
            "prompt": "30-45 minute cooking time, balanced preparation and cooking, medium complexity, home dinner style"
        },
        "slow": {
            "name": "慢炖/精煮（1小时以上）",
            "prompt": "Slow cooking 1+ hour, braised or stewed dish, deep flavors developed over time, tender texture, weekend cooking project"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        初始化 WanFridgeGourmet
        
        Args:
            api_key: DashScope API Key，如未提供则从环境变量 WAN_API_KEY 读取
            api_url: DashScope API 端点，如未提供则使用默认端点
        """
        self.api_key = api_key or os.environ.get("WAN_API_KEY")
        self.api_url = api_url or os.environ.get(
            "WAN_API_URL", 
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        )
        
        if not self.api_key:
            raise ValueError(
                "API Key 未设置。请通过参数传入或设置环境变量 WAN_API_KEY"
            )
    
    def _encode_image(self, image_path: str) -> str:
        """将图片文件转为 base64 编码"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _build_prompt(
        self,
        cuisine: str = "chinese",
        difficulty: str = "medium",
        cooking_time: str = "moderate",
        custom_requirements: Optional[str] = None
    ) -> str:
        """
        构建完整的提示词
        
        Args:
            cuisine: 菜系 (chinese/western/japanese/french/italian/korean/thai/fusion)
            difficulty: 难易程度 (easy/medium/hard)
            cooking_time: 烹饪时间 (quick/moderate/slow)
            custom_requirements: 额外自定义要求
            
        Returns:
            完整的提示词字符串
        """
        # 获取各部分提示词
        cuisine_info = self.CUISINE_PROMPTS.get(cuisine, self.CUISINE_PROMPTS["chinese"])
        difficulty_info = self.DIFFICULTY_PROMPTS.get(difficulty, self.DIFFICULTY_PROMPTS["medium"])
        time_info = self.TIME_PROMPTS.get(cooking_time, self.TIME_PROMPTS["moderate"])
        
        # 构建基础提示词
        base_prompt = f"""Based semantically on the ingredients found in the input image, create a highly detailed, exquisite gourmet dish.

Cuisine Style: {cuisine_info['prompt']}

Difficulty Level: {difficulty_info['prompt']}

Cooking Time: {time_info['prompt']}

The messy spatial arrangement of the fridge is completely ignored. The core semantic identities of the ingredients are extracted and synthesized into a beautiful, artfully plated culinary concept.

Photography style: macro shot, dark food photography, dramatic rim lighting, film grain, 8k, photorealistic, appetizing."""
        
        # 添加自定义要求
        if custom_requirements:
            base_prompt += f"\n\nAdditional Requirements: {custom_requirements}"
        
        return base_prompt.strip()
    
    def generate(
        self,
        image_path: str,
        cuisine: str = "chinese",
        difficulty: str = "medium",
        cooking_time: str = "moderate",
        custom_requirements: Optional[str] = None,
        size: str = "1024*1024",
        seed: Optional[int] = None,
        max_retries: int = 30,
        poll_interval: int = 2,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成美食概念图（支持异步轮询和详细参数定制）
        
        Args:
            image_path: 冰箱照片路径
            cuisine: 菜系选择
            difficulty: 难易程度
            cooking_time: 烹饪时间
            custom_requirements: 额外自定义要求
            size: 输出图片尺寸
            seed: 随机种子（可选）
            max_retries: 最大轮询次数
            poll_interval: 轮询间隔（秒）
            **kwargs: 其他 API 参数
            
        Returns:
            包含 image_url 或 error 的字典
        """
        # 构建提示词
        prompt = self._build_prompt(cuisine, difficulty, cooking_time, custom_requirements)
        
        # 获取参数中文名称用于显示
        cuisine_name = self.CUISINE_PROMPTS.get(cuisine, {}).get("name", cuisine)
        difficulty_name = self.DIFFICULTY_PROMPTS.get(difficulty, {}).get("name", difficulty)
        time_name = self.TIME_PROMPTS.get(cooking_time, {}).get("name", cooking_time)
        
        # 编码图片
        try:
            encoded_image = self._encode_image(image_path)
        except FileNotFoundError:
            return {"error": f"图片文件未找到: {image_path}"}
        except Exception as e:
            return {"error": f"图片编码失败: {str(e)}"}
        
        # 组装 API 请求（DashScope 格式）
        payload = {
            "model": "wanx2.1-t2i-plus",
            "input": {
                "prompt": prompt,
                "image": encoded_image
            },
            "parameters": {
                "size": size,
                "n": 1,
                **({"seed": seed} if seed else {}),
                **kwargs
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"
        }
        
        # 提交异步任务
        print(f"🚀 提交图像生成任务...")
        print(f"   模型: wanx2.1-t2i-plus")
        print(f"   菜系: {cuisine_name}")
        print(f"   难度: {difficulty_name}")
        print(f"   时间: {time_name}")
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code != 200:
                return {
                    "error": "任务提交失败",
                    "status_code": response.status_code,
                    "response": response.text[:500]
                }
            
            result = response.json()
            
            task_id = result.get("output", {}).get("task_id")
            if not task_id:
                return {
                    "error": "响应中未找到 task_id",
                    "raw_response": result
                }
            
            print(f"📝 任务ID: {task_id}")
            
            # 轮询查询结果
            print(f"\n⏳ 开始轮询任务状态...")
            query_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
            
            for i in range(max_retries):
                time.sleep(poll_interval)
                print(f"   第 {i+1} 次查询...", end=" ")
                
                query_response = requests.get(query_url, headers=headers, timeout=30)
                
                if query_response.status_code != 200:
                    print(f"查询失败: {query_response.status_code}")
                    continue
                
                task_result = query_response.json()
                status = task_result.get("output", {}).get("task_status", "UNKNOWN")
                print(f"状态: {status}")
                
                if status == "SUCCEEDED":
                    results = task_result.get("output", {}).get("results", [])
                    if results and len(results) > 0:
                        image_url = results[0].get("url")
                        print(f"\n🎉 任务完成！")
                        return {
                            "success": True,
                            "image_url": image_url,
                            "cuisine": cuisine,
                            "cuisine_name": cuisine_name,
                            "difficulty": difficulty,
                            "difficulty_name": difficulty_name,
                            "cooking_time": cooking_time,
                            "cooking_time_name": time_name,
                            "task_id": task_id,
                            "raw_response": task_result
                        }
                    else:
                        return {
                            "error": "任务成功但未返回图片 URL",
                            "raw_response": task_result
                        }
                
                elif status == "FAILED":
                    return {
                        "error": "任务执行失败",
                        "task_id": task_id,
                        "raw_response": task_result
                    }
            
            return {
                "error": "轮询超时，请稍后手动查询",
                "task_id": task_id,
                "query_url": query_url
            }
            
        except requests.exceptions.Timeout:
            return {"error": "请求超时，请检查网络或稍后重试"}
        except requests.exceptions.ConnectionError:
            return {"error": "连接失败，请检查 API URL 是否正确"}
        except Exception as e:
            return {"error": f"请求异常: {str(e)}"}
    
    def query_task(self, task_id: str) -> Dict[str, Any]:
        """查询已提交任务的状态"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        query_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        
        try:
            response = requests.get(query_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "查询失败",
                    "status_code": response.status_code,
                    "response": response.text[:500]
                }
        except Exception as e:
            return {"error": f"查询异常: {str(e)}"}


def generate_gourmet_from_fridge_photo(
    image_path: str,
    api_key: Optional[str] = None,
    api_url: Optional[str] = None,
    cuisine: str = "chinese",
    difficulty: str = "medium",
    cooking_time: str = "moderate",
    **kwargs
) -> Dict[str, Any]:
    """
    便捷函数：从冰箱照片生成美食概念图
    
    Args:
        image_path: 冰箱照片路径
        api_key: API Key（可选）
        api_url: API URL（可选）
        cuisine: 菜系
        difficulty: 难易程度
        cooking_time: 烹饪时间
        **kwargs: 其他参数
        
    Returns:
        生成结果字典
    """
    gourmet = WanFridgeGourmet(api_key=api_key, api_url=api_url)
    return gourmet.generate(
        image_path,
        cuisine=cuisine,
        difficulty=difficulty,
        cooking_time=cooking_time,
        **kwargs
    )


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="纯血万相冰箱盲盒 - 将冰箱照片转为米其林级美食概念图",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 generate_gourmet.py fridge.jpg --cuisine chinese --difficulty easy --cooking-time quick
  python3 generate_gourmet.py fridge.jpg -c western -d medium -t moderate
  python3 generate_gourmet.py --query <task_id>
        """
    )
    
    parser.add_argument("image", nargs="?", help="冰箱照片路径")
    
    # 菜系参数
    parser.add_argument(
        "--cuisine", "-c",
        choices=["chinese", "western", "japanese", "french", "italian", "korean", "thai", "fusion"],
        default="chinese",
        help="菜系选择（默认: chinese 中式）"
    )
    
    # 难易程度参数
    parser.add_argument(
        "--difficulty", "-d",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="难易程度（默认: medium 适中）"
    )
    
    # 烹饪时间参数
    parser.add_argument(
        "--cooking-time", "-t",
        choices=["quick", "moderate", "slow"],
        default="moderate",
        help="烹饪时间（默认: moderate 30-45分钟）"
    )
    
    # 自定义要求
    parser.add_argument(
        "--custom", "-x",
        help="额外自定义要求（如：不要辣、适合减脂、适合宝宝等）"
    )
    
    # 其他参数
    parser.add_argument("--seed", type=int, help="随机种子")
    parser.add_argument("--output", "-o", help="输出结果保存路径（JSON格式）")
    parser.add_argument("--query", help="查询已有任务状态（传入 task_id）")
    
    args = parser.parse_args()
    
    # 检查环境变量
    if not os.environ.get("WAN_API_KEY") and not args.query:
        print("❌ 错误: 未设置 WAN_API_KEY 环境变量")
        print("   请运行: export WAN_API_KEY='your-api-key'")
        sys.exit(1)
    
    gourmet = WanFridgeGourmet()
    
    # 查询模式
    if args.query:
        result = gourmet.query_task(args.query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    # 检查图片路径
    if not args.image:
        print("❌ 错误: 请提供冰箱照片路径")
        parser.print_help()
        sys.exit(1)
    
    # 生成模式
    result = gourmet.generate(
        args.image,
        cuisine=args.cuisine,
        difficulty=args.difficulty,
        cooking_time=args.cooking_time,
        custom_requirements=args.custom,
        seed=args.seed
    )
    
    # 输出结果
    if result.get("success"):
        print("\n✅ 生成成功！")
        print(f"   图片链接: {result['image_url']}")
        print(f"   菜系: {result['cuisine_name']}")
        print(f"   难度: {result['difficulty_name']}")
        print(f"   时间: {result['cooking_time_name']}")
        print(f"   任务ID: {result['task_id']}")
        print("\n（本图片语义完全源自您的冰箱照片，由 Wan2.1 独家生成）")
    else:
        print(f"\n❌ 生成失败: {result.get('error', '未知错误')}")
        if "task_id" in result:
            print(f"   任务ID: {result['task_id']}")
            print(f"   可稍后查询: python3 generate_gourmet.py --query {result['task_id']}")
        sys.exit(1)
    
    # 保存结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存至: {args.output}")


if __name__ == "__main__":
    main()
