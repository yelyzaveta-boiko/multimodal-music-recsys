from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from recommendation import random_songs, save_ratings, recommendations

load_dotenv()

app = Flask(__name__, template_folder="../frontend/templates",
            static_folder="../frontend/static")
CORS(app)

@app.route("/")
def root():
    return render_template("index.html")


@app.route("/api/random-songs", methods=["GET"])
def api_random():
    return jsonify(random_songs())


@app.route("/api/save-ratings", methods=["POST"])
def api_save():
    body = request.get_json(force=True)
    save_ratings(body.get("ratings", []))
    return jsonify({"msg": "ratings stored"})


@app.route("/api/recommendations", methods=["POST"])
def api_recs():
    body  = request.get_json(force=True)
    model = body.get("model", "lda_coh")
    k = int(body.get("k", 5))
    return jsonify(recommendations(k=k, model_name=model))

if __name__ == "__main__":
    app.run(debug=True)
