import os
from flask import Flask, send_file,render_template, Response,request,abort
from backend.conexiondb import get_connection
from flask import jsonify
import subprocess


logs = []


app = Flask(__name__)

API_KEY = "ua2026"

RUTAS_PROTEGIDAS = ["/stream", "/proceso", "/ejecutar"]

@app.before_request
def autenticar():
    print(request.path)   # para depurar

    if request.path in RUTAS_PROTEGIDAS:
        if request.args.get("key") != API_KEY:
            abort(401)


script_dir = os.path.dirname(os.path.abspath(__file__))

ruta_mapa = os.path.join(
    script_dir,
    'frontend',
    'mapa.html'
)


@app.route("/stream")
def stream():

    def ejecutar(nombre, script):

        yield f"data: === {nombre} ===\n\n"

        proceso = subprocess.Popen(
            ["python3", "-u", script],      # salida sin buffer
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        try:
            for linea in iter(proceso.stdout.readline, ''):
                if linea:
                    yield f"data: {linea.rstrip()}\n\n"

            codigo = proceso.wait()

            if codigo != 0:
                yield f"data: ERROR: {script} terminó con código {codigo}\n\n"

        except Exception as e:
            yield f"data: ERROR: {e}\n\n"

    def generar_logs():

        yield from ejecutar("Generar raw", "backend/genera_raw.py")

        yield from ejecutar("Procesador IA", "backend/procesador_ia.py")

        yield from ejecutar("DB Injector", "backend/db_injector.py")

        yield "data: === Pipeline finalizado ===\n\n"

    return Response(
        generar_logs(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"   # evita buffering en nginx
        }
    )


@app.route('/')
def mostrar_mapa():
    if not os.path.exists(ruta_mapa):
        return "El mapa aún no ha sido generado. Por favor, ejecuta el pipeline primero."
    return send_file(ruta_mapa)

@app.route('/ejecutar')
def ejecutar():
    #ejecutar_pipeline()
    return "Pipeline ejecutado. El mapa se ha actualizado."


@app.route("/proceso")
def index():
    return render_template("admin.html")



@app.route("/api/delitos")
def delitos():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            tipo_delito,
            resumen_breve,
            ST_Y(geom) AS lat,
            ST_X(geom) AS lng,
            ciudad,
            url_fuente,
            fecha_evento,
            SUBSTRING(url_fuente FROM 'https?://(?:www\.)?([^.]+)') AS fuente
        FROM delitos
        WHERE geom IS NOT NULL
    """)

    rows = cur.fetchall()

    data = []

    for row in rows:
        data.append({
            "tipo": row.get("tipo_delito"),
            "resumen": row.get("resumen_breve"),
            "lat": row.get("lat"),
            "lng": row.get("lng"),
            "ciudad": row.get("ciudad"),
            "fecha": row.get("fecha_evento").isoformat() if row.get("fecha_evento") else None,
            "fuente": row.get("fuente"),
            "url": row.get("url_fuente")
        })

    cur.close()
    conn.close()

    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
