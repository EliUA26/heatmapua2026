# import time
# import json
# import requests
# import os
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

# HEADERS = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#     'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'DNT': '1',
#     'Connection': 'keep-alive',
#     'Upgrade-Insecure-Requests': '1',
#     'Referer': 'https://www.ultimahora.com/'
# }

# KEYWORDS = [
#     "policiales", "robo", "asalto", "detenido",
#     "crimen", "hurto", "asesinato", "motochorro",
#     "investigan", "fiscalia"
# ]

# # ---------------------------
# # UTILIDAD
# # ---------------------------

# def es_relevante(texto):
#     texto = texto.lower()
#     return any(k in texto for k in KEYWORDS)


# def limpiar_texto(parrafos):
#     texto = " ".join(
#         p.get_text(" ", strip=True)
#         for p in parrafos
#         if len(p.get_text(strip=True)) > 30
#     )
#     return texto


# # ---------------------------
# # ABC SCRAPER
# # ---------------------------

# def obtener_links_abc():
#     print("ABC scraping...")

#     url = "https://www.abc.com.py/policiales/"
#     res = requests.get(url, headers=HEADERS, timeout=10)

#     if res.status_code != 200:
#         print("Error ABC:", res.status_code)
#         return []

#     soup = BeautifulSoup(res.text, "html.parser")

#     links = set()

#     for a in soup.select("a[href]"):
#         href = a["href"]

#         full_url = urljoin("https://www.abc.com.py", href)

#         if "/policiales/" in full_url:
#             links.add(full_url)

#     return list(links)

# def obtener_links_hoy():
#     print(" HOY scraping...")

#     url = "https://www.hoy.com.py/tag/asalto"
#     res = requests.get(url, headers=HEADERS, timeout=10)

#     if res.status_code != 200:
#         print("Error HOY:", res.status_code)
#         return []

#     soup = BeautifulSoup(res.text, "html.parser")

#     links = set()

#     # Buscar todos los enlaces dentro de artículos
#     for article in soup.select("article.list-entry"):
#         # Buscar el enlace principal del título
#         link_elem = article.select_one("h3.list-entry-title a")
#         if link_elem and link_elem.get("href"):
#             href = link_elem["href"]
#             # HOY usa /nacionales/ o similar, no /articulo/
#             if any(keyword in href.lower() for keyword in KEYWORDS):
#                 links.add(href)

#     return list(links)



# def obtener_links_ultimahora():
#     print(" Última Hora scraping...")

#     url = "https://www.ultimahora.com/nacionales"
#     res = requests.get(url, headers=HEADERS, timeout=10)

#     if res.status_code != 200:
#         print("Error Última Hora:", res.status_code)
#         return []

#     soup = BeautifulSoup(res.text, "html.parser")

#     links = set()

#     # Buscar todos los enlaces dentro de PagePromo-title
#     for title_elem in soup.select("div.PagePromo-title a.Link"):
#         href = title_elem.get("href")
#         if href and any(keyword in href.lower() for keyword in KEYWORDS):
#             links.add(href)

#     return list(links)

# # ---------------------------
# # EXTRAER NOTICIA
# # ---------------------------

# def extraer_noticia(url):
#     try:
#         res = requests.get(url, headers=HEADERS, timeout=10)

#         if res.status_code != 200:
#             return None

#         soup = BeautifulSoup(res.text, "html.parser")

#         titulo = soup.find("h1")
#         titulo = titulo.get_text(strip=True) if titulo else "Sin título"

#         parrafos = soup.select("article p, .content p, p")

#         texto = limpiar_texto(parrafos)

#         if len(texto) < 100:
#             return None

#         if not es_relevante(titulo + " " + texto):
#             return None

#         return {
#             "url": url,
#             "titulo": titulo,
#             "texto": texto
#         }

#     except Exception as e:
#         print(" Error:", url, e)
#         return None


# # ---------------------------
# # MAIN
# # ---------------------------

# if __name__ == "__main__":

#     links_abc = obtener_links_abc()
#     links_hoy = obtener_links_hoy()
#     links_uh = obtener_links_ultimahora()
    
#     # Combinar todos los links
#     links = list(set(links_abc + links_hoy + links_uh))

#     print(f" Links encontrados: {len(links)}")

#     noticias = []

#     for i, link in enumerate(list(links)[:100]):
#         print(f"[{i+1}] procesando...")

#         data = extraer_noticia(link)

#         if data:
#             noticias.append(data)

#         time.sleep(0.5)

   
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     noticia_raw = os.path.join(script_dir, '..', 'data', 'noticias_raw.json')
    
#     with open(noticia_raw, "w", encoding="utf-8") as f:
#         json.dump(noticias, f, ensure_ascii=False, indent=4)

#     print("✅ Listo: noticias_raw.json generado")


import time
import json
import requests
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://www.ultimahora.com/'
}

KEYWORDS = [
    "policiales", "robo", "asalto", "detenido",
    "crimen", "hurto", "asesinato", "motochorro",
    "investigan", "fiscalia"
]

# --- CONFIGURACIÓN DE FILTRADO ---
FECHA_MINIMA = datetime(2026, 1, 1)  # Solo noticias desde el 1 de Enero de 2026

# CONFIGURACIÓN DE FUENTES (Aquí eliges qué páginas y cómo buscarlas)
CONFIG_FUENTES = {
    "abc": {
        "url": "https://www.abc.com.py/policiales/",
        "selector": "a[href]",
        "base_url": "https://www.abc.com.py",
        "filtro_url": "/policiales/"
    },
    "hoy": {
        "url": "https://www.hoy.com.py/tag/asalto",
        "selector": "h3.list-entry-title a",
        "base_url": "",
        "filtro_url": "" # Se filtra por KEYWORDS más abajo
    },
    "ultimahora": {
        "url": "https://www.ultimahora.com/nacionales",
        "selector": "div.PagePromo-title a.Link",
        "base_url": "",
        "filtro_url": ""
    }
}

# ---------------------------
# UTILIDAD
# ---------------------------

def es_relevante(texto):
    texto = texto.lower()
    return any(k in texto for k in KEYWORDS)


def limpiar_texto(parrafos):
    texto = " ".join(
        p.get_text(" ", strip=True)
        for p in parrafos
        if len(p.get_text(strip=True)) > 30
    )
    return texto


def obtener_links_generico(nombre_fuente):
    conf = CONFIG_FUENTES.get(nombre_fuente)
    if not conf:
        return []

    print(f"Scraping {nombre_fuente.upper()}...")
    try:
        res = requests.get(conf["url"], headers=HEADERS, timeout=10)
        if res.status_code != 200:
            print(f"Error en {nombre_fuente}: {res.status_code}")
            return []

        soup = BeautifulSoup(res.text, "html.parser")
        links = set()

        for a in soup.select(conf["selector"]):
            href = a.get("href")
            if not href: continue
            
            full_url = urljoin(conf["base_url"], href)
            
            # Criterio: que tenga el filtro específico O que contenga keywords
            if (conf["filtro_url"] and conf["filtro_url"] in full_url) or \
               any(k in full_url.lower() for k in KEYWORDS):
                links.add(full_url)
        return list(links)
    except Exception as e:
        print(f"Excepción en {nombre_fuente}: {e}")
        return []

# ---------------------------
# EXTRAER NOTICIA
# ---------------------------

def extraer_noticia(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)

        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        # --- EXTRACCIÓN Y FILTRADO POR FECHA ---
        fecha_encontrada = None
        
        # 1. Intentar extraer de meta tags (Estándar SEO: article:published_time)
        meta_fecha = soup.find("meta", property="article:published_time") or \
                     soup.find("meta", {"name": "publish-date"})
        
        if meta_fecha:
            try:
                # Extraer solo la parte de la fecha YYYY-MM-DD
                fecha_str = meta_fecha["content"].split("T")[0]
                fecha_encontrada = datetime.strptime(fecha_str, "%Y-%m-%d")
            except: pass

        # 2. Fallback: Intentar extraer de la URL (Específico para ABC Color: /YYYY/MM/DD/)
        if not fecha_encontrada:
            match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
            if match:
                fecha_encontrada = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))

        # Si se encontró la fecha y es anterior a nuestra fecha límite, descartamos la noticia
        if fecha_encontrada and fecha_encontrada < FECHA_MINIMA:
            return None

        titulo = soup.find("h1")
        titulo = titulo.get_text(strip=True) if titulo else "Sin título"

        parrafos = soup.select("article p, .content p, p")

        texto = limpiar_texto(parrafos)

        if len(texto) < 100:
            return None

        if not es_relevante(titulo + " " + texto):
            return None

        return {
            "url": url,
            "titulo": titulo,
            "texto": texto
        }

    except Exception as e:
        print(" Error:", url, e)
        return None


# ---------------------------
# MAIN
# ---------------------------

if __name__ == "__main__":

    # AQUÍ ELIGES LAS FUENTES: Puedes comentar o quitar elementos de esta lista
    fuentes_a_procesar = ["abc", "hoy", "ultimahora"]
    
    links = []
    for f in fuentes_a_procesar:
        links.extend(obtener_links_generico(f))

    links = list(set(links)) # Eliminar duplicados
    print(f" Links encontrados: {len(links)}")

    noticias = []

    for i, link in enumerate(list(links)[:100]):
        print(f"[{i+1}] procesando...")

        data = extraer_noticia(link)

        if data:
            noticias.append(data)

        time.sleep(0.5)

   
    script_dir = os.path.dirname(os.path.abspath(__file__))
    noticia_raw = os.path.join(script_dir, '..', 'data', 'noticias_raw.json')
    
    with open(noticia_raw, "w", encoding="utf-8") as f:
        json.dump(noticias, f, ensure_ascii=False, indent=4)

    print("✅ Listo: noticias_raw.json generado")