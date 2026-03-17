#!/usr/bin/env python3
"""
HTML报告生成器 - 为GitHub Pages创建Web界面
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

def extract_latest_report_from_readme():
    """从README中提取最新的代币数据"""
    readme_path = Path(__file__).parent / 'README.md'
    
    if not readme_path.exists():
        return []
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取表格数据
    tokens = []
    
    # 查找TOP表格部分
    table_pattern = r'\|\s*(\d+)\s*\|\s*\*\*([A-Z]+)\*\*\s*\|\s*\$([\d,]+)\s*\|\s*([\d.]+)%\s*\|\s*\*\*(\d+)/100\*\*\s*\|\s*[🟢🟡🔴]\s*(重点跟踪|值得关注|观望)\s*\|\s*([^\|]+)\s*\|'
    
    matches = re.finditer(table_pattern, content)
    
    for match in matches:
        rank = int(match.group(1))
        symbol = match.group(2)
        market_cap = match.group(3).replace(',', '')
        growth_rate = float(match.group(4))
        score = int(match.group(5))
        rating = match.group(6)
        category = match.group(7).strip()
        
        # 判断是主流货币还是meme币
        # 市值超过10万美元的为主流货币
        is_mainstream = float(market_cap) >= 100000
        
        token = {
            'rank': rank,
            'symbol': symbol,
            'market_cap': float(market_cap),
            'growth_rate': growth_rate,
            'score': score,
            'rating': rating,
            'category': category.strip(),
            'is_mainstream': is_mainstream
        }
        
        tokens.append(token)
    
    return tokens

def generate_html(tokens):
    """生成HTML页面"""
    
    # 分类数据
    mainstream_tokens = [t for t in tokens if t['is_mainstream']]
    meme_tokens = [t for t in tokens if not t['is_mainstream']]
    
    # 排序
    mainstream_tokens.sort(key=lambda x: x['score'], reverse=True)
    meme_tokens.sort(key=lambda x: x['score'], reverse=True)
    
    # 获取更新时间
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Crypto Monitoring - 加密货币监控系统</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            color: white;
            padding: 40px 20px;
            margin-bottom: 30px;
        }}
        
        header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .update-time {{
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 15px;
            font-size: 0.9em;
        }}
        
        .section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .stat-card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 5px;
        }}
        
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f8f9ff;
        }}
        
        .score {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .score.high {{
            color: #10b981;
        }}
        
        .score.medium {{
            color: #f59e0b;
        }}
        
        .score.low {{
            color: #ef4444;
        }}
        
        .rating {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .rating.high {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .rating.medium {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .rating.low {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .growth {{
            color: #10b981;
            font-weight: bold;
        }}
        
        .growth.negative {{
            color: #ef4444;
        }}
        
        .category-badge {{
            display: inline-block;
            padding: 4px 10px;
            background: #e0e7ff;
            color: #4338ca;
            border-radius: 12px;
            font-size: 0.85em;
        }}
        
        footer {{
            text-align: center;
            color: white;
            padding: 30px 20px;
            margin-top: 30px;
        }}
        
        .warning {{
            background: #fee2e2;
            color: #991b1b;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #ef4444;
        }}
        
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 2em;
            }}
            
            .section {{
                padding: 15px;
            }}
            
            th, td {{
                padding: 10px;
                font-size: 0.9em;
            }}
            
            table {{
                display: block;
                overflow-x: auto;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 Crypto Monitoring</h1>
            <p>加密货币实时监控和分析系统</p>
            <div class="update-time">⏰ 最后更新: {update_time} (UTC+8)</div>
        </header>
        
        <div class="section">
            <div class="warning">
                <strong>⚠️ 风险提示：</strong>Meme币投资风险极高，可能导致本金全部损失。本报告仅供参考，不构成投资建议。请务必DYOR（自己做研究）！
            </div>
        </div>
        
        <div class="section">
            <h2 class="section-title">💎 主流货币板块</h2>
            <p style="color: #666; margin-bottom: 15px;">市值 ≥ $100,000 的稳定项目</p>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>总数量</h3>
                    <div class="value">{len(mainstream_tokens)}</div>
                </div>
                <div class="stat-card">
                    <h3>高评分项目</h3>
                    <div class="value">{len([t for t in mainstream_tokens if t['score'] >= 80])}</div>
                </div>
                <div class="stat-card">
                    <h3>平均评分</h3>
                    <div class="value">{sum(t['score'] for t in mainstream_tokens) / len(mainstream_tokens):.1f}</div>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>代币</th>
                        <th>市值</th>
                        <th>增长率</th>
                        <th>评分</th>
                        <th>评级</th>
                        <th>分类</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_token_rows(mainstream_tokens)}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2 class="section-title">🎲 Meme币板块</h2>
            <p style="color: #666; margin-bottom: 15px;">市值 < $100,000 的高潜力早期项目</p>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>总数量</h3>
                    <div class="value">{len(meme_tokens)}</div>
                </div>
                <div class="stat-card">
                    <h3>高评分项目</h3>
                    <div class="value">{len([t for t in meme_tokens if t['score'] >= 80])}</div>
                </div>
                <div class="stat-card">
                    <h3>平均评分</h3>
                    <div class="value">{sum(t['score'] for t in meme_tokens) / len(meme_tokens):.1f}</div>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>代币</th>
                        <th>市值</th>
                        <th>增长率</th>
                        <th>评分</th>
                        <th>评级</th>
                        <th>分类</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_token_rows(meme_tokens)}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>🔗 <a href="https://github.com/lm16688/Crypto-Monitoring" style="color: white; text-decoration: underline;">GitHub仓库</a> | ⏱️ 每小时自动更新</p>
            <p style="margin-top: 10px; opacity: 0.8;">使用 ❤️ 和 AI Agent 构建</p>
        </footer>
    </div>
</body>
</html>"""
    
    return html_template

def generate_token_rows(tokens):
    """生成表格行"""
    if not tokens:
        return '<tr><td colspan="7" style="text-align: center; padding: 30px;">暂无数据</td></tr>'
    
    rows = []
    
    for token in tokens:
        # 评分样式
        score_class = 'high' if token['score'] >= 80 else 'medium' if token['score'] >= 60 else 'low'
        
        # 评级样式
        rating_class = 'high' if '重点' in token['rating'] else 'medium' if '值得' in token['rating'] else 'low'
        
        # 增长率样式
        growth_class = 'negative' if token['growth_rate'] < 0 else ''
        
        # 市值格式化
        market_cap = token['market_cap']
        if market_cap >= 1000000:
            market_cap_str = f"${market_cap/1000000:.2f}M"
        elif market_cap >= 1000:
            market_cap_str = f"${market_cap/1000:.1f}K"
        else:
            market_cap_str = f"${market_cap:,.0f}"
        
        row = f"""
        <tr>
            <td><strong>#{token['rank']}</strong></td>
            <td><strong>{token['symbol']}</strong></td>
            <td>{market_cap_str}</td>
            <td class="growth {growth_class}">{token['growth_rate']:+.2f}%</td>
            <td class="score {score_class}">{token['score']}/100</td>
            <td><span class="rating {rating_class}">{token['rating']}</span></td>
            <td><span class="category-badge">{token['category']}</span></td>
        </tr>
        """
        
        rows.append(row)
    
    return '\n'.join(rows)

def main():
    """主函数"""
    print("📊 开始生成HTML报告...")
    
    # 创建docs目录
    docs_dir = Path(__file__).parent / 'docs'
    docs_dir.mkdir(exist_ok=True)
    
    # 提取数据
    tokens = extract_latest_report_from_readme()
    
    if not tokens:
        print("⚠️  未找到代币数据，生成空报告")
    else:
        print(f"✅ 找到 {len(tokens)} 个代币")
    
    # 生成HTML
    html_content = generate_html(tokens)
    
    # 保存HTML
    html_path = docs_dir / 'index.html'
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML报告已生成: {html_path}")
    print(f"📊 主流货币: {len([t for t in tokens if t['is_mainstream']])} 个")
    print(f"🎲 Meme币: {len([t for t in tokens if not t['is_mainstream']])} 个")

if __name__ == '__main__':
    main()
