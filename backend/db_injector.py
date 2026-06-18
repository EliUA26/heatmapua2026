import json
import psycopg2
import os
from conexiondb import get_connection

def inyectar_datos():

    conn = get_connection()
  
    cur = conn.cursor()

    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(BASE_DIR)  # usually .../CrimeHeatUA/backend

        # posibles ubicaciones del archivo JSON (buscar la que exista)
        candidates = [
            os.path.join(project_root, 'data', 'noticias_mapeadas.json'),
            os.path.join(BASE_DIR, 'data', 'noticias_mapeadas.json'),
            os.path.join(project_root, 'proyecto_heatmapp', 'data', 'noticias_mapeadas.json'),
        ]

        path = next((p for p in candidates if os.path.exists(p)), candidates[0])

        print(f"Leyendo JSON desde: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        print(f"Subiendo {len(datos)} registros a la base de datos...")

        for item in datos:
            cur.execute("""
                INSERT INTO delitos (tipo_delito, fecha_evento, gravedad, ubicacion_texto, barrio, ciudad, resumen_breve, geom, url_fuente)
                VALUES (%s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
                ON CONFLICT (url_fuente) DO NOTHING;
            """, (
                item['tipo_delito'], item['fecha_evento'], item['gravedad'],
                item['ubicacion_texto'], item['barrio'], item['ciudad'],
                item['resumen_breve'], item['lng'], item['lat'], item['url_fuente']
            ))

        conn.commit()
        print(" Inyección completada exitosamente.")
    except Exception as e:
        print(f"Error al inyectar datos: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    inyectar_datos()