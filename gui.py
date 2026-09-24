import tkinter as tk
from tkinter import filedialog, messagebox
from generator import generar_pdf
import os


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Numerador de folios")
        self.geometry("600x450")

        self.crear_interfaz()


    def crear_interfaz(self):

        # Plantilla
        tk.Label(self, text="Plantilla SVG").pack(anchor="w", padx=20)

        self.plantilla = tk.Entry(self, width=70)
        self.plantilla.pack(padx=20)

        tk.Button(
            self,
            text="Buscar",
            command=self.buscar_plantilla
        ).pack()


        # Salida
        tk.Label(self, text="Carpeta salida").pack(anchor="w", padx=20)

        self.salida = tk.Entry(self, width=70)
        self.salida.pack(padx=20)

        tk.Button(
            self,
            text="Buscar",
            command=self.buscar_salida
        ).pack()


        # Inkscape
        tk.Label(self, text="Inkscape").pack(anchor="w", padx=20)

        self.inkscape = tk.Entry(self, width=70)
        self.inkscape.pack(padx=20)

        self.inkscape.insert(
            0,
            r"C:\Program Files\Inkscape\bin\inkscape.exe"
        )


        # Parámetros

        frame = tk.Frame(self)
        frame.pack(pady=10)


        tk.Label(frame, text="Número inicial").grid(row=0,column=0)
        self.numero = tk.Entry(frame,width=10)
        self.numero.grid(row=0,column=1)
        self.numero.insert(0,"1")


        tk.Label(frame, text="Hojas").grid(row=1,column=0)
        self.hojas = tk.Entry(frame,width=10)
        self.hojas.grid(row=1,column=1)
        self.hojas.insert(0,"250")


        tk.Label(frame, text="Offset").grid(row=2,column=0)
        self.offset = tk.Entry(frame,width=10)
        self.offset.grid(row=2,column=1)
        self.offset.insert(0,"250")


        # Botón generar

        tk.Button(
            self,
            text="GENERAR PDF",
            command=self.generar
        ).pack(pady=20)


        self.estado = tk.Label(self,text="")
        self.estado.pack()


    def buscar_plantilla(self):

        archivo = filedialog.askopenfilename(
            filetypes=[("SVG","*.svg")]
        )

        if archivo:
            self.plantilla.delete(0,tk.END)
            self.plantilla.insert(0,archivo)


    def buscar_salida(self):

        carpeta = filedialog.askdirectory()

        if carpeta:
            self.salida.delete(0,tk.END)
            self.salida.insert(0,carpeta)


    def generar(self):

        try:

            self.estado.config(
                text="Generando..."
            )

            pdf = generar_pdf(

                plantilla=self.plantilla.get(),

                salida=self.salida.get(),

                inkscape=self.inkscape.get(),

                numero_inicial=int(
                    self.numero.get()
                ),

                hojas=int(
                    self.hojas.get()
                ),

                offset=int(
                    self.offset.get()
                ),

                nombre_pdf="resultado.pdf"

            )


            self.estado.config(
                text=f"Listo: {pdf}"
            )


            messagebox.showinfo(
                "Terminado",
                "PDF generado correctamente"
            )


        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )