# import g4f
# import json
# import os
# import time
# from geopy.geocoders import Nominatim
# from geopy.exc import GeocoderTimedOut

# # Inicializamos el geolocalizador
# geolocator = Nominatim(user_agent="crime_heatmap_asuncion_v2")

# def geolocalizar_con_ia(lugar, barrio, ciudad, resumen):
#     """Fallback: Usa IA para obtener coordenadas cuando Nominatim falla."""
#     prompt = (
#         f"Eres un experto en geografía de Paraguay, específicamente en Asunción. "
#         f"Se te pide que extraigas las coordenadas de latitud y longitud para: "
#         f"Lugar: {lugar}, Barrio: {barrio}, Ciudad: {ciudad}, Paraguay. "
#         f"Utiliza el resumen del incidente para mejorar la precisión de la ubicación: {resumen}\n"
#         f"Responde ÚNICAMENTE con un JSON:\n"
#         f"{{\n"
#         f'  "latitude": <número>,\n'
#         f'  "longitude": <número>\n'
#         f"}}\n"
#         f"Si no puedes determinar la ubicación exacta, usa las coordenadas del centro de Asunción: "
#         f"{{\n"
#         f'  "latitude": -25.2822,\n'
#         f'  "longitude": -57.6359\n'
#         f"}}"
#     )
    
#     modelos = ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo", "claude-3-opus", "claude-3-sonnet", "llama-3-70b", "mixtral-8x7b"]
    
#     for modelo in modelos:
#         try:
#             response = g4f.ChatCompletion.create(
#                 model=modelo,
#                 messages=[{"role": "user", "content": prompt}],
#             )
            
#             # Limpieza de markdown
#             if "```json" in response:
#                 response = response.split("```json")[1].split("```")[0].strip()
#             elif "```" in response:
#                 response = response.split("```")[1].split("```")[0].strip()
            
#             coords = json.loads(response)
#             lat = float(coords.get("latitude", -25.2822))
#             lng = float(coords.get("longitude", -57.6359))
#             return lat, lng
#         except Exception as e:
#             print(f"    ⚠️  Error IA con modelo {modelo}: {str(e)}")
#             continue
    
#     # Si todas las IA fallan, retorna fallback
#     return -25.2822, -57.6359


# def geolocalizar(lugar, barrio, ciudad, resumen):
#     """Convierte texto en coordenadas Lat/Lng para PostGIS."""
#     try:
#         # Intentamos una búsqueda específica: Lugar + Barrio + Ciudad
#         query = f"{lugar}, {barrio}, {ciudad}, Paraguay"
#         print(f"  Geolocalizando con Nominatim: {query}...")
#         location = geolocator.geocode(query, timeout=10)
        
#         if not location and barrio:
#             # Si falla, intentamos solo Barrio + Ciudad
#             query = f"{barrio}, {ciudad}, Paraguay"
#             location = geolocator.geocode(query, timeout=10)
            
#         if location:
#             return location.latitude, location.longitude
        
#         # Si Nominatim falla, usamos IA como fallback
#         print(f"   ⚠️  Nominatim falló, intentando con IA...")
#         return geolocalizar_con_ia(lugar, barrio, ciudad, resumen)
        
#     except Exception as e:
#         print(f"   ⚠️  Error en geolocalización: {str(e)}, usando IA...")
#         # Si hay excepción, también usamos IA como fallback
#         return geolocalizar_con_ia(lugar, barrio, ciudad, resumen)








# def procesar_con_ia(texto_noticia):
#     """Usa IA para extraer datos estructurados segun nuestro esquema SQL."""
    
#     prompt = (
#             "Actúa como un analista de seguridad ciudadana en Paraguay. "
#             "Extrae la información de la noticia y responde ÚNICAMENTE con un objeto JSON puro. "
#             "REGLAS CRÍTICAS DE FORMATO:\n"
#             "1. CATEGORÍAS DE DELITO: Solo usa [ASALTO, ROBO, MOTOCHORRO, HOMICIDIO, ACCIDENTE].\n"
#             "2. FECHA: Usa SIEMPRE formato 'YYYY-MM-DD'. Si la noticia no menciona una fecha específica, "
#             f"usa la fecha de hoy: 2026-04-25. NUNCA uses palabras como 'ayer' o 'lunes'.\n"
#             "3. GRAVEDAD: Un número entero del 1 al 10.\n"
#             "\n"
#             "Formato JSON requerido:\n"
#             "{\n"
#             "  \"tipo_delito\": \"\",\n"
#             "  \"fecha_evento\": \"\",\n"
#             "  \"gravedad\": ,\n"
#             "  \"ubicacion_texto\": \"\",\n"
#             "  \"barrio\": \"\",\n"
#             "  \"ciudad\": \"\",\n"
#             "  \"resumen\": \"\"\n"
#             "}\n"
#             f"Noticia a procesar: {texto_noticia[:800]}"
#         )

#     modelos = [ "gpt-4o-mini",
#     "gpt-4o",
#     "gpt-4",
#     "gpt-3.5-turbo",
#     "claude-3-opus",
#     "claude-3-sonnet",
#     "llama-3-70b",
#     "mixtral-8x7b"]
    
#     for modelo in modelos:
#         try:
#             response = g4f.ChatCompletion.create(
#                 model=modelo,
#                 messages=[{"role": "user", "content": prompt}],
#             )
            
#             # Limpieza de markdown si la IA lo agrega
#             if "```json" in response:
#                 response = response.split("```json")[1].split("```")[0].strip()
#             elif "```" in response:
#                 response = response.split("```")[1].strip()

#             return json.loads(response)
#         except Exception as e:
#             print(f"    Error con modelo {modelo}, probando el siguiente...")
#             continue
#     return None

# def principal():
#     # Usar rutas absolutas basadas en la ubicación del script
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     entrada = os.path.join(script_dir, '..', 'data', 'noticias_raw.json')
#     salida = os.path.join(script_dir, '..', 'data', 'noticias_mapeadas.json')

#     if not os.path.exists(entrada):
#         print(f"No existe el archivo de entrada: {entrada}")
#         return

#     with open(entrada, 'r', encoding='utf-8') as f:
#         noticias = json.load(f)

#     print(f"🚀 PROCESANDO {len(noticias)} NOTICIAS PARA LA DB SQL...")
#     resultados = []

#     for i, n in enumerate(noticias):
#         print(f"[{i+1}/{len(noticias)}] Analizando: {n['titulo'][:50]}...")
        
#         datos_ia = procesar_con_ia(n['texto'])
        
#         if datos_ia:
#             # Agregamos coordenadas para nuestra columna 'geom' de PostGIS
#             lat, lng = geolocalizar(datos_ia['ubicacion_texto'], datos_ia['barrio'], datos_ia['ciudad'],datos_ia['resumen'])
            
#             # Formateamos el objeto final para que el Scraper lo suba directo a SQL
#             registro = {
#                 "url_fuente": n['url'],
#                 "tipo_delito": datos_ia['tipo_delito'].upper(),
#                 "fecha_evento": datos_ia['fecha_evento'],
#                 "gravedad": datos_ia['gravedad'],
#                 "ubicacion_texto": datos_ia['ubicacion_texto'],
#                 "barrio": datos_ia['barrio'],
#                 "ciudad": datos_ia['ciudad'],
#                 "resumen_breve": datos_ia['resumen'],
#                 "lat": lat,
#                 "lng": lng
#             }
#             resultados.append(registro)
#             print(f"   ✅ Estructurado y Geolocalizado en: {lat}, {lng}")
        
#         time.sleep(1) # Evitar bloqueos de API

#     with open(salida, 'w', encoding='utf-8') as f:
#         json.dump(resultados, f, ensure_ascii=False, indent=4)
    
#     print(f"\n✨ PROCESO COMPLETADO. Datos listos para inyectar en SQL.")

# if __name__ == "__main__":
#     principal()

# from datetime import datetime
# fecha_hoy = datetime.now().strftime('%Y-%m-%d')

# # Y en el prompt cambias el texto fijo por la variable:
# # f"usa la fecha de hoy: {fecha_hoy}. NUNCA uses..."

import g4f
import json
import os
import time
from geopy.geocoders import Nominatim
from datetime import datetime

# Inicializamos el geolocalizador para convertir texto en coordenadas
geolocator = Nominatim(user_agent="crime_heatmap_py_v2")

def geolocalizar(lugar, barrio, ciudad):
    """Obtiene lat/lng para que el mapa de calor funcione."""
    try:
        query = f"{lugar}, {barrio}, {ciudad}, Paraguay"
        location = geolocator.geocode(query, timeout=10)
        if not location and barrio:
            location = geolocator.geocode(f"{barrio}, {ciudad}, Paraguay", timeout=10)
        
        if location:
            return location.latitude, location.longitude
    except:
        pass
    # Coordenadas por defecto (Centro de Asunción) si falla la búsqueda
    return -25.2822, -57.6359

def principal():
    # Usamos rutas absolutas para evitar errores en el Pipeline
    script_dir = os.path.dirname(os.path.abspath(__file__))
    entrada = os.path.join(script_dir, '..', 'data', 'noticias_raw.json')
    salida = os.path.join(script_dir, '..', 'data', 'noticias_mapeadas.json')

    fecha_hoy = datetime.now().strftime('%Y-%m-%d')

    # Verificar existencia del archivo de entrada
    if not os.path.exists(entrada):
        print(f" No se encontró el archivo: {entrada}")
        return

    with open(entrada, 'r', encoding='utf-8') as f:
        noticias = json.load(f)

    print(f" INICIANDO PROCESAMIENTO INTELIGENTE")
    print(f"Se analizarán {len(noticias)} noticias.\n")
    
    resultados = []
    
    for i, n in enumerate(noticias):
        print(f"[{i+1}/{len(noticias)}] Analizando: {n['titulo'][:45]}...")
        
        # Prompt optimizado para recibir JSON puro
        # IMPORTANTE: Pedimos los campos exactos que usa db_injector.py
        prompt = (
            f"Actúa como un analista de seguridad. Extrae la información de la noticia "
            f"y responde ÚNICAMENTE con un objeto JSON (sin texto extra) con este formato: "
            f"{{\"tipo_delito\": \"ASALTO/ROBO/HOMICIDIO/MOTOCHORRO\", "
            f"\"fecha_evento\": \"YYYY-MM-DD\", \"gravedad\": 1-10, "
            f"\"ubicacion_texto\": \"\", \"barrio\": \"\", \"ciudad\": \"\", \"resumen\": \"\"}}. "
            f"Si no hay fecha, usa {fecha_hoy}. "
            f"Noticia: {n['texto'][:600]}"
        )
        
        exito = False
        # Intentamos con una lista de modelos comunes por si alguno falla
        modelos_a_probar = ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "claude-3-haiku"]
        
        for modelo in modelos_a_probar:
            if exito: break
            try:
                # Llamada simplificada sin especificar proveedor para evitar AttributeError
                response = g4f.ChatCompletion.create(
                    model=modelo,
                    messages=[{"role": "user", "content": prompt}],
                )
                
                if not response or len(response) < 10:
                    continue

                # Limpieza de formato Markdown
                texto_limpio = response
                if "```json" in texto_limpio:
                    texto_limpio = texto_limpio.split("```json")[1].split("```")[0].strip()
                elif "```" in texto_limpio:
                    texto_limpio = texto_limpio.split("```")[1].strip()
                
                datos_ia = json.loads(texto_limpio)
                
                # GEOLOCALIZACIÓN: El inyector necesita lat/lng
                lat, lng = geolocalizar(datos_ia.get('ubicacion_texto'), datos_ia.get('barrio'), datos_ia.get('ciudad'))

                # Armamos el registro final compatible con la DB
                resultados.append({
                    "url_fuente": n['url'],
                    "tipo_delito": datos_ia.get('tipo_delito', 'OTROS').upper(),
                    "fecha_evento": datos_ia.get('fecha_evento', fecha_hoy),
                    "gravedad": datos_ia.get('gravedad', 5),
                    "ubicacion_texto": datos_ia.get('ubicacion_texto', ''),
                    "barrio": datos_ia.get('barrio', ''),
                    "ciudad": datos_ia.get('ciudad', 'Asunción'),
                    "resumen_breve": datos_ia.get('resumen', n['titulo']),
                    "lat": lat,
                    "lng": lng
                })
                print(f"IA extrajo: {datos_ia.get('tipo_delito')} en {datos_ia.get('ciudad')} ({datos_ia.get('barrio')})")
                exito = True
                
            except Exception:
                # Si falla este modelo, el bucle sigue al siguiente automáticamente
                print(f"  Error con modelo {modelo}, intentando otro...")
        
        if not exito:
            print("    Fallo en el procesamiento.")
        
        # Pausa para evitar bloqueos
        time.sleep(1)

    # Guardar resultados
    with open(salida, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
        
    print(f"PROCESO COMPLETADO")
    print(f"Datos listos para el mapa de calor en: {salida}")

if __name__ == "__main__":
    principal()