from flask import Flask, render_template, request
from carteira_core import rodar_modelo

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None

    if request.method == "POST":

        # =========================
        # CARTEIRA 
        # =========================
        carteira_raw = request.form["carteira"]
        carteira = {}

        for linha in carteira_raw.split("\n"):
            linha = linha.strip().replace(",", ":")

            if not linha or ":" not in linha:
                continue

            try:
                t, q = linha.split(":", 1)
                t = t.strip().upper()
                q = int(q.strip())
                carteira[t] = q
            except:
                continue

        # =========================
        # UNIVERSO
        # =========================
        universo = [
            t.strip().upper()
            for t in request.form["universo"].split("\n")
            if t.strip()
        ]

        # =========================
        # VIEWS 
        # =========================
        views_raw = request.form["views"]
        views = {}

        for linha in views_raw.split("\n"):
            linha = linha.strip().replace(",", ":")

            if not linha or ":" not in linha:
                continue

            try:
                t, v = linha.split(":", 1)
                t = t.strip().upper()
                v = float(v.strip())
                views[t] = v
            except:
                continue

        # =========================
        # MODELO
        # =========================
        try:
            resultado = rodar_modelo(carteira, universo, views)
        except Exception as e:
            resultado = {"Erro": str(e)}

    return render_template("index.html", resultado=resultado)


if __name__ == "__main__":
    app.run(debug=True)