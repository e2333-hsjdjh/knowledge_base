import os
from pypdf import PdfReader

base_path = "/Users/zzzzzz/Documents/个人文件/课件/传播理论"
files = [
    "第一周 课程介绍+绪论.pdf",
    "第二周 社会科学理论评价.pdf",
    "第三周 人与自我.pdf",
    "第五周 人与他人.pdf",
    "第六周 人与组织.pdf",
    "第七周 人与讯息.pdf",
    "第八九周 媒体与效果.pdf"
]

for filename in files:
    file_path = os.path.join(base_path, filename)
    if not os.path.exists(file_path):
        print(f"File not found: {filename}")
        continue
        
    print(f"\n--- START OF {filename} ---\n")
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                print(text)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    print(f"\n--- END OF {filename} ---\n")
