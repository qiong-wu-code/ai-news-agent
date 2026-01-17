import os
import json
import requests
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 配置 LLM
client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)

def fetch_huggingface_papers(limit=7):
    """获取 Hugging Face 每日热门论文"""
    print(f"📡 [1/3] 正在连接 Hugging Face 获取最新论文...")
    url = "https://huggingface.co/api/daily_papers"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        papers = []
        for item in data[:limit]:
            title = item['paper']['title']
            summary = item['paper'].get('summary', '暂无摘要')[:300].replace('\n', ' ')
            link = f"https://huggingface.co/papers/{item['paper']['id']}"
            papers.append(f"📄 论文: {title}\n   摘要: {summary}...\n   链接: {link}")
            
        print(f"   ✅ 获取到 {len(papers)} 篇热门论文")
        return "\n\n".join(papers)
    except Exception as e:
        print(f"   ❌ Hugging Face 获取失败: {e}")
        return "无法获取论文数据。"

def get_hn_item(item_id):
    """获取单条 HN 新闻详情"""
    try:
        url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        return requests.get(url, timeout=5).json()
    except:
        return None

def fetch_hacker_news(limit=20):
    """并发获取 Hacker News 热门新闻"""
    print(f"📡 [2/3] 正在扫描 Hacker News 科技热点...")
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    
    try:
        # 1. 获取前 N 个 ID
        ids = requests.get(top_stories_url, timeout=10).json()[:limit]
        
        news_items = []
        # 2. 并发下载详情（速度更快）
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(get_hn_item, ids)
            
        for item in results:
            if item and 'title' in item and 'url' in item:
                news_items.append(f"📰 新闻: {item['title']}\n   链接: {item['url']}")
        
        print(f"   ✅ 成功抓取 {len(news_items)} 条热门科技新闻")
        return "\n\n".join(news_items)
    except Exception as e:
        print(f"   ❌ Hacker News 获取失败: {e}")
        return "无法获取新闻数据。"

def generate_report(hn_data, paper_data):
    """调用 LLM 生成中文日报"""
    print(f"🧠 [3/3] 正在调用 AI 进行深度总结与翻译...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    prompt = f"""
    你是一个专业的科技主编。请根据以下两条数据源，生成一份 markdown 格式的《AI & Tech 每日简报》。
    
    日期: {today}

    【数据源 1：Hugging Face 热门论文】
    {paper_data}

    【数据源 2：Hacker News 科技热点】
    {hn_data}

    ---
    你的任务：
    1. 【核心论文】：从论文数据中挑选 3-5 篇最重要的，用中文简要介绍其核心创新点。
    2. 【科技热点】：从 Hacker News 中挑选 5 条最值得关注的新闻（尤其是与 AI、开发工具相关的），用中文一句话概括。
    3. 格式要求：使用 Markdown，要有 Emoji 点缀，排版美观，重点加粗。
    4. 必须包含原文链接。
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat", # 如果是用 OpenAI，这里改 gpt-4o-mini 或 gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful tech assistant."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM 生成失败: {e}"

def main():
    start_time = datetime.now()
    
    # 1. 获取数据
    paper_data = fetch_huggingface_papers()
    hn_data = fetch_hacker_news()
    
    # 2. 生成报告
    report = generate_report(hn_data, paper_data)
    
    # 3. 保存文件
    filename = f"AI_Brief_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"\n✅ 任务完成！耗时: {datetime.now() - start_time}")
    print(f"📁 简报已保存为: {filename}")
    print("-" * 30)
    print("你可以双击左侧文件列表中的 .md 文件查看预览")

if __name__ == "__main__":
    main()
