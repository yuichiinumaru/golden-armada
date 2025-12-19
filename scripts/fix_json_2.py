import json
try:
    with open('codeswarm/prompts/kb/kb_synergy_files_extractor.json', 'r') as f:
        content = f.read()
    dec = json.JSONDecoder()
    obj, idx = dec.raw_decode(content)
    print(f'Successfully decoded until index {idx}')

    with open('codeswarm/prompts/kb/kb_synergy_files_extractor.json', 'w') as f:
        json.dump(obj, f, indent=2)
    print('Fixed file.')
except Exception as e:
    print(f'Error fixing: {e}')
