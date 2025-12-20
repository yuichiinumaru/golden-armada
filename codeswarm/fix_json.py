import json
try:
    with open('codeswarm/prompts/kb/kb_framework_problem_solving.json', 'r') as f:
        content = f.read()
    # The content seems valid JSON until char 101374. Let's slice it there.
    # The traceback said: Extra data: line 1339 column 1 (char 101374)
    # This means after the last closing brace '}', there is more data (probably a newline and then more braces or text).
    # Since I verified the end of the file looked like a closing brace, maybe there's invisible trash.
    # I'll rely on the decoder to tell me where the valid JSON ends.
    dec = json.JSONDecoder()
    obj, idx = dec.raw_decode(content)
    print(f'Successfully decoded until index {idx}')

    # Write back the clean object
    with open('codeswarm/prompts/kb/kb_framework_problem_solving.json', 'w') as f:
        json.dump(obj, f, indent=2)
    print('Fixed file.')
except Exception as e:
    print(e)
