import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import pandas as pd
from io_sead import lectura_SEAD_RA3_bin
from datetime import datetime
import os
import json

CONFIG_FILE = "config_ra3.json"

VARIABLES_DISPONIBLES = [
    'LOG M1','LOG M2','LOG M3','TASA M3','LIN M3','CIP','DELTA P',
    'LIN M4','QP','TEN 1','TSN 1','TEN 3','TSN 3','MA SB','MA PC',
    'MA TM','MA BT1','MA BT2','MA BT3','MA CO','CI N16-1','CI N16-2',
    'TEN 2','TSN 2','LOG A1','LOG A2','LOG A3','TASA A1','TASA A2',
    'COND','BC1','BC4','REACTIV'
]

class RA3App:

    def __init__(self, root):
        self.root = root
        self.root.title("Convertidor RA3")
        self.root.geometry("950x650")

        self.files = []
        self.selected_vars = set()

        main = ttk.Frame(root, padding=15)
        main.pack(fill=BOTH, expand=True)

        main.rowconfigure(1, weight=1)
        main.columnconfigure(0, weight=1)

        # HEADER
        header = ttk.Frame(main)
        header.grid(row=0, column=0, sticky="ew")

        ttk.Label(header, text="Convertidor RA3 2026",
                  font=("Segoe UI", 16, "bold")).pack(side=LEFT)

        self.status_label = ttk.Label(header, text="Estado: Listo")
        self.status_label.pack(side=RIGHT)

        # BODY
        body = ttk.Frame(main)
        body.grid(row=1, column=0, sticky="nsew", pady=10)

        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        # ARCHIVOS
        frame_files = ttk.Labelframe(body, text="Archivos", padding=10)
        frame_files.grid(row=0, column=0, sticky="nsew", padx=5)

        frame_files.columnconfigure(0, weight=1)
        frame_files.rowconfigure(1, weight=1)

        ttk.Button(frame_files, text="Agregar archivos",
                   command=self.select_files,
                   bootstyle="primary").grid(row=0, column=0, sticky="ew")

        ttk.Button(frame_files, text="Eliminar seleccionado",
                   command=self.remove_file,
                   bootstyle="danger").grid(row=0, column=1, padx=5)

        self.files_list = ttk.Treeview(frame_files, show="tree")
        self.files_list.grid(row=1, column=0, columnspan=2, sticky="nsew")

        scrollbar_files = ttk.Scrollbar(frame_files, command=self.files_list.yview)
        scrollbar_files.grid(row=1, column=2, sticky="ns")
        self.files_list.configure(yscrollcommand=scrollbar_files.set)

        self.label_rango = ttk.Label(frame_files, text="")
        self.label_rango.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        # VARIABLES
        frame_vars = ttk.Labelframe(body, text="Variables", padding=10)
        frame_vars.grid(row=0, column=1, sticky="nsew", padx=5)

        frame_vars.columnconfigure(0, weight=1)
        frame_vars.rowconfigure(2, weight=1)

        self.search_var = ttk.StringVar()
        search = ttk.Entry(frame_vars, textvariable=self.search_var)
        search.grid(row=0, column=0, sticky="ew", pady=5)
        self.search_var.trace_add("write", self.update_listbox)

        btns = ttk.Frame(frame_vars)
        btns.grid(row=1, column=0, sticky="ew")

        ttk.Button(btns, text="Seleccionar todas",
                   command=self.select_all).pack(side=LEFT, padx=2)

        ttk.Button(btns, text="Limpiar",
                   command=self.clear_selection).pack(side=LEFT, padx=2)

        self.counter_label = ttk.Label(btns, text="0 seleccionadas")
        self.counter_label.pack(side=RIGHT)

        self.listbox = ttk.Treeview(frame_vars, show="tree")
        self.listbox.grid(row=2, column=0, sticky="nsew")

        scrollbar_vars = ttk.Scrollbar(frame_vars, command=self.listbox.yview)
        scrollbar_vars.grid(row=2, column=1, sticky="ns")
        self.listbox.configure(yscrollcommand=scrollbar_vars.set)

        self.listbox.bind("<Button-1>", self.toggle_selection)

        self.listbox.tag_configure("selected", background="#28a745", foreground="white")

        self.all_vars = VARIABLES_DISPONIBLES.copy()
        self.populate_listbox(self.all_vars)

        # INTERVALO
        frame_interval = ttk.Labelframe(main, text="Intervalo de tiempo", padding=10)
        frame_interval.grid(row=2, column=0, sticky="ew", pady=10)

        self.interval_var = ttk.BooleanVar()

        ttk.Checkbutton(frame_interval, text="Usar intervalo",
                        variable=self.interval_var,
                        command=self.toggle_interval).grid(row=0, column=0, columnspan=2, sticky="w")

        ttk.Label(frame_interval, text="Desde:").grid(row=1, column=0)
        ttk.Label(frame_interval, text="Hasta:").grid(row=1, column=1)

        self.start_entry = ttk.Entry(frame_interval)
        self.start_entry.grid(row=2, column=0, sticky="ew", padx=5)

        self.end_entry = ttk.Entry(frame_interval)
        self.end_entry.grid(row=2, column=1, sticky="ew", padx=5)

        frame_interval.columnconfigure(0, weight=1)
        frame_interval.columnconfigure(1, weight=1)

        self.toggle_interval()

        # FOOTER
        footer = ttk.Frame(main)
        footer.grid(row=3, column=0, sticky="ew")

        ttk.Button(footer, text="Convertir y Exportar",
                   command=self.convert,
                   bootstyle="success").pack(fill=X, pady=10)

        self.load_config()

    # -------- PARSE ARCHIVOS --------
    def parse_ra3_filename(self, filename):
        name = os.path.basename(filename)
        try:
            if "-" in name:
                date_part, hour_part = name.split("-")
            else:
                date_part, hour_part = name.split("_")

            d, m, y = date_part.split("_")
            y = "20" + y
            hour = int(hour_part[:2])

            return datetime(int(y), int(m), int(d), hour)
        except:
            return datetime.min

    # -------- VARIABLES --------
    def populate_listbox(self, variables):
        self.listbox.delete(*self.listbox.get_children())
        for var in variables:
            if var in self.selected_vars:
                self.listbox.insert("", "end", text=var, tags=("selected",))
            else:
                self.listbox.insert("", "end", text=var)

    def update_listbox(self, *args):
        query = self.search_var.get().lower()
        filtered = [v for v in self.all_vars if query in v.lower()]
        self.populate_listbox(filtered)

    def toggle_selection(self, event):
        item = self.listbox.identify_row(event.y)
        if not item:
            return

        var = self.listbox.item(item, "text")

        if var in self.selected_vars:
            self.selected_vars.remove(var)
        else:
            self.selected_vars.add(var)

        self.update_listbox()
        self.update_counter()

    def select_all(self):
        self.selected_vars = set(self.all_vars)
        self.update_listbox()
        self.update_counter()

    def clear_selection(self):
        self.selected_vars.clear()
        self.update_listbox()
        self.update_counter()

    def update_counter(self):
        self.counter_label.config(text=f"{len(self.selected_vars)} seleccionadas")

    # -------- ARCHIVOS --------
    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("RA3 files", "*.RA3")])
        if not files:
            return

        for f in files:
            if f not in self.files:
                self.files.append(f)

        self.files.sort(key=self.parse_ra3_filename)

        self.files_list.delete(*self.files_list.get_children())
        for f in self.files:
            self.files_list.insert("", "end", text=os.path.basename(f))

        df_temp = lectura_SEAD_RA3_bin(self.files, variables=[], formato='datetime')

        inicio = df_temp['Fecha-Hora'].iloc[0]
        fin = df_temp['Fecha-Hora'].iloc[-1]

        self.label_rango.config(text=f"Rango: {inicio} → {fin}")

        self.start_entry.delete(0, "end")
        self.start_entry.insert(0, inicio.strftime("%Y-%m-%d %H:%M"))

        self.end_entry.delete(0, "end")
        self.end_entry.insert(0, fin.strftime("%Y-%m-%d %H:%M"))

        self.interval_var.set(True)
        self.toggle_interval()

    def remove_file(self):
        selected = self.files_list.selection()
        for item in selected:
            name = self.files_list.item(item)["text"]
            self.files = [f for f in self.files if not f.endswith(name)]
            self.files_list.delete(item)

    # -------- INTERVALO --------
    def toggle_interval(self):
        state = "normal" if self.interval_var.get() else "disabled"
        self.start_entry.config(state=state)
        self.end_entry.config(state=state)

    # -------- CONFIG --------
    def save_config(self):
        config = {
            "variables": list(self.selected_vars),
            "interval_on": self.interval_var.get(),
            "start": self.start_entry.get(),
            "end": self.end_entry.get()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return

        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        self.selected_vars = set(config.get("variables", []))
        self.interval_var.set(config.get("interval_on", False))

        self.start_entry.insert(0, config.get("start", ""))
        self.end_entry.insert(0, config.get("end", ""))

        self.update_listbox()
        self.update_counter()
        self.toggle_interval()

    # -------- CONVERTIR --------
    def convert(self):
        if not self.files or not self.selected_vars:
            messagebox.showerror("Error", "Faltan datos.")
            return

        variables = list(self.selected_vars)
        region = False

        if self.interval_var.get():
            try:
                start = datetime.strptime(self.start_entry.get(), "%Y-%m-%d %H:%M:%S")
                end = datetime.strptime(self.end_entry.get(), "%Y-%m-%d %H:%M:%S")
                if start >= end:
                    raise ValueError
                region = [start, end]
            except:
                messagebox.showerror("Error", "Formato inválido.")
                return

        data = lectura_SEAD_RA3_bin(
            self.files,
            variables=variables,
            region=region,
            formato='datetime'
        )

        if data.empty:
            messagebox.showerror("Error", "Sin datos.")
            return

        # 👉 columna hora
        data['Hora'] = data['Fecha-Hora'].dt.strftime('%H:%M:%S')

        columnas = ['Fecha-Hora', 'Hora'] + variables

        # nombre por defecto
        first_file = os.path.basename(self.files[0])
        default_name = os.path.splitext(first_file)[0] + "_convertido"

        save_path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx")]
        )

        if not save_path:
            return

        # 👉 exportación según formato
        if save_path.endswith(".xlsx"):
            data.to_excel(save_path, columns=columnas, index=False)
        else:
            data.to_csv(save_path, columns=columnas, sep=';', index=False, decimal=',')

        self.save_config()
        messagebox.showinfo("Listo", "Exportación completada.")


if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = RA3App(root)
    root.mainloop()
