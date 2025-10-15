import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import threading
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re

alfabeto = {"0", "1"}

productos = {
    "01": ("galletas.jpg", "Galletas", "$1500"),
    "10": ("gaseosa.jpg", "Gaseosa", "$1500"),
    "00": ("agua.jpg", "Agua", "$1000"),
    "11": ("papas.jpg", "Papitas", "$2000"),
    "000": ("chicle.jpg", "Chicle", "$1500"),
    "111": ("chocolate.jpg", "Chocolate", "$3000"),
    "010": ("mani.jpg", "Maní", "$2000"),
    "101": ("jugo.jpg", "Jugo", "$2000"),
    "011": ("tostacos.jpg", "Tostacos", "$2500"),
}


def construir_automata_para(secuencia):
    q0 = "q0"
    estados = {q0}
    transiciones = {}
    finales = set()
    estado_actual = q0
    for i, simbolo in enumerate(secuencia):
        nuevo_estado = f"q{i+1}"
        estados.add(nuevo_estado)
        transiciones[(estado_actual, simbolo)] = nuevo_estado
        estado_actual = nuevo_estado
    finales.add(estado_actual)
    return estados, alfabeto, transiciones, q0, finales


def procesar_entrada(entrada):
    return productos.get(entrada, False)



def construir_expresion_regular(transiciones):

    reglas = {}
    for (estado, simbolo), destino in transiciones.items():
        if estado not in reglas:
            reglas[estado] = []
        reglas[estado].append((simbolo, destino))

  
    pasos = []
    for estado, lista in reglas.items():
        expresion = " + ".join([f"{s}{d}" for s, d in lista])
        pasos.append(f"{estado} = {expresion}")
   
    destinos = {d for _, d in transiciones.items()}
    for d in destinos:
        if d not in reglas:
            pasos.append(f"{d} = λ")

    simplificado = dict(re.findall(r"(q\d+) = (.+)", "\n".join(pasos)))

    def expandir(estado):
        expr = simplificado[estado]
        partes = expr.split("+")
        resultado = ""
        for parte in partes:
            simbolos = []
            i = 0
            while i < len(parte):
                if parte[i] == "q":
                   
                    j = i + 1
                    while j < len(parte) and parte[j].isdigit():
                        j += 1
                    destino = parte[i:j]
                    if destino in simplificado:
                        simbolos.append(f"({expandir(destino)})")
                    i = j
                else:
                    simbolos.append(parte[i])
                    i += 1
            resultado += "".join(simbolos)
        return resultado.replace("λ", "")

    simplificada = expandir("q0")

    salida = "=== Expresión Regular Paso a Paso ===\n"
    salida += "\n".join(pasos)
    salida += f"\n\n=== Expresión Regular Simplificada ===\nq0 = {simplificada}"
    return salida

def dibujar_grafo(transiciones, finales, q0, contenedor):
    for widget in contenedor.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(5.5, 4.5), dpi=100)
    G = nx.DiGraph()
    for (estado, simbolo), destino in transiciones.items():
        G.add_edge(estado, destino, label=simbolo)
    pos = nx.circular_layout(G)
    nx.draw(G, pos, with_labels=True, node_color="#a4c8ff", node_size=1800,
            font_weight="bold", font_size=12, arrowsize=20, ax=ax)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=11, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=[q0], node_color="#88ff88", node_size=1800, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=list(finales), node_color="#ff8888", node_size=1800, ax=ax)
    ax.set_title("Grafo del Autómata (AFD)", fontsize=13, pad=10)
    ax.axis("off")

    canvas_fig = FigureCanvasTkAgg(fig, master=contenedor)
    canvas_fig.draw()
    canvas_fig.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)


def animar_producto(img_path):
    canvas_animacion.delete("all")
    try:
        img = Image.open(img_path)
        img = img.resize((80, 80))
        tk_img = ImageTk.PhotoImage(img)
    except Exception:
        return

    producto = canvas_animacion.create_image(200, 40, image=tk_img)
    canvas_animacion.image = tk_img

    for angulo in range(0, 360, 20):
        rotated = img.rotate(angulo)
        tk_rotado = ImageTk.PhotoImage(rotated)
        canvas_animacion.itemconfig(producto, image=tk_rotado)
        canvas_animacion.image = tk_rotado
        root.update()
        time.sleep(0.02)

    for y in range(40, 180, 5):
        canvas_animacion.move(producto, 0, 5)
        root.update()
        time.sleep(0.03)

    time.sleep(1)
    canvas_animacion.delete("all")


def verificar_entrada(event):
    entrada = entry.get().strip()
    if not entrada:
        info_automata.config(text="Ingrese una secuencia.")
        resultado.config(text="")
        return

    estados, sigma, delta, q0, finales = construir_automata_para(entrada)
    resultado_producto = procesar_entrada(entrada)

    expresion = construir_expresion_regular(delta)
    texto = (
        f"Alfabeto (Σ): {', '.join(sigma)}\n"
        f"Conjunto de estados (Q): {', '.join(estados)}\n"
        f"Estado inicial: {q0}\n"
        f"Estado(s) de aceptación: {', '.join(finales)}\n\n"
        f"Función de transición (δ):\n"
    )
    for (estado, simbolo), destino in delta.items():
        texto += f"  δ({estado}, {simbolo}) → {destino}\n"
    texto += f"\n{expresion}"

    info_automata.config(text=texto)

    if resultado_producto:
        nombre_img, nombre, precio = resultado_producto
        resultado.config(text=f"Pertenece  Al Automata✅\n{nombre} - {precio}", fg="green")
        dibujar_grafo(delta, finales, q0, grafo_frame)
        threading.Thread(target=animar_producto, args=(nombre_img,), daemon=True).start()
    else:
        resultado.config(text="No pertenece Al Automata❌", fg="red")
        for widget in grafo_frame.winfo_children():
            widget.destroy()

root = tk.Tk()
root.title("Máquina Expendedora")
root.geometry("1100x800")
root.config(bg="#dfe8ff")

# Frame con scroll
main_canvas = tk.Canvas(root, bg="#dfe8ff", highlightthickness=0)
main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
main_canvas.configure(yscrollcommand=scrollbar.set)
scroll_frame = tk.Frame(main_canvas, bg="#dfe8ff")
main_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")


def on_frame_configure(event):
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))


scroll_frame.bind("<Configure>", on_frame_configure)

titulo = tk.Label(scroll_frame, text="MÁQUINA EXPENDEDORA",
                  font=("Arial Black", 20), bg="#dfe8ff", fg="#222")
titulo.pack(pady=10)

frame = tk.Frame(scroll_frame, bg="#dfe8ff")
frame.pack()
tk.Label(frame, text="Ingrese la secuencia (0=500, 1=1000):",
         font=("Arial", 14), bg="#dfe8ff").grid(row=0, column=0)
entry = tk.Entry(frame, font=("Consolas", 14), width=20)
entry.grid(row=0, column=1, padx=10)
entry.bind("<Return>", verificar_entrada)

info_automata = tk.Label(scroll_frame, text="", font=("Consolas", 12),
                         justify="left", bg="#dfe8ff", fg="#111")
info_automata.pack(pady=10)

resultado = tk.Label(scroll_frame, text="", font=("Arial", 16), bg="#dfe8ff")
resultado.pack(pady=10)

maquina_frame = tk.Frame(scroll_frame, bg="#a7baff", bd=5, relief="ridge")
maquina_frame.pack(pady=10)
canvas_animacion = tk.Canvas(maquina_frame, width=400, height=220, bg="#f3f3f3")
canvas_animacion.pack(pady=10)
tk.Label(maquina_frame, text="Máquina Expendedora",
         font=("Arial Black", 14), bg="#a7baff", fg="white").pack()


productos_frame = tk.LabelFrame(scroll_frame, text="Productos disponibles",
                                font=("Arial", 14, "bold"), bg="#ffffff",
                                padx=15, pady=15)
productos_frame.pack(pady=10, padx=20, fill="x")

row = col = 0
for secuencia, (img_file, nombre, precio) in productos.items():
    try:
        img = Image.open(img_file).resize((90, 90))
        img_tk = ImageTk.PhotoImage(img)
    except:
        continue

    frame_prod = tk.Frame(productos_frame, bg="white", padx=10, pady=10)
    frame_prod.grid(row=row, column=col, padx=20, pady=20)
    lbl_img = tk.Label(frame_prod, image=img_tk, bg="white")
    lbl_img.image = img_tk
    lbl_img.pack()
    tk.Label(frame_prod, text=nombre, font=("Arial", 12, "bold"), bg="white").pack()
    tk.Label(frame_prod, text=precio, font=("Arial", 11), fg="#333", bg="white").pack()
    col += 1
    if col == 3:
        col = 0
        row += 1

grafo_frame = tk.LabelFrame(scroll_frame, text="Visualización del Grafo del AFD",
                            font=("Arial", 14, "bold"), bg="#ffffff", padx=10, pady=10)
grafo_frame.pack(pady=15, padx=20, fill="both", expand=True)

root.mainloop()
