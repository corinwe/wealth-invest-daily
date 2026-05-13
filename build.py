#!/usr/bin/env python3
"""Build static HTML pages for 九九财富投资晨报."""
import os
import re
import json
import glob

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(SITE_DIR, 'reports')
INDEX_TPL = os.path.join(SITE_DIR, 'index.template.html')
INDEX_OUT = os.path.join(SITE_DIR, 'index.html')
REPORT_TPL = os.path.join(SITE_DIR, 'report.template.html')
REPORT_OUT = os.path.join(SITE_DIR, 'report.html')
PLACEHOLDER = 'REPORTS_JSON_PLACEHOLDER'


def extract_metadata(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return None

    meta = {
        'date': '',
        'file': os.path.basename(filepath),
        'summary': '',
        'sections': [],
        'word_count': 0,
    }

    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', meta['file'])
    if date_match:
        meta['date'] = date_match.group(1)

    text_only = re.sub(r'[#*`\[\]|>]', '', content)
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', text_only))
    en_words = len(re.findall(r'[a-zA-Z]+', text_only))
    meta['word_count'] = cn_chars + en_words

    for m in re.finditer(r'^## ([^\n]+)', content, re.MULTILINE):
        title = m.group(1).strip()
        title = re.sub(r'\*\*', '', title)
        anchor = re.sub(r'[^\w\u4e00-\u9fff]+', '-', title).lower().strip('-')
        meta['sections'].append({'title': title, 'anchor': anchor})

    conclusion_match = re.search(
        r'>\s*(.+?)(?:\n\n|\n[^>]|\Z)', content, re.DOTALL
    )
    if conclusion_match:
        summary = conclusion_match.group(1).strip()
        summary = re.sub(r'\n', ' ', summary)
        summary = re.sub(r'\s+', ' ', summary)
        meta['summary'] = summary[:200]

    if not meta['summary']:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('##') and i > 0:
                para_lines = []
                for j in range(1, i):
                    l = lines[j].strip()
                    if l and not l.startswith('#') and not l.startswith('---'):
                        para_lines.append(l)
                    if len(para_lines) >= 2:
                        break
                if para_lines:
                    meta['summary'] = ' '.join(para_lines)[:200]
                break

    return meta


def scan_reports():
    reports = []
    for filepath in sorted(glob.glob(os.path.join(REPORTS_DIR, '*.md')), reverse=True):
        meta = extract_metadata(filepath)
        if meta and meta['date']:
            reports.append(meta)
    return reports


def build(template_path, output_path, reports_json):
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    html = html.replace(PLACEHOLDER, reports_json)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Built {os.path.basename(output_path)} with placeholder injected")


def main():
    reports = scan_reports()
    reports_json = json.dumps(reports, ensure_ascii=False, indent=2)

    for tpl, out in [(INDEX_TPL, INDEX_OUT), (REPORT_TPL, REPORT_OUT)]:
        if not os.path.exists(tpl):
            print(f"⚠️ Template not found: {tpl}")
            continue
        build(tpl, out, reports_json)

    for r in reports:
        secs = ', '.join(s['title'] for s in r['sections'])
        print(f"   {r['date']} | {r['word_count']}字 | {secs}")


if __name__ == '__main__':
    main()
