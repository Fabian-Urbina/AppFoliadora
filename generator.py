import os
import re
import subprocess
import xml.etree.ElementTree as ET
import sys
import time

# Mantenemos tus Namespaces originales que garantizan el foliado correcto
NS = {"svg": "http://www.w3.org/2000/svg"}

def resource_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def generar_e_imprimir_pdf(
    plantilla,
    inkscape,
    numero_inicial,
    hojas,
    offset,
    nombre_impresora=None,
    prefijo="N° ",
    digitos=6,
    progress_bar=None,
    check_cancel=None
):
    BASE_DIR = resource_path()
    TEMP_DIR = os.path.join(BASE_DIR, "temp")
    os.makedirs(TEMP_DIR, exist_ok=True)

    numero = numero_inicial
    pdfs_creados = []

    for hoja in range(1, hojas + 1):
        if check_cancel and check_cancel():
            print("🛑 Impresión cancelada por el usuario.")
            break
        
        tree = ET.parse(plantilla)
        root = tree.getroot()
        folios = []

        # Buscar TODOS los objetos de texto usando tu Namespace original
        for text in root.findall(".//svg:text", NS):
            object_id = text.get("id")
            
            # --- SOLUCIÓN DE BÚSQUEDA FLEXIBLE PARA EL LABEL ---
            object_label = None
            # Revisamos todas las llaves de los atributos del objeto de texto crudo
            for llave_attr, valor_attr in text.attrib.items():
                # Si la llave termina en 'label' (no importa el namespace que use Inkscape), lo guardamos
                if llave_attr.endswith("label"):
                    object_label = valor_attr
                    break
            # ---------------------------------------------------

            print(f"Procesando objeto de texto: id={object_id}, label={object_label}")
            
            if object_label is None:
                continue

            # El MATCH ahora se hace de forma robusta sobre el object_label detectado
            m = re.fullmatch(r"folio(\d+)", object_label, re.IGNORECASE)
            if m is None:
                continue

            indice = int(m.group(1))

            # Buscar el primer tspan del texto
            tspan = text.find("svg:tspan", NS)
            if tspan is None:
                continue

            folios.append((indice, tspan))

        print(f"📊 Total de folios emparejados con éxito por LABEL en Hoja {hoja}: {len(folios)}")

        # Ordenar por folio1, folio2...
        folios.sort(key=lambda x: x[0])

        # Reemplazar contenido (Tu lógica exacta original)
        for indice, tspan in folios:
            valor = numero + (indice - 1) * offset
            tspan.text = prefijo + f"{valor:0{digitos}d}"

        svg_temp = os.path.join(TEMP_DIR, f"tmp_{hoja:03}.svg")
        pdf_temp = os.path.join(TEMP_DIR, f"tmp_{hoja:03}.pdf")

        # Guardar el SVG temporal modificado
        tree.write(svg_temp, encoding="utf-8", xml_declaration=True)

        # Convertir a PDF con Inkscape
        subprocess.run(
            [
                inkscape,
                svg_temp,
                "--export-type=pdf",
                f"--export-filename={pdf_temp}",
            ],
            check=True,
        )

        pdfs_creados.append(pdf_temp)

        # Enviar a la impresora seleccionada
        if nombre_impresora:
            try:
                import win32api
                win32api.ShellExecute(0, "printto", pdf_temp, f'"{nombre_impresora}"', ".", 0)
                time.sleep(0.5)
            except Exception as e:
                print(f"Error al enviar a la impresora {nombre_impresora}: {e}")

        # Avanzar el contador de folios
        numero += 1

        if progress_bar:
            progress_bar(hoja, hojas)

        # Se borra el SVG temporal
        if os.path.exists(svg_temp):
            os.remove(svg_temp)

    # --- LIMPIEZA POST-IMPRESIÓN ---
    time.sleep(5) 
    for pdf in pdfs_creados:
        try:
            if os.path.exists(pdf):
                os.remove(pdf)
        except PermissionError:
            pass

# Bloque main de debug para validar localmente en la terminal
if __name__ == "__main__":
    PLANTILLA_PRUEBA = r"C:\Users\fitoz\Desktop\Trabajos Imprenta\entradas pajaritos solo folios.svg"
    INKSCAPE_PRUEBA = r"C:\Program Files\Inkscape\bin\inkscape.exe"

    if os.path.exists(PLANTILLA_PRUEBA) and os.path.exists(INKSCAPE_PRUEBA):
        print("🚀 Ejecutando prueba de Foliación por Label Inteligente...")
        generar_e_imprimir_pdf(
            plantilla=PLANTILLA_PRUEBA,
            inkscape=INKSCAPE_PRUEBA,
            numero_inicial=1,
            hojas=2,
            offset=250,
            nombre_impresora=None
        )
        print("🏁 Proceso terminado.")

