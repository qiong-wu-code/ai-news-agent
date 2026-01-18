import requests
import json
import os
import time

def get_tenant_access_token():
    """获取飞书鉴权 Token (有效期 2 小时)"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {
        "app_id": os.getenv("FEISHU_APP_ID"),
        "app_secret": os.getenv("FEISHU_APP_SECRET")
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        return resp.json().get("tenant_access_token")
    except Exception as e:
        print(f"❌ 获取 Token 失败: {e}")
        return None

def create_feishu_doc(title, content):
    """
    1. 创建空文档
    2. 写入内容
    3. 返回文档链接
    """
    token = get_tenant_access_token()
    if not token:
        return "Token 获取失败，无法创建文档"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8"
    }

    # 1. 创建新文档 (New Docs 2.0 API)
    # 注意：这里需要在你的企业根目录下创建，或者指定 folder_token
    # 为了简单，我们直接创建在根目录
    create_url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    create_payload = {
        "folder_token": "FN0efIWC3lwZCdd7UcXcsArGnte", # 空字符串表示根目录
        "title": title
    }
    
    print("☁️ 正在创建飞书云文档...")
    resp = requests.post(create_url, headers=headers, json=create_payload)
    if resp.status_code != 200:
        print(f"❌ 创建失败: {resp.text}")
        return None
        
    doc_id = resp.json()['data']['document']['document_id']
    doc_url = f"https://feishu.cn/docx/{doc_id}" # 你的企业域名可能不一样，这是通用链接
    
    # 2. 写入内容
    # 飞书 Docs 2.0 写入比较复杂，需要把 Markdown 文本转成 Block 结构
    # 为了简化，我们只把整个 Report 作为一个大文本块写进去
    # 真正的 Markdown 渲染需要解析器，这里我们做一个简单的“纯文本”插入
    
    blocks_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"
    
    # 构造内容 Block
    # 这里的逻辑是：把所有内容作为一个 Text Block 插入
    block_payload = {
        "children": [
            {
                "block_type": 2,
                "text": {
                    "elements": [{"text_run": {"content": content}}]
                }
            }
        ],
        "index": -1 # -1 表示追加到末尾
    }
    
    print("📝 正在写入内容...")
    write_resp = requests.post(blocks_url, headers=headers, json=block_payload)
    
    if write_resp.status_code == 200:
        print(f"✅ 文档创建成功！链接如下：\n{doc_url}")
        return doc_url
    else:
        print(f"❌ 写入内容失败: {write_resp.text}")
        return doc_url
