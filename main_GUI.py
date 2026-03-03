import tkinter as tk
from tkinter import messagebox, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import os

# ---------------- GLOBAL VARIABLES ----------------

X = []
Y = []
scale = {}   # {"x":[unit, small, min], "y":[unit, small, min]}
triangle_artists = [] #Dummy
highlight_artists = [] #Dummy

# ---------------- CORE FUNCTIONS ----------------

def parse_data():
    global X, Y
    try:
        X = list(map(float, x_entry.get().split(",")))
        Y = list(map(float, y_entry.get().split(",")))

        if len(X) != len(Y):
            raise ValueError

        return True
    except:
        messagebox.showerror("Error", "Invalid X or Y input format")
        return False

def generate_markings(min_val, max_val, unit):
    markings = []
    value = min_val

    # Avoid floating point accumulation errors
    while value <= max_val + 1e-9:
        markings.append(round(value, 4))
        value += unit

    return markings

def generate_graph():
    global scale

    if not parse_data():
        return

    try:
        x_boxes = int(x_grid_entry.get())
        y_boxes = int(y_grid_entry.get())
    except:
        messagebox.showerror("Error", "Enter valid number of large & small boxes")
        return

    ax.clear()
    ax.plot(X, Y, "o-")

    # Axis Info (optional)
    axis_text = axis_entry.get().strip()
    if axis_text:
        try:
            axis_vals = list(map(float, axis_text.split(",")))
            ax.set_xlim(axis_vals[0], axis_vals[1])
            ax.set_ylim(axis_vals[2], axis_vals[3])
        except:
            messagebox.showerror("Error", "Axis format must be xmin,xmax,ymin,ymax")
            return


    min_x, max_x = ax.get_xlim()
    min_y, max_y = ax.get_ylim()

    unit_x = (max_x - min_x) / x_boxes
    unit_y = (max_y - min_y) / y_boxes

    small_x = unit_x / 10
    small_y = unit_y / 10

    scale = {
        "x": [unit_x, small_x, min_x],
        "y": [unit_y, small_y, min_y]
    }

    # ----- GRID CONFIGURATION -----

    # Major ticks (Large Squares)
    ax.set_xticks(np.arange(min_x, max_x + unit_x, unit_x))
    ax.set_yticks(np.arange(min_y, max_y + unit_y, unit_y))

    # Minor ticks (Small Squares)
    ax.set_xticks(np.arange(min_x, max_x + small_x, small_x), minor=True)
    ax.set_yticks(np.arange(min_y, max_y + small_y, small_y), minor=True)

    # Grid appearance
    ax.grid(which="major", linewidth=1)
    ax.grid(which="minor", linewidth=0.3)
    ax.tick_params(axis='x', labelrotation=90)

    # Make grid below data points
    ax.set_axisbelow(True)

    #Add scale info to the graph

    # Remove previous scale text if exists
    if hasattr(generate_graph, "scale_text"):
        generate_graph.scale_text.remove()
    scale_string = (
    f"Scale:\n"
    f"X → L: {round(unit_x,4)}  S: {round(small_x,5)}\n"
    f"Y → L: {round(unit_y,4)}  S: {round(small_y,5)}"
)
    generate_graph.scale_text = fig.text(
        0.89,0.96,                # Figure coordinates (outside axes)
        scale_string,
        ha='right',
        va='top',
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9)
)

    canvas.draw()


    output.delete(1.0, tk.END)

    output.insert(tk.END, "------ SCALE INFO ------\n", "center_bold")
    output.insert(tk.END,
                  f"X-axis: 1 Large sq. = {round(unit_x,4)}, "
                  f"1 Small sq. = {round(small_x,5)}\n")
    output.insert(tk.END,
                  f"Y-axis: 1 Large sq. = {round(unit_y,4)}, "
                  f"1 Small sq. = {round(small_y,5)}\n\n")
    
    # Generate markings
    x_markings = generate_markings(min_x, max_x, unit_x)
    y_markings = generate_markings(min_y, max_y, unit_y)

    output.insert(tk.END, "X-axis Markings:\n")
    output.insert(tk.END, f"{x_markings}\n\n")

    output.insert(tk.END, "Y-axis Markings:\n")
    output.insert(tk.END, f"{y_markings}\n\n")

    output.insert(tk.END, "------ POINT LOCATIONS ------\n", "center_bold")

    for i in range(len(X)):

        lx = int((X[i] - min_x) // unit_x)
        sx = int(((X[i] - min_x) % unit_x) // small_x)

        ly = int((Y[i] - min_y) // unit_y)
        sy = int(((Y[i] - min_y) % unit_y) // small_y)

        output.insert(
            tk.END,
            f"Point {i+1}:\n"
            f"   X → {lx} large sq and {sx} small sq\n"
            f"   Y → {ly} large sq and {sy} small sq\n\n"
        )


# ---------------- VALUE → GRAPH ----------------

def value_to_graph():

    if not scale:
        messagebox.showerror("Error", "Generate graph first")
        return

    axis = simpledialog.askstring("Axis", "Enter axis (x/y):")
    if axis is None:
        return

    axis = axis.lower().strip()
    if axis not in ["x", "y"]:
        messagebox.showerror("Error", "Axis must be x or y")
        return

    value_input = simpledialog.askstring("Value", "Enter value:")
    if value_input is None:
        return

    try:
        value = float(value_input)
    except:
        messagebox.showerror("Error", "Invalid numeric value")
        return

    unit, small, min_val = scale[axis]

    large = int((value - min_val) // unit)
    small_box = int(((value - min_val) % unit) // small)

    messagebox.showinfo(
        "Graph Location",
        f"Plot at:\n{large} large square and {small_box} small square"
    )


# ---------------- GRAPH → VALUE ----------------

def graph_to_value():

    if not scale:
        messagebox.showerror("Error", "Generate graph first")
        return

    axis = simpledialog.askstring("Axis", "Enter axis (x/y):")
    if axis not in ["x", "y"]:
        return

    large = int(simpledialog.askstring("Large", "Number of large boxes:"))
    small = int(simpledialog.askstring("Small", "Number of small boxes:"))

    unit, small_unit, min_val = scale[axis]

    value = large * unit + small * small_unit + min_val

    messagebox.showinfo("Calculated Value",
                        f"Value = {round(value,5)}")

#-----------------Helper function to "slope_from_triangle"--------------------

def clear_triangle():
    global triangle_artists

    for artist in triangle_artists:
        try:
            artist.remove()
        except:
            pass

    triangle_artists = []
    canvas.draw()

# ---------------- SLOPE USING BOX METHOD ----------------

def slope_from_triangle():

    if not scale:
        messagebox.showerror("Error", "Generate graph first")
        return

    # Perpendicular (Y)
    y2_l = int(simpledialog.askstring("Y2", "Y2 large boxes-perpendicular:"))
    y2_s = int(simpledialog.askstring("Y2", "Y2 small boxes-perpendicular:"))
    y1_l = int(simpledialog.askstring("Y1", "Y1 large boxes-perpendicular:"))
    y1_s = int(simpledialog.askstring("Y1", "Y1 small boxes-perpendicular:"))

    # Base (X)
    x2_l = int(simpledialog.askstring("X2", "X2 large boxes-base:"))
    x2_s = int(simpledialog.askstring("X2", "X2 small boxes-base:"))
    x1_l = int(simpledialog.askstring("X1", "X1 large boxes-base:"))
    x1_s = int(simpledialog.askstring("X1", "X1 small boxes-base:"))

    ux, sx, min_x = scale["x"]
    uy, sy, min_y = scale["y"]

    y2 = y2_l * uy + y2_s * sy + min_y
    y1 = y1_l * uy + y1_s * sy + min_y
    x2 = x2_l * ux + x2_s * sx + min_x
    x1 = x1_l * ux + x1_s * sx + min_x

    perp = y2 - y1
    base = x2 - x1

    if base == 0:
        messagebox.showerror("Error", "Base cannot be zero")
        return

    slope = perp / base

    # For refresh button
    global triangle_artists

    # Clear previous triangle automatically (optional safety)
    clear_triangle()

    # Base
    line1, = ax.plot([x1, x2], [y1, y1])
    # Perpendicular
    line2, = ax.plot([x2, x2], [y1, y2])
    # Hypotenuse
    line3, = ax.plot([x1, x2], [y1, y2])
    # Points
    points = ax.scatter([x1, x2], [y1, y2], color='red')

    triangle_artists = [line1, line2, line3, points]

    # Base label (midpoint of base)
    base_text = ax.text(
        (x1 + x2) / 2,
        y1,
        f"Base = {round(base,3)}",
        va='top'
    )

    # Perpendicular label
    perp_text = ax.text(
        x2,
        (y1 + y2) / 2,
        f"Perp = {round(perp,3)}",
        ha='left'
    )
    triangle_artists.extend([base_text, perp_text])

    canvas.draw()

    messagebox.showinfo("Slope Calculation",
                        f"tan(θ) = {round(perp,4)} / {round(base,4)}\n")


# ---------------- GUI SETUP ----------------
root = tk.Tk()
root.title("Physical Graph Plotting Assistant")
root.geometry("1100x650")

left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, padx=10, pady=10)

tk.Label(left_frame, text="X values (comma separated)").pack()
x_entry = tk.Entry(left_frame, width=45)
x_entry.pack()

tk.Label(left_frame, text="Y values (comma separated)").pack()
y_entry = tk.Entry(left_frame, width=45)
y_entry.pack()

tk.Label(left_frame, text="Number of X large boxes").pack()
x_grid_entry = tk.Entry(left_frame)
x_grid_entry.pack()

tk.Label(left_frame, text="Number of Y large boxes").pack()
y_grid_entry = tk.Entry(left_frame)
y_grid_entry.pack()

tk.Label(left_frame, text="Axis info [xmin,xmax,ymin,ymax] (optional)").pack()
axis_entry = tk.Entry(left_frame, width=45)
axis_entry.pack()

tk.Button(left_frame, text="Generate Graph & Locations",
          command=generate_graph).pack(pady=8)

tk.Button(left_frame, text="Value → Graph Location",
          command=value_to_graph).pack()

tk.Button(left_frame, text="Graph Location → Value",
          command=graph_to_value).pack(pady=5)

button_frame = tk.Frame(left_frame)
button_frame.pack(pady=5)

tk.Button(button_frame,
          text="Calculate Slope (Triangle Method)",
          command=slope_from_triangle).pack(side=tk.LEFT, padx=5)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(BASE_DIR,"assests", "refreshs.png")

refresh_icon = tk.PhotoImage(file=icon_path)
ref_img = tk.PhotoImage(file=icon_path)
tk.Button(button_frame,
          image = ref_img,
          command=clear_triangle).pack(side=tk.LEFT)

# ---- Scrollable Output Area ----
output_frame = tk.Frame(left_frame)
output_frame.pack(pady=10)

scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

output = tk.Text(output_frame, height=18, width=55,
                 yscrollcommand=scrollbar.set)

output.tag_configure("center_bold",
                     justify="center",
                     font=("Arial", 10, "bold"))

output.pack(side=tk.LEFT)
scrollbar.config(command=output.yview)

# -------- Graph Area --------

right_frame = tk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

fig = Figure(figsize=(6,5), dpi=100)
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

root.mainloop()