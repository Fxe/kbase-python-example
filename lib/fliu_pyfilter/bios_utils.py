import json

def read_json(filename):
    data = None
    with open(filename, 'r') as f:
        data = json.loads(f.read())
    return data

def write_json(data, filename):
    with open(filename, 'w') as f:
        f.write(json.dumps(data))