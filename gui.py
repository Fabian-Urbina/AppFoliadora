import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import win32print  
from generator import generar_e_imprimir_pdf 
import os
import threading  # <-- Para que la app responda al hacer clic en Cancelar

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Numerador e Impresor de folios")
        self.geometry("600x560")  
        
        # Variable para controlar la detención
        self.cancelado = False 
        
        self.crear_interfaz()

    def obtener_impresoras(self):
        impresoras = [imp for imp in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
        try:
            predeterminada = win32print.GetDefaultPrinter()
        except:
            predeterminada = impresoras if impresoras else ""
        return impresoras, predeterminada

    def crear_interfaz(self):
        # Plantilla
        tk.Label(self, text="Plantilla SVG").pack(anchor="w", padx=20, pady=(10,0))
        self.plantilla = tk.Entry(self, width=70)
        self.plantilla.pack(padx=20)
        tk.Button(self, text="Buscar Plantilla", command=self.buscar_plantilla).pack(pady=5)

        # Selector de Impresora
        tk.Label(self, text="Seleccionar Impresora").pack(anchor="w", padx=20, pady=(5,0))
        lista_impresoras, impresora_defecto = self.obtener_impresoras()
        
        self.selector_impresora = ttk.Combobox(self, values=lista_impresoras, width=67, state="readonly")
        self.selector_impresora.pack(padx=20)
        if impresora_defecto:
            self.selector_impresora.set(impresora_defecto)

        # Inkscape
        tk.Label(self, text="Ruta de Inkscape").pack(anchor="w", padx=20, pady=(5,0))
        self.inkscape = tk.Entry(self, width=70)
        self.inkscape.pack(padx=20)
        self.inkscape.insert(0, r"C:\Program Files\Inkscape\bin\inkscape.exe")

        # Parámetros en un Frame
        frame = tk.Frame(self)
        frame.pack(pady=15)

        tk.Label(frame, text="Número inicial:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.numero = tk.Entry(frame, width=10)
        self.numero.grid(row=0, column=1, padx=5, pady=5)
        self.numero.insert(0, "1")

        tk.Label(frame, text="Total Hojas:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.hojas = tk.Entry(frame, width=10)
        self.hojas.grid(row=1, column=1, padx=5, pady=5)
        self.hojas.insert(0, "250")

        tk.Label(frame, text="Offset:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.offset = tk.Entry(frame, width=10)
        self.offset.grid(row=2, column=1, padx=5, pady=5)
        self.offset.insert(0, "250")

        # Barra de progreso
        self.progreso = ttk.Progressbar(self, orient="horizontal", length=420, mode="determinate")
        self.progreso.pack(pady=(10, 5))

        self.estado = tk.Label(self, text="Listo para iniciar")
        self.estado.pack()

        # CONTENEDOR DE BOTONES PARALELOS
        boton_frame = tk.Frame(self)
        boton_frame.pack(pady=15)

        self.btn_generar = tk.Button(
            boton_frame,
            text="GENERAR Y IMPRIMIR",
            command=self.iniciar_hilo_impresion,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        self.btn_generar.grid(row=0, column=0, padx=10)

        self.btn_cancelar = tk.Button(
            boton_frame,
            text="CANCELAR PROCESO",
            command=self.cancelar_impresion,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10,
            state="disabled"  # Bloqueado hasta que empiece la impresión
        )
        self.btn_cancelar.grid(row=0, column=1, padx=10)

    def buscar_plantilla(self):
        archivo = filedialog.askopenfilename(filetypes=[("SVG", "*.svg")])
        if archivo:
            self.plantilla.delete(0, tk.END)
            self.plantilla.insert(0, archivo)

    def actualizar_progreso(self, hoja_actual, total_hojas):
        porcentaje = (hoja_actual / total_hojas) * 100
        self.progreso["value"] = porcentaje
        self.estado.config(text=f"Procesando y enviando hoja {hoja_actual} de {total_hojas} ({int(porcentaje)}%)")
        self.update_idletasks()

    def verificar_cancelacion(self):
        return self.cancelado

    def cancelar_impresion(self):
        self.cancelado = True
        self.estado.config(text="Cancelando... Deteniendo el envío de hojas.")
        self.btn_cancelar.config(state="disabled")

    def iniciar_hilo_impresion(self):
        """ Lanza la impresión en segundo plano para mantener la ventana viva """
        self.cancelado = False
        self.progreso["value"] = 0
        self.btn_generar.config(state="disabled")
        self.btn_cancelar.config(state="normal")
        
        # Creamos y encendemos el hilo secundario
        hilo = threading.Thread(target=self.ejecutar_proceso)
        hilo.setDaemon(True)
        hilo.start()

    def ejecutar_proceso(self):
        if not self.selector_impresora.get():
            messagebox.showwarning("Falta Impresora", "Por favor, selecciona una impresora válida.")
            self.finalizar_interfaz_botones()
            return

        try:
            self.estado.config(text="Iniciando el motor de numeración...")
            
            generar_e_imprimir_pdf(
                plantilla=self.plantilla.get(),
                inkscape=self.inkscape.get(),
                numero_inicial=int(self.numero.get()),
                hojas=int(self.hojas.get()),
                offset=int(self.offset.get()),
                nombre_impresora=self.selector_impresora.get(),
                progress_bar=self.actualizar_progreso,
                check_cancel=self.verificar_cancelacion  # <-- Conexión de parada
            )

            if self.cancelado:
                self.estado.config(text="Proceso interrumpido.")
                messagebox.showwarning("Cancelado", "Se detuvo el envío de nuevos folios a la impresora.")
            else:
                self.estado.config(text="Proceso completado.")
                messagebox.showinfo("Terminado", "Todas las hojas fueron enviadas.")

        except Exception as e:
            self.estado.config(text="Error en el proceso.")
            messagebox.showerror("Error", str(e))
            
        finally:
            self.finalizar_interfaz_botones()

    def finalizar_interfaz_botones(self):
        self.btn_generar.config(state="normal")
        self.btn_cancelar.config(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()
