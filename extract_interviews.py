import docx
import os
import glob

def read_docx(path):
    doc = docx.Document(path)
    return '\n'.join(p.text for p in doc.paragraphs if p.text.strip())

base = os.path.dirname(os.path.abspath(__file__))
result = {}
for folder in ['interviews', 'interviews_2']:
    files = sorted(glob.glob(os.path.join(base, folder, '*.docx')))
    for f in files:
        name = os.path.basename(f)
        result[f'{folder}/{name}'] = read_docx(f)

total = sum(len(v) for v in result.values())
print(f'Files: {len(result)}, Total chars: {total}')

out = os.path.join(base, 'all_interviews_raw.txt')
with open(out, 'w', encoding='utf-8') as fh:
    for fname, text in result.items():
        fh.write('\n' + '='*80 + '\n')
        fh.write(fname + '\n')
        fh.write('='*80 + '\n')
        fh.write(text + '\n')
print('Saved to', out)
