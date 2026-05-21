def get_github_file():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"خطأ في الاتصال: {response.status_code} - تأكد من اسم المستودع والملف")
        
    data = response.json()
    if 'content' not in data:
        raise Exception("الملف فارغ أو غير موجود")
        
    content = base64.b64decode(data['content']).decode('utf-8')
    return content, data['sha']
