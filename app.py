from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

DATA_FILE = 'whitelist_keys.json'

def load_keys():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_keys(keys):
    with open(DATA_FILE, 'w') as f:
        json.dump(keys, f)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/keys', methods=['GET'])
def get_keys():
    return jsonify(load_keys())

@app.route('/api/keys', methods=['POST'])
def add_key():
    keys = load_keys()
    data = request.json
    keys.append(data)
    save_keys(keys)
    return jsonify({'success': True})

@app.route('/api/keys/<int:index>', methods=['PUT'])
def update_key(index):
    keys = load_keys()
    data = request.json
    if 0 <= index < len(keys):
        keys[index].update(data)
        save_keys(keys)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid index'}), 400

@app.route('/api/keys/delete', methods=['DELETE'])
def delete_keys():
    try:
        print("\n=== Delete Request Start ===")
        keys = load_keys()
        print(f"Loaded keys: {json.dumps(keys, indent=2)}")
        
        data = request.get_json()
        print(f"Received data: {json.dumps(data, indent=2)}")
        
        if not data or 'keysToDelete' not in data:
            print("Error: Missing keysToDelete in request")
            return jsonify({'error': 'Missing keysToDelete in request'}), 400

        keys_to_delete = data['keysToDelete']
        print(f"Keys to delete: {keys_to_delete}")
        
        # More explicit deletion logic
        original_keys = len(keys)
        new_keys = []
        for k in keys:
            if k['key'] not in keys_to_delete:
                new_keys.append(k)
            else:
                print(f"Deleting key: {k['key']}")
        
        print(f"Keys remaining: {json.dumps(new_keys, indent=2)}")
        
        if len(new_keys) == original_keys:
            print("Warning: No keys were deleted")
        else:
            print(f"Deleted {original_keys - len(new_keys)} keys")
            save_keys(new_keys)
        
        print("=== Delete Request End ===\n")
        return jsonify(new_keys)

    except Exception as e:
        print(f"Error in delete_keys: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_key():
    data = request.json
    key = data.get('key')
    hwid = data.get('hwid')
    executor = data.get('executor')
    keys = load_keys()
    for k in keys:
        if k.get('key') == key:
            # Update HWID and executor if not set
            if k.get('hwid') == '':
                k['hwid'] = hwid
                k['executor'] = executor
                save_keys(keys)
            if k.get('hwid') == hwid:
                return jsonify({'valid': True, 'hwid_match': True})
            else:
                return jsonify({'valid': True, 'hwid_match': False})
    return jsonify({'valid': False, 'hwid_match': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)