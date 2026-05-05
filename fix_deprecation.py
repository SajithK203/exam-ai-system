# Read the file with UTF-8 encoding
with open('frontend/pages/analysis.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace use_container_width=True with width='stretch'
content = content.replace("use_container_width=True", "width='stretch'")

# Replace use_container_width=False with width='content'
content = content.replace("use_container_width=False", "width='content'")

# Write back with UTF-8 encoding
with open('frontend/pages/analysis.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Replaced all use_container_width parameters')
