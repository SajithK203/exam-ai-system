import os
import glob

found = False
for py_file in glob.glob('frontend/**/*.py', recursive=True):
    with open(py_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if 'use_container_width' in line:
                print(f'{py_file}:{i}: {line.strip()}')
                found = True

if not found:
    print('✓ No more use_container_width found')
