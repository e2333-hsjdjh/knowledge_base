#!/usr/bin/env python3
"""从原始文件 `大一上法外.txt` 提取法语与中文，生成：
 - 大一上法外_vocab.csv  (fr,zh)
 - 大一上法外_quiz.txt  (法译中 / 中译法 随机题)
 - 大一上法外_zh_only.txt (仅中文版，保留章节信息)

规则：
 - 以每行处理：把首个中文字符出现处作为分隔点，左侧为法语部分，右侧为中文部分。
 - 法语部分按逗号分割为多个词条，各生成独立 CSV 行，中文部分复用。
 - 忽略空行与纯注释行。
"""
import re
from pathlib import Path
import csv
import random

ROOT = Path(__file__).parent
SRC = ROOT / '大一上法外.txt'
CSV_OUT = ROOT / '大一上法外_vocab.csv'
QUIZ_OUT = ROOT / '大一上法外_quiz.txt'
ZH_ONLY = ROOT / '大一上法外_zh_only.txt'

# 匹配中文字符的简单正则
chinese_re = re.compile(r'[\u4e00-\u9fff]')
seq_re = re.compile(r'S[eé]quence\s*(\d+)', re.IGNORECASE)

entries = []  # list of (fr, zh)
zh_lines = []

if not SRC.exists():
    print('Source file not found:', SRC)
    raise SystemExit(1)

text = SRC.read_text(encoding='utf-8')
for raw_line in text.splitlines():
    line = raw_line.strip()
    if not line:
        zh_lines.append('')
        continue
    # keep section headings as Chinese '章节 N' in zh_only if matched
    seqm = seq_re.search(line)
    if seqm:
        zh_lines.append(f'章节 {seqm.group(1)}')
    # find first chinese char
    m = chinese_re.search(line)
    if m:
        idx = m.start()
        left = line[:idx].strip()
        right = line[idx:].strip()
        # left may contain french tokens separated by comma or tabs
        # split by comma or / or whitespace when comma absent
        if left:
            parts = re.split(r'[,/]', left)
            for p in parts:
                p = p.strip()
                if p:
                    entries.append((p, right))
        else:
            # no french part, maybe pure chinese line
            # but still append zh_only line
            pass
        zh_lines.append(right)
    else:
        # no chinese char found; assume pure French or heading - keep French in CSV with empty zh
        # but for zh_only we skip these or keep as-is? We'll keep the French line removed in zh_only
        # Add CSV entries with empty zh to allow later filling
        parts = re.split(r'[,/]', line)
        for p in parts:
            p = p.strip()
            if p:
                entries.append((p, ''))
        # do not add French-only line to zh_only

# write CSV
with CSV_OUT.open('w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['fr', 'zh'])
    for fr, zh in entries:
        writer.writerow([fr, zh])
print('Wrote', CSV_OUT)

# generate quiz: select pairs that have both fr and zh
pairs = [e for e in entries if e[0] and e[1]]
if not pairs:
    print('No bilingual pairs found to make quiz.')
else:
    # prepare 40 questions (or less if not enough)
    num = min(40, len(pairs))
    selected = random.sample(pairs, num)
    lines = []
    # half french->chinese, half chinese->french

    import re
    from pathlib import Path
    import csv
    import random

    def extract_vocab_pairs(lines):
        pairs = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 跳过章节、纯中文、纯法语、无法分割的行
            # 以第一个中文字符为分界，前面为法语，后面为中文
            match = re.search(r'[\u4e00-\u9fff]', line)
            if match:
                idx = match.start()
                fr = line[:idx].strip('：:，,、. 1234567890')
                zh = line[idx:].strip()
                # 法语部分不能全是中文，中文部分不能全是法语
                if fr and zh and not re.search(r'[\u4e00-\u9fff]', fr) and re.search(r'[\u4e00-\u9fff]', zh):
                    pairs.append((fr, zh))
        return pairs

    def main():
        src = Path('大一上法外.txt')
        lines = src.read_text(encoding='utf-8').splitlines()
        pairs = extract_vocab_pairs(lines)

        # 生成csv
        with open('大一上法外_vocab.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['法语', '中文'])
            writer.writerows(pairs)

        # 生成quiz（法语->中文，乱序）
        quiz = pairs.copy()
        random.shuffle(quiz)
        with open('大一上法外_quiz.txt', 'w', encoding='utf-8') as f:
            for i, (fr, zh) in enumerate(quiz, 1):
                f.write(f'{i}. {fr}\n')
                f.write('答：\n')
                f.write(f'正确答案：{zh}\n\n')

    if __name__ == '__main__':
        main()
