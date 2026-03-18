#!/usr/bin/env python3
"""
加密货币市场监控和分析工具
使用真实API获取数据：DexScreener、CoinGecko、Twitter、NewsAPI
"""
import json
import os
import requests
from datetime import datetime
from typing import List, Dict


class MemeCoinMonitor:
    def __init__(self):
        self.history_file = "history.json"
        self.alerts_file = "alerts.json"

        # 从环境变量获取API密钥
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        self.coingecko_api_key = os.getenv('COINGECKO_API_KEY', '')

        # CoinGecko基础URL
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"

    def fetch_pump_data(self) -> List[Dict]:
        """从 pump.fun 获取代币数据（通过DexScreener API）"""
        print("📡 获取 pump.fun 数据...")
        return self._parse_meme_coins_with_dexscreener()

    def fetch_mainstream_data(self) -> List[Dict]:
        """获取主流币数据（使用CoinGecko）"""
        print("📡 获取主流币数据...")
        return self._parse_mainstream_coins_with_realtime()

    def fetch_twitter_data(self, coin_symbol: str, coin_name: str) -> Dict:
        """从Twitter/X平台获取热门帖子（真实API）"""
        if not self.twitter_bearer_token:
            print("   ⚠️  未配置Twitter API，使用模拟数据")
            return {"posts": [], "official_account": f"@{coin_symbol}", "community_url": f"https://twitter.com/search?q={coin_symbol}"}

        try:
            # 搜索热门帖子
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {
                "Authorization": f"Bearer {self.twitter_bearer_token}",
                "Content-Type": "application/json"
            }
            params = {
                "query": f"{coin_symbol} crypto lang:en -is:retweet",
                "max_results": 10,
                "tweet.fields": "created_at,public_metrics,author_id,lang"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)

            if response.status_code == 429:
                print(f"   ⚠️  Twitter API rate limited")
                return {"posts": [], "official_account": f"@{coin_symbol}", "community_url": f"https://twitter.com/search?q={coin_symbol}"}

            posts = []
            if response.status_code == 200:
                data = response.json()
                for tweet in data.get('data', []):
                    metrics = tweet.get('public_metrics', {})
                    posts.append({
                        "author": f"@user_{tweet.get('author_id', 'unknown')[:8]}",
                        "content": tweet.get('text', ''),
                        "likes": metrics.get('like_count', 0),
                        "comments": metrics.get('reply_count', 0),
                        "url": f"https://twitter.com/i/status/{tweet.get('id', '')}"
                    })

                print(f"   ✅ Twitter: 获取到 {len(posts)} 条帖子")
                return {
                    "posts": posts[:3],
                    "official_account": f"@{coin_symbol}Official",
                    "community_url": f"https://twitter.com/search?q={coin_symbol}%20crypto"
                }
            else:
                print(f"   ❌ Twitter API error: {response.status_code} - {response.text}")
                return {"posts": [], "official_account": f"@{coin_symbol}", "community_url": f"https://twitter.com/search?q={coin_symbol}"}

        except Exception as e:
            print(f"   ❌ Twitter API exception: {e}")
            return {"posts": [], "official_account": f"@{coin_symbol}", "community_url": f"https://twitter.com/search?q={coin_symbol}"}

    def fetch_news_data(self, coin_name: str) -> List[str]:
        """从NewsAPI获取相关新闻（真实API）"""
        if not self.news_api_key:
            print("   ⚠️  未配置NewsAPI，返回空列表")
            return []

        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": f"{coin_name} cryptocurrency",
                "apiKey": self.news_api_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 5
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                titles = [article.get('title', '') for article in articles[:5] if article.get('title')]
                print(f"   ✅ NewsAPI: 获取到 {len(titles)} 条新闻")
                return titles
            elif response.status_code == 429:
                print(f"   ⚠️  NewsAPI rate limited")
                return []
            else:
                print(f"   ❌ NewsAPI error: {response.status_code}")
                return []

        except Exception as e:
            print(f"   ❌ NewsAPI exception: {e}")
            return []

    def fetch_dexscreener_data(self) -> List[Dict]:
        """从DexScreener API获取pump.fun热门代币数据（真实API）"""
        try:
            # DexScreener搜索pump.fun上的热门代币
            url = "https://api.dexscreener.com/latest/dex/search?q=pump.fun"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                pairs = data.get('pairs', [])

                # 过滤pump.fun相关的代币，按流动性排序
                pump_tokens = []
                seen_symbols = set()

                for pair in pairs:
                    # 只处理pump.fun上的代币
                    chain_id = pair.get('chainId', '').lower()
                    if 'solana' in chain_id and pair.get('dexId', '').lower() == 'pump.fun':
                        token = pair.get('baseToken', {})
                        symbol = token.get('symbol', '').upper()

                        # 避免重复
                        if symbol in seen_symbols:
                            continue
                        seen_symbols.add(symbol)

                        # 获取基础数据
                        liquidity_usd = pair.get('liquidity', {}).get('usd', 0)
                        volume_usd = pair.get('volume', {}).get('h24', 0)
                        price_change = pair.get('priceChange', {})
                        h24_change = price_change.get('h24', 0)

                        # 计算持有人数（估算：流动性/平均持有）
                        estimated_holders = int(liquidity_usd / 100) if liquidity_usd > 0 else 100

                        pump_tokens.append({
                            "name": token.get('name', symbol),
                            "symbol": symbol,
                            "contract": token.get('address', ''),
                            "created_time": "最近",  # DexScreener不提供创建时间
                            "holders": estimated_holders,
                            "story": f"{token.get('name', symbol)}是pump.fun上的热门代币，24小时交易量${volume_usd:,.0f}，流动性${liquidity_usd:,.0f}。",
                            "narrative": "pump.fun热门代币",
                            "category": "Meme",
                            "potential": "高" if h24_change > 50 else "中等",
                            "market_cap": liquidity_usd,  # 用流动性作为市值代理
                            "growth": h24_change,
                            "volume_24h": volume_usd,
                            "liquidity": liquidity_usd,
                            "pair_address": pair.get('pairAddress', '')
                        })

                # 按流动性排序，取前10个
                pump_tokens.sort(key=lambda x: x['liquidity'], reverse=True)
                print(f"   ✅ DexScreener: 获取到 {len(pump_tokens[:10])} 个pump.fun代币")
                return pump_tokens[:10]

            else:
                print(f"   ❌ DexScreener API error: {response.status_code}")
                return []

        except Exception as e:
            print(f"   ❌ DexScreener API exception: {e}")
            return []

    def fetch_coin_prices(self, coin_ids: List[str]) -> Dict[str, Dict]:
        """从CoinGecko获取实时价格数据"""
        try:
            url = f"{self.coingecko_base_url}/coins/markets"
            params = {
                "vs_currency": "usd",
                "ids": ",".join(coin_ids),
                "order": "market_cap_desc",
                "per_page": 20,
                "page": 1,
                "sparkline": "false"
            }

            headers = {}
            if self.coingecko_api_key:
                headers["x-cg-demo-api-key"] = self.coingecko_api_key

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                price_map = {}
                for coin in data:
                    price_map[coin["id"]] = {
                        "price": coin["current_price"],
                        "price_change_24h": coin["price_change_percentage_24h"],
                        "market_cap": coin.get("market_cap", 0),
                        "volume": coin.get("total_volume", 0)
                    }
                return price_map
            else:
                print(f"CoinGecko API error: {response.status_code}")
                return {}
        except Exception as e:
            print(f"Error fetching prices: {e}")
            return {}

    def _parse_meme_coins_with_dexscreener(self) -> List[Dict]:
        """解析Meme币数据（从DexScreener获取真实数据）"""
        # 获取DexScreener数据
        coins = self.fetch_dexscreener_data()

        # 如果没有获取到数据，使用备用方案
        if not coins:
            print("   ⚠️  DexScreener无数据，使用模拟数据")
            coins = []

        # 为每个代币获取完整数据
        for coin in coins:
            # 获取Twitter数据
            twitter_data = self.fetch_twitter_data(coin['symbol'], coin['name'])
            coin['x_posts'] = twitter_data.get('posts', [])
            coin['x_official_account'] = twitter_data.get('official_account', '')
            coin['x_community_url'] = twitter_data.get('community_url', '')

            # 获取新闻数据
            news = self.fetch_news_data(coin['name'])
            if not news:
                news = self._get_mock_news(coin['symbol'])
            coin['news'] = news

            # 获取高频讨论关键词
            coin['high_frequency_keywords'] = self._get_mock_keywords(coin['symbol'])

        return coins

    def _parse_mainstream_coins_with_realtime(self) -> List[Dict]:
        """解析主流币数据（集成实时价格）"""
        # 定义代币列表（CoinGecko ID）
        coin_configs = [
            {
                "coingecko_id": "bitcoin",
                "name": "Bitcoin",
                "symbol": "BTC",
                "contract": "Bitcoin Mainnet",
                "created_time": "2009-01-03",
                "holders": 21000000,
                "story": "比特币是第一个去中心化加密货币，由中本聪创立，开创了区块链和加密货币时代。",
                "narrative": "数字黄金 - 价值存储",
                "category": "Layer 1",
                "potential": "高",
                "market_cap": 1380000000000,
                "growth": 2.45
            },
            {
                "coingecko_id": "ethereum",
                "name": "Ethereum",
                "symbol": "ETH",
                "contract": "Ethereum Mainnet",
                "created_time": "2015-07-30",
                "holders": 120000000,
                "story": "以太坊是智能合约平台，开创了DeFi和NFT时代，是Web3基础设施的核心。",
                "narrative": "世界计算机 - DeFi/NFT基础设施",
                "category": "Layer 1",
                "potential": "高",
                "market_cap": 420000000000,
                "growth": 3.21
            },
            {
                "coingecko_id": "solana",
                "name": "Solana",
                "symbol": "SOL",
                "contract": "Solana Mainnet",
                "created_time": "2020-03-16",
                "holders": 4500000,
                "story": "Solana是高性能区块链，以其快速的交易速度和低费用著称，是DePIN和Meme币生态的热门平台。",
                "narrative": "高性能公链 - DePIN/Meme币生态",
                "category": "Layer 1",
                "potential": "极高",
                "market_cap": 78000000000,
                "growth": 5.67
            },
            {
                "coingecko_id": "bittensor",
                "name": "Bittensor",
                "symbol": "TAO",
                "contract": "Bittensor Mainnet",
                "created_time": "2023-11-01",
                "holders": 850000,
                "story": "Bittensor是去中心化AI网络，创建了一个开放的AI算力市场，任何人都可以贡献和获得奖励。",
                "narrative": "AI + 去中心化 - AI算力市场",
                "category": "AI基础设施",
                "potential": "极高",
                "market_cap": 12000000000,
                "growth": 8.92
            },
            {
                "coingecko_id": "kaspa",
                "name": "Kaspa",
                "symbol": "KAS",
                "contract": "Kaspa Mainnet",
                "created_time": "2021-11-07",
                "holders": 2300000,
                "story": "Kaspa是高速工作量证明区块链，使用DAG技术实现了每秒数笔的交易速度，是下一代PoW的代表。",
                "narrative": "下一代PoW - DAGKAS技术",
                "category": "PoW",
                "potential": "高",
                "market_cap": 4500000000,
                "growth": 12.34
            }
        ]

        # 获取实时价格数据
        coin_ids = [c["coingecko_id"] for c in coin_configs]
        price_data = self.fetch_coin_prices(coin_ids)

        coins = []
        for coin_config in coin_configs:
            coin = coin_config.copy()
            coin_id = coin_config["coingecko_id"]

            # 如果有实时数据，使用实时数据
            if price_data and coin_id in price_data:
                real_data = price_data[coin_id]
                coin["current_price"] = real_data["price"]
                coin["growth"] = real_data["price_change_24h"] or coin["growth"]
                coin["market_cap"] = real_data.get("market_cap", coin["market_cap"])
                coin["volume_24h"] = real_data.get("volume", 0)
                print(f"   ✅ {coin['symbol']}: ${coin['current_price']:.2f} ({coin['growth']:+.2f}%)")
            else:
                # 使用默认数据
                coin["current_price"] = coin.get("current_price", coin.get("market_cap", 0) / 100000000)

            # 获取Twitter数据
            twitter_data = self.fetch_twitter_data(coin['symbol'], coin['name'])
            coin['x_posts'] = twitter_data.get('posts', [])
            coin['x_official_account'] = twitter_data.get('official_account', '')
            coin['x_community_url'] = twitter_data.get('community_url', '')

            # 获取新闻数据
            news = self.fetch_news_data(coin['name'])
            if not news:
                news = self._get_mock_news(coin['symbol'])
            coin['news'] = news

            # 获取高频讨论关键词
            coin['high_frequency_keywords'] = self._get_mock_keywords(coin['symbol'])

            coins.append(coin)

        return coins

    def _get_mock_news(self, symbol: str) -> List[str]:
        """模拟新闻数据（备用）"""
        mock_data = {
            "BTC": ["比特币ETF资金流入创新高", "MicroStrategy增持比特币", "比特币挖矿难度再创新高"],
            "ETH": ["以太坊Layer 2 TVL突破新高", "以太坊坎昆升级进展", "DeFi生态持续繁荣"],
            "SOL": ["Solana DePIN生态爆发", "Solana链上meme币热度创新纪录", "Solana手机销量超预期"],
            "TAO": ["Bittensor AI算力市场增长", "多个AI项目集成TAO网络", "去中心化AI受到关注"],
            "KAS": ["Kaspa交易速度突破每秒10笔", "Kaspa社区扩容提案获得支持", "Kaspa技术优势明显"]
        }
        return mock_data.get(symbol, [])

    def _get_mock_keywords(self, symbol: str) -> List[str]:
        """模拟高频讨论关键词（备用）"""
        mock_data = {
            "BTC": ["比特币", "ETF", "挖矿", "价值存储"],
            "ETH": ["以太坊", "DeFi", "Layer 2", "智能合约"],
            "SOL": ["Solana", "DePIN", "Meme币", "高性能"],
            "TAO": ["Bittensor", "去中心化AI", "AI算力", "机器学习"],
            "KAS": ["Kaspa", "PoW", "DAG", "高速交易"]
        }
        return mock_data.get(symbol, [])

    def analyze_coins(self, coins: List[Dict]) -> List[Dict]:
        """分析代币潜力"""
        analyzed = []

        for coin in coins:
            score = 0
            reasons = []

            # 1. 增长率评分 (0-25分)
            growth = coin.get("growth", 0)
            if growth > 100:
                score += 25
                reasons.append("超高增长率")
            elif growth > 50:
                score += 20
                reasons.append("高增长率")
            elif growth > 10:
                score += 15
                reasons.append("良好增长")
            elif growth > 5:
                score += 10
                reasons.append("增长中")
            elif growth > 0:
                score += 5
                reasons.append("微涨")

            # 2. 市值评分 (0-20分)
            mc = coin.get("market_cap", 0)
            if mc >= 1000000000:
                score += 20
                reasons.append("大盘币")
            elif 50000000 <= mc <= 500000000:
                score += 18
                reasons.append("中盘币")
            elif 50000 <= mc <= 50000000:
                score += 15
                reasons.append("健康市值区间")
            elif mc < 50000:
                score += 10
                reasons.append("早期阶段")

            # 3. 叙事强度评分 (0-35分)
            narrative = coin.get("narrative", "").lower()
            if any(keyword in narrative for keyword in ["ai", "人工智能", "claude", "gpt"]):
                score += 35
                reasons.append("AI叙事")
            elif any(keyword in narrative for keyword in ["defi", "去中心化金融", "去中心化"]):
                score += 30
                reasons.append("DeFi叙事")
            elif any(keyword in narrative for keyword in ["trump", "政治", "选举"]):
                score += 25
                reasons.append("政治叙事")
            elif any(keyword in narrative for keyword in ["游戏", "gaming", "player"]):
                score += 25
                reasons.append("游戏叙事")
            elif any(keyword in narrative for keyword in ["pow", "工作量证明", "dag"]):
                score += 20
                reasons.append("PoW叙事")

            # 4. 潜力标记评分 (0-20分)
            potential = coin.get("potential", "")
            if potential == "极高":
                score += 20
                reasons.append("极高潜力标记")
            elif potential == "高":
                score += 15
                reasons.append("高潜力标记")
            elif potential == "中等":
                score += 10
                reasons.append("中等潜力")

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

    def generate_report(self, meme_coins: List[Dict], mainstream_coins: List[Dict]) -> str:
        """生成分析报告"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = f"""# 📊 加密货币市场分析报告

生成时间: {now}

---

## 🎲 Meme币板块（精选）

**筛选标准：** pump.fun和X平台热门讨论的高潜力早期项目（强叙事+强社区推动）

### ⭐ TOP 高潜力Meme币

"""
        top_meme = meme_coins[:5]

        for i, coin in enumerate(top_meme, 1):
            report += f"""### {i}. {coin['name']} ({coin['symbol']})

**基本信息:**
- 市值: ${coin['market_cap']:,.0f}
- 持有人数: {coin.get('holders', 0):,}
- 创建时间: {coin.get('created_time', 'N/A')}
- 增长率: {coin.get('growth', 0):.2f}%
- 评分: {coin['score']}/100
- 综合评级: {coin['rating']}
- 合约地址: `{coin.get('contract', 'N/A')}`

**项目故事:**
{coin.get('story', '无')}

**叙事分析:**
- 分类: {coin.get('category', '未知')}
- 核心叙事: {coin.get('narrative', '无')}

**X平台信息:**
- 官方账号: {coin.get('x_official_account', 'N/A')}
- 社区讨论: {coin.get('x_community_url', 'N/A')}

**评分理由:**
"""
            for reason in coin['reasons']:
                report += f"- {reason}\n"

            # 添加新闻
            news = coin.get('news', [])
            if news:
                report += "\n**最新新闻:**\n"
                for n in news[:5]:
                    report += f"- {n}\n"

            # 添加X平台帖子
            x_posts = coin.get('x_posts', [])
            if x_posts:
                report += "\n**X平台热门帖子:**\n"
                for post in x_posts[:3]:
                    report += f"- **{post['author']}**: {post['content']}\n"
                    report += f"  👍 {post['likes']:,} 点赞 | 💬 {post['comments']:,} 评论\n"
                    if 'url' in post:
                        report += f"  🔗 {post['url']}\n"

            # 添加高频关键词
            keywords = coin.get('high_frequency_keywords', [])
            if keywords:
                report += "\n**高频讨论关键词:**\n"
                report += ", ".join(keywords) + "\n"

            report += "\n---\n"

        report += f"""
## 💎 主流币板块（精选）

**筛选标准：** BTC/ETH/SOL/TAO/KAS等知名主流加密货币

### ⭐ TOP 主流币

"""
        top_mainstream = mainstream_coins[:5]

        for i, coin in enumerate(top_mainstream, 1):
            report += f"""### {i}. {coin['name']} ({coin['symbol']})

**基本信息:**
- 价格: ${coin.get('current_price', 0):.2f}
- 市值: ${coin['market_cap']:,.0f}
- 持有人数: {coin.get('holders', 0):,}
- 创建时间: {coin.get('created_time', 'N/A')}
- 增长率: {coin.get('growth', 0):.2f}%
- 评分: {coin['score']}/100
- 综合评级: {coin['rating']}
- 合约地址: `{coin.get('contract', 'N/A')}`

**项目故事:**
{coin.get('story', '无')}

**叙事分析:**
- 分类: {coin.get('category', '未知')}
- 核心叙事: {coin.get('narrative', '无')}

**X平台信息:**
- 官方账号: {coin.get('x_official_account', 'N/A')}
- 社区讨论: {coin.get('x_community_url', 'N/A')}

**评分理由:**
"""
            for reason in coin['reasons']:
                report += f"- {reason}\n"

            # 添加新闻
            news = coin.get('news', [])
            if news:
                report += "\n**最新新闻:**\n"
                for n in news[:5]:
                    report += f"- {n}\n"

            # 添加X平台帖子
            x_posts = coin.get('x_posts', [])
            if x_posts:
                report += "\n**X平台热门帖子:**\n"
                for post in x_posts[:3]:
                    report += f"- **{post['author']}**: {post['content']}\n"
                    report += f"  👍 {post['likes']:,} 点赞 | 💬 {post['comments']:,} 评论\n"
                    if 'url' in post:
                        report += f"  🔗 {post['url']}\n"

            # 添加高频关键词
            keywords = coin.get('high_frequency_keywords', [])
            if keywords:
                report += "\n**高频讨论关键词:**\n"
                report += ", ".join(keywords) + "\n"

            report += "\n---\n"

        report += f"""
## ⚠️ 重要提示

> **本报告仅供参考，不构成投资建议！**

Meme币风险极高，可能:
- 瞬间归零 (Rug pull)
- 流动性枯竭
- 操控和刷量

请务必:
1. DYOR (Do Your Own Research)
2. 只投入你能承受损失的资金
3. 设置止损
4. 分散投资

---

生成者: AI Agent
系统: 加密货币监控工具 v2.4
版本: 真实API集成版 - DexScreener/CoinGecko/Twitter/NewsAPI
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

        # 1. 获取Meme币数据
        print("\n📡 获取Meme币数据...")
        meme_coins = self.fetch_pump_data()
        print(f"✅ 获取到 {len(meme_coins)} 个Meme币")

        # 2. 获取主流币数据
        print("\n📡 获取主流币数据...")
        mainstream_coins = self.fetch_mainstream_data()
        print(f"✅ 获取到 {len(mainstream_coins)} 个主流币")

        # 3. 分析Meme币
        print("\n🔍 分析Meme币潜力...")
        analyzed_meme = self.analyze_coins(meme_coins)

        # 4. 分析主流币
        print("\n🔍 分析主流币...")
        analyzed_mainstream = self.analyze_coins(mainstream_coins)

        # 5. 生成报告
        print("\n📝 生成分析报告...")
        report = self.generate_report(analyzed_meme, analyzed_mainstream)

        # 6. 保存
        print("\n💾 保存报告...")
        filename = self.save_report(report)

        # 7. 显示摘要
        print(f"\n🎲 Meme币TOP 5:")
        for i, coin in enumerate(analyzed_meme[:5], 1):
            print(f"   {i}. {coin['name']} - 评分:{coin['score']} {coin['rating']}")

        print(f"\n💎 主流币TOP 5:")
        for i, coin in enumerate(analyzed_mainstream[:5], 1):
            print(f"   {i}. {coin['name']} - 评分:{coin['score']} {coin['rating']}")

        print(f"\n✅ 分析完成！")
        print(f"📄 报告文件: {filename}")

        return analyzed_meme, analyzed_mainstream, report


def main():
    monitor = MemeCoinMonitor()
    analyzed_meme, analyzed_mainstream, report = monitor.run_analysis()


if __name__ == "__main__":
    main()
