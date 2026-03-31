import tkinter as tk
from src.ui.home_ui import ArcanaHomeApp


def main():
    root = tk.Tk()
    app = ArcanaHomeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()