from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

# Señal en formato 'color,hora'
ultima_senal = "ninguna,00:00:00"

@app.route("/senal", methods=["GET"])
def get_senal():
    return jsonify({"senal": ultima_senal})

@app.route("/update/<color>/<hora>/<resul>", methods=["POST"])
def update_senal(color, hora,resul):
    global ultima_senal
    ultima_senal = f"{color},{hora},{resul}"
    print(f"📡 Señal actualizada a: {ultima_senal}")
    return jsonify({"mensaje": "Señal actualizada correctamente", "senal": ultima_senal}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
