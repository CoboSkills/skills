# US Treasury Radar - 美债风险雷达

## 触发词
- 美债分析
- 美债雷达
- 浑水报告
- Muddy Waters
- US Treasury analysis
- 戴维期双杀

## 功能
实时获取美联储与外国持有美债数据，生成"浑水风险雷达"报告，检测"戴维期双杀"信号。

## 数据来源
- FRED API (Federal Reserve Economic Data)
- 美债总额：DEBTBTOTUSCZGDP
- 外资持有：FREDGTBAM02GPMM
- 美联储持有：TREAST

## 核心指标
| 指标 | 说明 |
|------|------|
| Delta (Δ) | 每月新增债务规模 |
| Gamma (Γ) | 债务加速度（本月新增 vs 上月新增） |
| MoM | 环比变化 |
| YoY | 同比变化 |

## 信号判定
- **戴维期双杀**：Gamma > 0 + 外资 YoY < 0
- **空头警告**：发债速度非线形扩张
- **去美元化**：外资持续减持

## 使用示例
```
用户：美债分析
→ 返回完整浑水风险雷达报告
```

## 输出格式
- 供应端分析（美债总量、Delta、Gamma）
- 需求端分析（外资、Fed 持有变化）
- 风险信号判定
- 投资建议

---
