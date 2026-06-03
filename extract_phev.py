import re
import os

base = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, 'all_interviews_raw.txt')

with open(src, encoding='utf-8') as f:
    text = f.read()

sections = re.split(r'={80}\n(.*?)\n={80}', text)
files = []
for i in range(1, len(sections)-1, 2):
    fname = sections[i].strip()
    content = sections[i+1].strip()
    files.append((fname, content))

out_lines = []
for fname, content in files:
    lines = content.split('\n')

    phev_kw = re.compile(
        r'PHEV|phev|plug.in hybrid|plug in hybrid|ปลั๊กอิน|ปลั๊ก.อิน|'
        r'PHEV Consideration|BYD PHEV|Unlocking Insight|'
        r'รถ PHEV|สนใจ PHEV|พิจารณา PHEV|เลือก PHEV|กังวล.*PHEV|PHEV.*กังวล|'
        r'two system|สองระบบ|ซ้ำซ้อน|ค่า maintenance.*สูง|maintenance.*ซ้ำซ้อน',
        re.IGNORECASE
    )

    seen = set()
    blocks = []
    for j, l in enumerate(lines):
        if phev_kw.search(l):
            start = max(0, j - 2)
            end = min(len(lines), j + 10)
            for k in range(start, end):
                if k not in seen:
                    seen.add(k)
                    blocks.append((k, lines[k]))

    if blocks:
        out_lines.append('\n' + '=' * 70)
        out_lines.append('FILE: ' + fname)
        out_lines.append('=' * 70)
        prev_k = -5
        for k, l in sorted(blocks):
            if k > prev_k + 1:
                out_lines.append('  ---')
            out_lines.append('  [' + str(k) + '] ' + l)
            prev_k = k

dst = os.path.join(base, 'phev_quotes_raw.txt')
with open(dst, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))
print('Saved', len(out_lines), 'lines to', dst)
