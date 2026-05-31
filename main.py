import tkinter as tk
from src.ui.main_window import AcademicDataChecker


def on_closing(root):
    import matplotlib.pyplot as plt
    plt.close("all")
    root.destroy()




if __name__ == "__main__":
    root = tk.Tk()
    app = AcademicDataChecker(root)
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    root.mainloop()
