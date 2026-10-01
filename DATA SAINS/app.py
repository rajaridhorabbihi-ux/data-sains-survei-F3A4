
from flask import Flask, render_template, request, jsonify
from datasurvei import data_responden

app = Flask(__name__)

KOLOM = [
    ("id", "ID"),
    ("nama", "Nama Mahasiswa"),
    ("fakultas", "Fakultas"),
    ("makanan", "Makanan"),
    ("minuman", "Minuman"),
    ("pengeluaran", "Pengeluaran"),
]

RENTANG = [
    "Kurang dari Rp10.000",
    "Rp10.000 - Rp20.000",
    "Rp20.000 - Rp30.000",
    "Lebih dari Rp30.000"
]


def normalisasi_fakultas(f):
    f = (f or "").strip()

    if f.lower() in ("informatika", "fasilkom informatika"):
        return "Fakultas Ilmu Komputer"

    return f


def kategori_pengeluaran(p):
    p = str(p)

    if "Kurang" in p:
        return 0

    if "10.000" in p and "20.000" in p:
        return 1

    if "20.000" in p and "30.000" in p:
        return 2

    if "Lebih" in p:
        return 3

    return None


def persen(n, total):
    return round(n / total * 100, 1) if total else 0


@app.route("/")
def data_mahasiswa():
    sort_by = request.args.get("sort_by", "id")
    order = request.args.get("order", "asc")

    baris = [
        dict(
            r,
            fakultas=normalisasi_fakultas(r["fakultas"])
        )
        for r in data_responden
    ]

    if sort_by in dict(KOLOM):
        if sort_by == "id":
            key = lambda r: r["id"]
        else:
            key = lambda r: str(r[sort_by]).lower()

        baris.sort(
            key=key,
            reverse=(order == "desc")
        )

    return render_template(
        "index.html",
        halaman="data",
        data=baris,
        kolom=KOLOM,
        sort_by=sort_by,
        order=order
    )


@app.route("/visualisasi")
def visualisasi():
    return render_template(
        "visualisasi.html",
        halaman="visualisasi"
    )


@app.route("/api/stats")
def api_stats():
    total = len(data_responden)

    # ==========================================
    # 1. BAR CHART: RESPONDEN PER FAKULTAS
    # ==========================================

    fak = {}

    for r in data_responden:
        f = normalisasi_fakultas(r["fakultas"])
        fak[f] = fak.get(f, 0) + 1

    fak = sorted(
        fak.items(),
        key=lambda x: -x[1]
    )

    # ==========================================
    # 2. HISTOGRAM: RENTANG PENGELUARAN
    # ==========================================

    hitung = [0] * len(RENTANG)

    # ==========================================
    # 3. SCATTER: ID VS RENTANG PENGELUARAN
    # ==========================================

    scatter = [[] for _ in RENTANG]

    for r in data_responden:
        k = kategori_pengeluaran(r["pengeluaran"])

        if k is not None:
            hitung[k] += 1

            scatter[k].append({
                "x": r["id"],
                "y": k,
                "nama": r["nama"]
            })

    # ==========================================
    # KIRIM DATA KE FRONTEND
    # ==========================================

    return jsonify({
        "total": total,

        "bar": {
            "labels": [f for f, _ in fak],
            "counts": [n for _, n in fak],
            "pct": [persen(n, total) for _, n in fak]
        },

        "histogram": {
            "labels": RENTANG,
            "counts": hitung,
            "pct": [persen(n, total) for n in hitung]
        },

        "scatter": {
            "labels": RENTANG,
            "groups": scatter,
            "pct": [persen(n, total) for n in hitung]
        }
    })


# ==========================================
# JALANKAN FLASK
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)

