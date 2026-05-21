def get_github_file():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    
    # إضافة هذا السطر للطباعة في Termux لتعرف أين المشكلة
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        raise Exception(f"خطأ: {response.status_code}")
        
    data = response.json()
    # ... باقي الكود
