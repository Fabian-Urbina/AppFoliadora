import os
import re
import subprocess
import xml.etree.ElementTree as ET
import sys

from pypdf import PdfWriter

NS = {"svg": "http://www.w3.org/2000/svg"}

def resource_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))
def generar_pdf(
    plantilla,
    salida,
    inkscape,
    numero_inicial,
    hojas,
    offset,
    nombre_pdf="salida.pdf",
    prefijo="N° ",
    digitos=6,
    progress_bar = None
):

    BASE_DIR = resource_path()
    TEMP_DIR = os.path.join(BASE_DIR, "temp")
    SALIDA_DIR = salida
    os.makedirs(SALIDA_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    writer = PdfWriter()

    numero = numero_inicial

    for hoja in range(1, hojas + 1):

        tree = ET.parse(plantilla)
        root = tree.getroot()

        folios = []

        # Buscar TODOS los objetos de texto
        for text in root.findall(".//svg:text", NS):

            object_id = text.get("id")
            print(f"Procesando objeto de texto con id: {object_id}")

            if object_id is None:
                continue

            m = re.fullmatch(r"folio(\d+)", object_id)

            if m is None:
                continue

            indice = int(m.group(1))

            # Buscar el primer tspan del texto
            tspan = text.find("svg:tspan", NS)

            if tspan is None:
                continue

            folios.append((indice, tspan))

        # Ordenar por folio1, folio2...
        folios.sort(key=lambda x: x[0])

        # Reemplazar contenido
        for indice, tspan in folios:

            valor = numero + (indice - 1) * offset

            tspan.text = prefijo + f"{valor:0{digitos}d}"

        svg_temp = os.path.join(TEMP_DIR, f"tmp_{hoja:03}.svg")
        pdf_temp = os.path.join(TEMP_DIR, f"tmp_{hoja:03}.pdf")

        tree.write(svg_temp, encoding="utf-8", xml_declaration=True)

        subprocess.run(
            [
                inkscape,
                svg_temp,
                "--export-type=pdf",
                f"--export-filename={pdf_temp}",
            ],
            check=True,
        )

        writer.append(pdf_temp)

        numero += 1

    pdf_final = os.path.join(SALIDA_DIR, nombre_pdf)

    writer.write(pdf_final)
    writer.close()

    # Eliminar archivos temporales
    for hoja in range(1, hojas + 1):

        svg_temp = os.path.join(TEMP_DIR, f"tmp_{hoja:03}.svg")
        pdf_temp = os.path.join(TEMP_DIR, f"tmp_{hoja:03}.pdf")

        if os.path.exists(svg_temp):
            os.remove(svg_temp)

        if os.path.exists(pdf_temp):
            os.remove(pdf_temp)

    return pdf_final

if __name__ == "__main__":
    generar_pdf(
        plantilla=r"...",
        salida=r"...",
        inkscape=r"...",
        numero_inicial=1,
        hojas=10,
        offset=250,
        nombre_pdf="test.pdf",
        progress_bar = None
    )