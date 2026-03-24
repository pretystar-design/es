import json
import sys

def generate_hcl(project):
    lines = []
    for node in project.get('nodes', []):
        res_type = node.get('type')
        res_id = node.get('id')
        lines.append(f'resource "{res_type}" "{res_id}" {{')
        for k, v in node.get('attributes', {}).items():
            lines.append(f'  {k} = "{v}"')
        lines.append('}')
        lines.append('')
    # Ensure the output ends with a newline
    return '\n'.join(lines) + '\n'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: generate_hcl.py <model.json>')
        sys.exit(1)
    with open(sys.argv[1], 'r') as f:
        proj = json.load(f)
    print(generate_hcl(proj))
