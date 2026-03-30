import json
import sys

def generate_hcl(project):
    # Build dependency map: target -> list of sources
    dep_map = {}
    for edge in project.get('edges', []):
        # Treat every edge as a depends_on relationship
        target = edge.get('target')
        source = edge.get('source')
        if target and source:
            dep_map.setdefault(target, []).append(source)
    lines = []
    for node in project.get('nodes', []):
        res_type = node.get('type')
        res_id = node.get('id')
        lines.append(f'resource "{res_type}" "{res_id}" {{')
        for k, v in node.get('attributes', {}).items():
            lines.append(f'  {k} = "{v}"')
        # Add depends_on block if there are dependencies for this node
        if res_id in dep_map:
            deps = dep_map[res_id]
            dep_str = ', '.join(f'"{d}"' for d in deps)
            lines.append(f'  depends_on = [{dep_str}]')
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
