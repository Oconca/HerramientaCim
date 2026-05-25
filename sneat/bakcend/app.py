from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/api/enviar", methods=["POST"])
def recibir():
    data = request.get_json()
    print("Datos recibidos:", data)
    # Aquí puedes guardar en una base de datos o archivo
    return jsonify({"message": "Datos recibidos correctamente"}), 200

if __name__ == "__main__":
    app.run(debug=True)
