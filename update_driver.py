import requests
import os

API_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

def get_stable_chromedriver_data():
    url_path = []
    try:
        response = requests.get(API_URL)
        data = response.json()
        
        stable_channel = data['channels']['Stable']
        version = stable_channel['version']
        downloads = stable_channel['downloads']['chromedriver']
        
        for item in downloads:
            url_path.append(item['url'])
            
        if version and url_path:
            print(f"检测到版本: {version}, 获取到 {len(url_path)} 个下载地址")
            return (version, url_path)
    except Exception as e:
        print(f"获取数据失败: {e}")
    return None

def update_readme(version):
    """在 README.md 的顶部（标题下方）插入新版本，保留旧版本"""
    header_text = "# chromedriver"
    
    # 1. 准备新版本的内容块
    new_entry = f"""
## chrome {version} 版本 webdriver 下载 （chrome driver {version} download）

* [chromedriver win32](./{version}%20chromedriver-win32.zip)
* [chromedriver win64](./{version}%20chromedriver-win64.zip)
* [chromedriver linux64](./{version}%20chromedriver-linux64.zip)
* [chromedriver mac-arm64](./{version}%20chromedriver-mac-arm64.zip)
* [chromedriver mac-x64](./{version}%20chromedriver-mac-x64.zip)

---"""

    # 2. 读取现有内容
    old_content = ""
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            old_content = f.read().strip()

    # 3. 逻辑判断：如果文件为空或标题不存在
    if header_text not in old_content:
        # 初始状态：标题 + 新内容
        final_content = f"{header_text}\n{new_entry}"
    else:
        # 核心逻辑：在标题行之后插入新内容，保留后面的旧内容
        # 找到标题所在的行尾位置
        header_end_index = old_content.find(header_text) + len(header_text)
        
        # 拼接：标题 + 新条目 + 之前的全部内容
        # old_content[header_end_index:] 是原来标题之后的所有历史版本
        final_content = old_content[:header_end_index] + "\n" + new_entry + old_content[header_end_index:]

    # 4. 写回文件
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(final_content)

def main():
    data = get_stable_chromedriver_data()
    if not data:
        return

    version, urls = data
    version_file = "version.txt"
    
    # 1. 比较版本
    current_version = ""
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            current_version = f.read().strip()

    if version == current_version:
        print("版本未更新，执行结束。")
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
                print("updated=false", file=fh)
        return

    # 2. 版本不一致，开始下载
    print(f"版本从 {current_version} 更新至 {version}，开始下载文件...")
    for url in urls:
        raw_name = url.split('/')[-1] # 例如 chromedriver-win64.zip
        new_name = f"{version} {raw_name}"
        
        print(f"正在下载: {new_name}")
        resp = requests.get(url)
        with open(new_name, "wb") as f:
            f.write(resp.content)

    # 3. 更新版本记录
    with open(version_file, "w") as f:
        f.write(version)

    # 4. 更新 README
    update_readme(version)

    # 5. 输出给 GitHub Actions
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print("updated=true", file=fh)
            print(f"version={version}", file=fh)

if __name__ == "__main__":
    main()



