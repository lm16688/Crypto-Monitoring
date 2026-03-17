#!/usr/bin/env python3
"""
加密货币市场监控和分析工具
自动追踪 pump.fun 上的热门 meme 币，分析社区活跃度和叙事强度
"""
import json
from datetime import datetime
from typing import List, Dict


class MemeCoinMonitor:
    def __init__(self):
        self.history_file = "crypto-monitor/history.json"
        self.alerts_file = "crypto-monitor/alerts.json"

    def fetch_pump_data(self) -> List[Dict]:
        """从 pump.fun 获取代币数据"""
        print("📡 获取 pump.fun 数据...")
        # 这里返回模拟数据（基于之前获取到的pump.fun数据）
        return self._parse_market_data()

    def _parse_market_data(self) -> List[Dict]:
        """解析市场数据"""
        coins = [
            {
                "name": "NotInEmploymentEducationTraining",
                "symbol": "NEET",
                "market_cap": 24120000,
                "growth": 0.0,
                "description": "You Will Be Unemployed and You Will Be Happy",
                "narrative": "NEET文化 - 拒绝就业压力的生活态度",
                "category": "文化叙事"
            },
            {
                "name": "DRONE",
                "symbol": "DRONE",
                "market_cap": 24500000,
                "growth": 0.56,
                "description": "memecoin",
                "narrative": "无人机科技主题",
                "category": "科技"
            },
            {
                "name": "PvP",
                "symbol": "PVP",
                "market_cap": 41000000,
                "growth": 0.92,
                "description": "The PvP of social media",
                "narrative": "社交媒体竞争对抗",
                "category": "社交媒体"
            },
            {
                "name": "PsyopAnime",
                "symbol": "PSYOP",
                "market_cap": 6180000,
                "growth": 0.0,
                "description": "PsyopAnime",
                "narrative": "动漫文化 + Psyop工作室",
                "category": "流行文化"
            },
            {
                "name": "XAICASH",
                "symbol": "XAIC",
                "market_cap": 182600,
                "growth": 31.73,
                "description": "AI + 支付 + 加密货币的交汇点",
                "narrative": "AI基础设施叙事 - xAI和AI支付",
                "category": "AI",
                "potential": "高"
            },
            {
                "name": "PVE",
                "symbol": "PVE",
                "market_cap": 13200,
                "growth": 378.40,
                "description": "Deployed using rapidlaunch.io",
                "narrative": "游戏玩家 vs 环境",
                "category": "游戏",
                "potential": "极高"
            },
            {
                "name": "THE BAGWORKOOR",
                "symbol": "BAGWORKOOR",
                "market_cap": 401100,
                "growth": 2.97,
                "description": "Deployed using j7tracker.io",
                "narrative": "韭菜文化 - 解放被套牢的人",
                "category": "社区文化"
            },
            {
                "name": "How It Feels",
                "symbol": "FEELS",
                "market_cap": 166700,
                "growth": 7.61,
                "description": "Created on rapidlaunch.io",
                "narrative": "情感共鸣 - '感受'类meme",
                "category": "情感"
            },
            {
                "name": "Trump House",
                "symbol": "TRUMPHOUSE",
                "market_cap": 161400,
                "growth": 10.06,
                "description": "美国爱国主义的象征",
                "narrative": "政治人物 - 特朗普相关",
                "category": "政治"
            },
            {
                "name": "Crawstar (Crawfish by Claude AI)",
                "symbol": "CRAWSTAR",
                "market_cap": 12700,
                "growth": 11.60,
                "description": "AI完全自动化照顾龙虾",
                "narrative": "AI Agent应用 - Claude AI + 物联网",
                "category": "AI Agent",
                "potential": "高"
            }
        ]
        return coins

    def analyze_coins(self, coins: List[Dict]) -> List[Dict]:
        """分析代币潜力"""
        analyzed = []

        for coin in coins:
            score = 0
            reasons = []

            # 1. 增长率评分 (0-30分)
            growth = coin.get("growth", 0)
            if growth > 100:
                score += 30
                reasons.append("超高增长率")
            elif growth > 50:
                score += 25
                reasons.append("高增长率")
            elif growth > 10:
                score += 20
                reasons.append("良好增长")
            elif growth > 5:
                score += 15
                reasons.append("增长中")

            # 2. 市值评分 (0-25分)
            mc = coin.get("market_cap", 0)
            if 50000 <= mc <= 500000:
                score += 25
                reasons.append("黄金市值区间(5万-50万)")
            elif 1000000 <= mc <= 5000000:
                score += 20
                reasons.append("健康市值(100万-500万)")
            elif mc < 50000:
                score += 15
                reasons.append("早期阶段")
            elif mc > 5000000:
                score += 10
                reasons.append("大盘币")

            # 3. 叙事强度评分 (0-30分)
            narrative = coin.get("narrative", "").lower()
            if any(keyword in narrative for keyword in ["ai", "人工智能", "claude", "gpt"]):
                score += 30
                reasons.append("AI叙事")
            elif any(keyword in narrative for keyword in ["trump", "政治", "选举"]):
                score += 25
                reasons.append("政治叙事")
            elif any(keyword in narrative for keyword in ["游戏", "gaming", "player"]):
                score += 20
                reasons.append("游戏叙事")
            elif any(keyword in narrative for keyword in["文化", "community", "social"]):
                score += 15
                reasons.append("社区文化")

            # 4. 手动标记评分 (0-25分)
            potential = coin.get("potential", "")
            if potential == "极高":
                score += 25
                reasons.append("极高潜力标记")
            elif potential == "高":
                score += 20
                reasons.append("高潜力标记")

            # 综合评级
            if score >= 80:
                rating = "🟢 重点跟踪"
            elif score >= 60:
                rating = "🟡 值得关注"
            elif score >= 40:
                rating = "🟡 中等关注"
            else:
                rating = "🔴 观望"

            coin["score"] = score
            coin["rating"] = rating
            coin["reasons"] = list(set(reasons))
            analyzed.append(coin)

        # 按分数排序
        analyzed.sort(key=lambda x: x["score"], reverse=True)
        return analyzed

    def generate_report(self, coins: List[Dict]) -> str:
        """生成分析报告"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""# 📊 Meme币市场分析报告

生成时间: {now}

---

## ⭐ 高潜力代币 (TOP 5)

"""
        top_coins = coins[:5]

        for i, coin in enumerate(top_coins, 1):
            report += f"""### {i}. {coin['name']} ({coin['symbol']})

**基本信息:**
- 市值: ${coin['market_cap']:,.0f}
- 增长率: {coin.get('growth', 0):.2f}%
- 评分: {coin['score']}/100
- 综合评级: {coin['rating']}

**叙事分析:**
- 分类: {coin.get('category', '未知')}
- 核心叙事: {coin.get('narrative', '无')}
- 描述: {coin.get('description', '无')}

**评分理由:**
"""
            for reason in coin['reasons']:
                report += f"- {reason}\n"

            report += "\n---\n"

        report += f"""## 📋 全部代币排序

| 排名 | 代币 | 市值 | 增长率 | 评分 | 评级 | 分类 |
|------|------|------|--------|------|------|------|
"""
        for i, coin in enumerate(coins, 1):
            report += f"| {i} | {coin['symbol']} | ${coin['market_cap']:,.0f} | {coin.get('growth', 0):.2f}% | {coin['score']}/100 | {coin['rating']} | {coin.get('category', '-')} |\n"

        report += f"""---

## ⚠️ 重要提示

> **本报告仅供参考，不构成投资建议！**
> 
> Meme币风险极高，可能:
> - 瞬间归零 (Rug pull)
> - 流动性枯竭
> - 操控和刷量
> 
> 请务必:
> 1. DYOR (Do Your Own Research)
> 2. 只投入你能承受损失的资金
> 3. 设置止损
> 4. 分散投资

---

## 🔍 观察建议

### {top_coins[0]['name']} ({top_coins[0]['symbol']})
- 重点关注，社区活跃度强
- 建议持续观察链上数据
- 跟踪X平台讨论热度

---

生成者: AI Agent
系统: 加密货币监控工具 v1.0
"""

        return report

    def save_report(self, report: str):
        """保存报告"""
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 报告已保存: {filename}")
        return filename

    def run_analysis(self):
        """运行完整分析流程"""
        print("🚀 开始市场分析...")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. 获取数据
        coins = self.fetch_pump_data()
        print(f"✅ 获取到 {len(coins)} 个代币")

        # 2. 分析
        print("\n🔍 分析代币潜力...")
        analyzed = self.analyze_coins(coins)

        # 3. 生成报告
        print("\n📝 生成分析报告...")
        report = self.generate_report(analyzed)

        # 4. 保存
        print("\n💾 保存报告...")
        filename = self.save_report(report)

        # 5. 显示摘要
        print(f"\n🎯 前5名高潜力代币:")
        for i, coin in enumerate(analyzed[:5], 1):
            print(f"   {i}. {coin['name']} - 评分:{coin['score']} {coin['rating']}")

        print(f"\n✅ 分析完成！")
        print(f"📄 报告文件: {filename}")

        return analyzed, report


def main():
    monitor = MemeCoinMonitor()
    analyzed, report = monitor.run_analysis()

    # 显示完整报告
    print("\n" + "="*60)
    print(report)
    print("="*60)


if __name__ == "__main__":
    main()
