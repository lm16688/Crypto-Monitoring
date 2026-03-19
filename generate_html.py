#!/usr/bin/env python3
"""
Crypto Monitoring - 完整信息HTML生成器
展示所有代币相关信息
- 移动端响应式设计
- 主流币显示价格，Meme币显示市值
- 真实API数据展示
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_monitor_and_get_data():
    """运行monitor.py并获取数据"""
    print("📊 开始生成HTML报告...")

    result = subprocess.run([sys.executable, 'monitor.py'],
                          capture_output=True, text=True,
                          cwd=Path(__file__).parent)

    print(result.stdout[-300:] if len(result.stdout) > 300 else result.stdout)

    import monitor

    monitor_instance = monitor.MemeCoinMonitor()
    meme_coins = monitor_instance.fetch_pump_data()
    mainstream_coins = monitor_instance.fetch_mainstream_data()

    analyzed_meme = monitor_instance.analyze_coins(meme_coins)
    analyzed_mainstream = monitor_instance.analyze_coins(mainstream_coins)

    return analyzed_meme, analyzed_mainstream

def format_market_cap(mc):
    """格式化市值"""
    if mc >= 1000000000:
        return f"${mc/1000000000:.2f}B"
    elif mc >= 1000000:
        return f"${mc/1000000:.2f}M"
    elif mc >= 1000:
        return f"${mc/1000:.1f}K"
    return f"${mc:,.0f}"

def format_holders(h):
    """格式化持有人数"""
    if h >= 1000000:
        return f"{h/1000000:.1f}M"
    elif h >= 1000:
        return f"{h/1000:.0f}K"
    return f"{h:,}"

def format_price(price):
    """格式化价格"""
    if price >= 1000:
        return f"${price:,.0f}"
    elif price >= 1:
        return f"${price:.2f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    else:
        return f"${price:.8f}"

def generate_coin_detail(coin, is_meme=True):
    """生成完整的代币详情卡片"""
    rating_badge = 'bg-green-500/20 text-green-400' if coin['score'] >= 80 else 'bg-yellow-500/20 text-yellow-400' if coin['score'] >= 60 else 'bg-red-500/20 text-red-400'

    # X平台帖子
    x_posts_html = ''
    for post in coin.get('x_posts', [])[:3]:
        post_url = post.get('url', '#')
        x_posts_html += f'''
        <div class="bg-gray-800/50 rounded-lg p-3 md:p-4 border border-gray-700/50">
            <div class="flex items-center gap-2 mb-2">
                <span class="text-blue-400 font-medium text-sm md:text-base">{post["author"]}</span>
                <span class="text-xs text-gray-500 bg-gray-700/30 px-2 py-1 rounded">热门帖子</span>
            </div>
            <p class="text-gray-300 text-sm mb-3 line-clamp-2">{post["content"]}</p>
            <div class="flex items-center justify-between flex-wrap gap-2">
                <div class="flex gap-4 text-xs text-gray-400">
                    <span>👍 {post["likes"]:,}</span>
                    <span>💬 {post["comments"]:,}</span>
                </div>
                <a href="{post_url}" target="_blank" class="text-blue-400 hover:text-blue-300 text-xs flex items-center gap-1">
                    查看帖子 <span>→</span>
                </a>
            </div>
        </div>
        '''

    # 新闻 - 处理字典列表格式
    news_html = ''
    for news in coin.get('news', [])[:5]:
        if isinstance(news, dict):
            # 新格式：包含title和url的字典
            news_title = news.get('title', '')
            news_url = news.get('url', '#')
            news_source = news.get('source', 'News')
            news_html += f'''
            <a href="{news_url}" target="_blank" class="flex items-start gap-3 p-3 hover:bg-gray-800/50 rounded-lg transition-colors border-l-2 border-yellow-500/50 block group">
                <span class="text-yellow-500 mt-0.5 text-sm">●</span>
                <div class="flex-1">
                    <p class="text-gray-300 text-sm line-clamp-2 group-hover:text-white transition-colors">{news_title}</p>
                    <p class="text-xs text-gray-500 mt-1">{news_source}</p>
                </div>
                <span class="text-blue-400 text-xs">→</span>
            </a>
            '''
        else:
            # 旧格式：字符串
            news_html += f'''
            <div class="flex items-start gap-3 p-3 hover:bg-gray-800/50 rounded-lg transition-colors border-l-2 border-yellow-500/50">
                <span class="text-yellow-500 mt-0.5 text-sm">●</span>
                <p class="text-gray-300 text-sm line-clamp-2">{news}</p>
            </div>
            '''

    # 高频关键词
    keywords = coin.get('high_frequency_keywords', [])
    keywords_html = ' '.join([f'<span class="bg-purple-500/20 text-purple-300 px-2 py-1 rounded text-xs">{k}</span>' for k in keywords]) if keywords else ''

    # X平台链接
    x_official = coin.get('x_official_account', '')
    x_community = coin.get('x_community_url', '')

    # 根据类型显示不同的信息
    info_label = "市值" if is_meme else "价格"
    info_value = format_market_cap(coin["market_cap"]) if is_meme else format_price(coin.get("current_price", coin.get("market_cap", 0) / 100000000))

    return f'''
    <div class="bg-gray-900/50 rounded-2xl p-4 md:p-6 border border-gray-800 hover:border-gray-700 transition-all duration-300 mb-6">
        <!-- 头部 -->
        <div class="flex flex-col md:flex-row md:items-start justify-between mb-4 md:mb-6 pb-4 md:pb-6 border-b border-gray-800 gap-4">
            <div class="flex items-center gap-3 md:gap-5">
                <div class="w-12 h-12 md:w-16 md:h-16 rounded-2xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-white font-bold text-xl md:text-2xl shadow-lg">
                    {coin["symbol"][:2]}
                </div>
                <div>
                    <h3 class="text-xl md:text-2xl font-bold text-white mb-1">{coin["name"]}</h3>
                    <p class="text-sm md:text-base text-gray-400">{coin["symbol"]}</p>
                    <div class="flex items-center gap-2 mt-2">
                        <span class="px-2 md:px-3 py-1 rounded-lg {rating_badge} font-semibold text-xs md:text-sm">
                            {coin["score"]}/100
                        </span>
                        <span class="text-base md:text-lg">{coin["rating"]}</span>
                    </div>
                </div>
            </div>
            <a href="{x_community}" target="_blank" class="bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 px-3 md:px-4 py-2 rounded-lg text-sm font-medium transition-colors self-start">
                🐦 X平台社区
            </a>
        </div>

        <!-- 基本信息 -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-4 md:mb-6">
            <div class="bg-gray-800/50 rounded-xl p-3 md:p-4 text-center border border-gray-700/50">
                <div class="text-xs text-gray-400 mb-2">{info_label}</div>
                <div class="text-lg md:text-xl font-bold text-white">{info_value}</div>
            </div>
            <div class="bg-gray-800/50 rounded-xl p-3 md:p-4 text-center border border-gray-700/50">
                <div class="text-xs text-gray-400 mb-2">持有人数</div>
                <div class="text-lg md:text-xl font-bold text-white">{format_holders(coin.get('holders', 0))}</div>
            </div>
            <div class="bg-gray-800/50 rounded-xl p-3 md:p-4 text-center border border-gray-700/50">
                <div class="text-xs text-gray-400 mb-2">24h涨幅</div>
                <div class="text-lg md:text-xl font-bold {"text-green-400" if coin["growth"] > 0 else "text-red-400"}">
                    {"+" if coin["growth"] > 0 else ""}{coin["growth"]:.2f}%
                </div>
            </div>
            <div class="bg-gray-800/50 rounded-xl p-3 md:p-4 text-center border border-gray-700/50">
                <div class="text-xs text-gray-400 mb-2">创建时间</div>
                <div class="text-sm md:text-base font-bold text-white">{coin.get('created_time', 'N/A')}</div>
            </div>
        </div>

        <!-- 合约地址 -->
        <div class="bg-gray-800/30 rounded-xl p-3 md:p-4 mb-4 md:mb-6 border border-gray-700/50">
            <div class="text-xs text-gray-400 mb-2 flex items-center gap-2">
                <span>📋</span>
                <span>合约地址</span>
            </div>
            <div class="text-gray-300 text-xs md:text-sm font-mono break-all bg-gray-900/50 p-2 md:p-3 rounded-lg">
                {coin.get("contract", "N/A")}
            </div>
        </div>

        <!-- 项目故事 -->
        <div class="bg-gray-800/30 rounded-xl p-3 md:p-4 mb-4 md:mb-6 border border-gray-700/50">
            <div class="text-xs text-gray-400 mb-2 flex items-center gap-2">
                <span>📖</span>
                <span>项目故事</span>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed">{coin.get("story", "暂无故事")}</p>
        </div>

        <!-- 核心叙事 -->
        <div class="bg-purple-500/10 rounded-xl p-3 md:p-4 mb-4 md:mb-6 border border-purple-500/30">
            <div class="text-xs text-purple-300 mb-2 flex items-center gap-2">
                <span>💭</span>
                <span>核心叙事</span>
            </div>
            <p class="text-gray-200 text-sm font-medium">{coin.get("narrative", "无")}</p>
        </div>

        <!-- X平台信息 -->
        <div class="bg-gray-800/30 rounded-xl p-3 md:p-4 mb-4 md:mb-6 border border-gray-700/50">
            <div class="text-xs text-gray-400 mb-3 md:mb-4 flex items-center gap-2">
                <span>🐦</span>
                <span>X平台信息</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
                <div>
                    <div class="text-xs text-gray-500 mb-1">官方账号</div>
                    <a href="{x_community}" target="_blank" class="text-blue-400 hover:text-blue-300 text-sm font-medium">
                        {x_official if x_official else 'N/A'}
                    </a>
                </div>
                <div>
                    <div class="text-xs text-gray-500 mb-1">社区讨论</div>
                    <a href="{x_community}" target="_blank" class="text-blue-400 hover:text-blue-300 text-sm">
                        查看讨论 <span>→</span>
                    </a>
                </div>
            </div>
        </div>

        <!-- 双栏内容 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
            <!-- X平台帖子 -->
            <div class="bg-gray-800/30 rounded-xl p-3 md:p-4 border border-gray-700/50">
                <div class="text-xs text-gray-400 mb-3 md:mb-4 flex items-center justify-between">
                    <span class="flex items-center gap-2">
                        <span>🐦</span>
                        <span>X平台热门帖子</span>
                    </span>
                    <a href="{x_community}" target="_blank" class="text-blue-400 hover:text-blue-300 text-xs">
                        查看更多 →
                    </a>
                </div>
                <div class="space-y-3 md:space-y-4">
                    {x_posts_html if x_posts_html else '<div class="text-gray-500 text-sm text-center py-4">暂无热门帖子</div>'}
                </div>
            </div>

            <!-- 新闻 + 高频关键词 -->
            <div class="space-y-3 md:space-y-4">
                <div class="bg-gray-800/30 rounded-xl p-3 md:p-4 border border-gray-700/50">
                    <div class="text-xs text-gray-400 mb-3 flex items-center gap-2">
                        <span>📰</span>
                        <span>相关新闻</span>
                    </div>
                    <div class="space-y-2">
                        {news_html if news_html else '<div class="text-gray-500 text-sm text-center py-4">暂无新闻</div>'}
                    </div>
                </div>

                <!-- 高频关键词 -->
                <div class="bg-gray-800/30 rounded-xl p-3 md:p-4 border border-gray-700/50">
                    <div class="text-xs text-gray-400 mb-3 flex items-center gap-2">
                        <span>🔤</span>
                        <span>高频讨论关键词</span>
                    </div>
                    <div class="flex flex-wrap gap-2">
                        {keywords_html if keywords_html else '<div class="text-gray-500 text-sm">暂无数据</div>'}
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''

def generate_html(meme_coins, mainstream_coins):
    """生成完整信息HTML页面"""

    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    meme_avg = round(sum(t['score'] for t in meme_coins) / len(meme_coins), 1) if meme_coins else 0
    mainstream_avg = round(sum(t['score'] for t in mainstream_coins) / len(mainstream_coins), 1) if mainstream_coins else 0

    # 生成详情卡片
    meme_cards = ''.join([generate_coin_detail(coin, is_meme=True) for coin in meme_coins])
    mainstream_cards = ''.join([generate_coin_detail(coin, is_meme=False) for coin in mainstream_coins])

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Monitoring — 加密货币热点监控</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
        }}
        .gradient-text {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .glass {{
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border:1px solid rgba(255, 255, 255, 0.1);
        }}
        .glow {{
            box-shadow: 0 0 40px rgba(102, 126, 234, 0.3);
        }}
    </style>
</head>
<body class="bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 min-h-screen text-gray-100">
    <!-- Header -->
    <header class="border-b border-gray-800 bg-gray-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 md:px-6 py-4 md:py-6">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 md:w-12 md:h-12 rounded-xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-white font-bold text-xl md:text-2xl glow">
                        🚀
                    </div>
                    <div>
                        <h1 class="text-2xl md:text-3xl font-bold gradient-text">Crypto Monitoring</h1>
                        <p class="text-xs md:text-sm text-gray-400 mt-0.5">加密货币热点监控系统</p>
                    </div>
                </div>
                <div class="flex flex-col md:flex-row items-start md:items-center gap-2 md:gap-4">
                    <div class="glass rounded-lg px-3 md:px-4 py-2 flex items-center gap-2">
                        <span class="text-yellow-400">●</span>
                        <span class="text-xs md:text-sm text-gray-300">实时更新</span>
                    </div>
                    <div class="glass rounded-lg px-3 md:px-4 py-2 text-xs md:text-sm text-gray-300">
                        更新于 {update_time}
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 md:px-6 py-6 md:py-8">
        <!-- Hero Stats -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-6 md:mb-8">
            <div class="glass rounded-2xl p-4 md:p-6 glow">
                <div class="text-xs text-gray-400 mb-2">Meme币总数</div>
                <div class="text-3xl md:text-4xl font-bold text-white">{len(meme_coins)}</div>
                <div class="text-xs text-gray-400 mt-1">pump.fun热门项目</div>
            </div>
            <div class="glass rounded-2xl p-4 md:p-6">
                <div class="text-xs text-gray-400 mb-2">主流币总数</div>
                <div class="text-3xl md:text-4xl font-bold text-white">{len(mainstream_coins)}</div>
                <div class="text-xs text-gray-400 mt-1">BTC/ETH/SOL等</div>
            </div>
            <div class="glass rounded-2xl p-4 md:p-6">
                <div class="text-xs text-gray-400 mb-2">高评分项目</div>
                <div class="text-3xl md:text-4xl font-bold text-green-400">{len([t for t in meme_coins + mainstream_coins if t['score'] >= 80])}</div>
                <div class="text-xs text-gray-400 mt-1">评分 ≥ 80</div>
            </div>
            <div class="glass rounded-2xl p-4 md:p-6">
                <div class="text-xs text-gray-400 mb-2">平均评分</div>
                <div class="text-3xl md:text-4xl font-bold text-purple-400">{(meme_avg + mainstream_avg) / 2:.1f}</div>
                <div class="text-xs text-gray-400 mt-1">综合评分</div>
            </div>
        </div>

        <!-- Data Sources -->
        <div class="glass rounded-2xl p-3 md:p-4 mb-6 md:mb-8 flex flex-col md:flex-row items-center justify-between gap-3">
            <div class="flex flex-wrap items-center gap-4 md:gap-6 text-xs md:text-sm text-gray-400">
                <span class="flex items-center gap-2">
                    <span class="text-blue-400">●</span>
                    CoinGecko
                </span>
                <span class="flex items-center gap-2">
                    <span class="text-purple-400">●</span>
                    X Platform
                </span>
                <span class="flex items-center gap-2">
                    <span class="text-green-400">●</span>
                    NewsAPI
                </span>
                <span class="flex items-center gap-2">
                    <span class="text-yellow-400">●</span>
                    pump.fun
                </span>
            </div>
            <div class="text-xs text-gray-500">
                ⚠️ 仅供参考，不构成投资建议
            </div>
        </div>

        <!-- Meme Coins Section -->
    '''

    if meme_coins:
        html += f'''
        <section class="mb-12 md:mb-16">
            <div class="flex flex-col md:flex-row md:items-center gap-3 mb-4 md:mb-6">
                <h2 class="text-2xl md:text-3xl font-bold text-white">🎲 Meme币板块</h2>
                <span class="glass rounded-full px-3 md:px-4 py-2 text-xs md:text-sm text-gray-300">{len(meme_coins)} 个</span>
            </div>
            <p class="text-gray-400 mb-6 md:mb-8 text-sm md:text-lg">pump.fun和X平台热门讨论的高潜力早期项目（强叙事+强社区推动，不限市值）</p>

            <div class="grid grid-cols-1 gap-4 md:gap-6">
                {meme_cards}
            </div>
        </section>
        '''
    else:
        html += '''
        <section class="mb-12 md:mb-16">
            <div class="bg-gray-800/50 rounded-xl p-6 text-center">
                <p class="text-gray-400">暂无Meme币数据，API可能受限或网络连接问题</p>
            </div>
        </section>
        '''

    html += f'''
        <!-- Mainstream Coins Section -->
        <section>
            <div class="flex flex-col md:flex-row md:items-center gap-3 mb-4 md:mb-6">
                <h2 class="text-2xl md:text-3xl font-bold text-white">💎 主流币板块</h2>
                <span class="glass rounded-full px-3 md:px-4 py-2 text-xs md:text-sm text-gray-300">{len(mainstream_coins)} 个</span>
            </div>
            <p class="text-gray-400 mb-6 md:mb-8 text-sm md:text-lg">BTC/ETH/SOL/TAO/KAS等知名主流加密货币</p>

            <div class="grid grid-cols-1 gap-4 md:gap-6">
                {mainstream_cards}
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="border-t border-gray-800 mt-12 md:mt-16">
        <div class="max-w-7xl mx-auto px-4 md:px-6 py-6 md:py-8">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div class="text-xs md:text-sm text-gray-400">
                    数据来源：CoinGecko · X Platform · NewsAPI · pump.fun
                </div>
                <div class="text-xs md:text-sm text-gray-400">
                    ⚠️ 仅供参考，不构成投资建议
                </div>
            </div>
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div class="text-xs md:text-sm text-gray-500">
                    © 2025 Crypto Monitoring · 每小时自动更新
                </div>
                <a href="https://github.com/lm16688/Crypto-Monitoring" class="text-purple-400 hover:text-purple-300 text-xs md:text-sm">
                    GitHub 仓库
                </a>
            </div>
        </div>
    </footer>
</body>
</html>'''

    return html

def main():
    """主函数"""
    meme_coins, mainstream_coins = run_monitor_and_get_data()

    docs_dir = Path(__file__).parent / 'docs'
    docs_dir.mkdir(exist_ok=True)

    print(f"✅ Meme币: {len(meme_coins)} 个")
    print(f"✅ 主流币: {len(mainstream_coins)} 个")

    html_content = generate_html(meme_coins, mainstream_coins)
    html_path = docs_dir / 'index.html'

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML报告已生成: {html_path}")
    print(f"🌐 访问: https://lm16688.github.io/Crypto-Monitoring/")

if __name__ == '__main__':
    main()
