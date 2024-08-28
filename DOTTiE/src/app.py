import tkinter as tk
from tkinter import Toplevel, Label, Button, colorchooser, Frame
import ctypes
from ctypes import wintypes
import keyboard
import sys
if getattr(sys, 'frozen', False):
    import pyi_splash
class DotClickThroughApp:
    def __init__(self):
        self.root = tk.Tk()
        self.dot_radius = 10
        self.dot_x = self.root.winfo_screenwidth() // 2
        self.dot_y = self.root.winfo_screenheight() // 2
        self.dot_fill_color = 'aqua'  # Default fill color
        self.dot_ring_color = 'red'   # Default ring color
        self.dot = None
        self.dot_visible = True

    def run(self):
        self.setup_window()
        self.setup_dot()
        self.update_dot_position()
        self.setup_key_bindings()
        if getattr(sys, 'frozen', False):
            pyi_splash.close()
        self.root.mainloop()
        
    def setup_window(self):
        self.root.attributes('-fullscreen', False)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.attributes('-transparentcolor', 'black')
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        taskbar_height = self.get_taskbar_height()

        self.root.geometry(f"{screen_width}x{screen_height-taskbar_height}+0+0")
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        self.enable_aero(hwnd)
        self.make_click_through(hwnd)

    def get_taskbar_height(self):
        # This function uses the Windows API to get the taskbar height
        user32 = ctypes.windll.user32
        hWnd = user32.FindWindowW("Shell_TrayWnd", None)
        rect = wintypes.RECT()
        user32.GetWindowRect(hWnd, ctypes.byref(rect))
        return rect.bottom - rect.top

    def setup_dot(self):
        canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        self.dot = canvas.create_oval(
            self.dot_x - self.dot_radius, self.dot_y - self.dot_radius,
            self.dot_x + self.dot_radius, self.dot_y + self.dot_radius,
            fill=self.dot_fill_color, outline=self.dot_ring_color, width=5
        )

    def enable_aero(self, window_id):
        dwmapi = ctypes.windll.dwmapi
        DWMWA_TRANSITIONS_FORCEDISABLED = 3
        DWMWA_ALLOW_NCPAINT = 4
        DWM_BB_ENABLE = 1
        DWM_BB_BLURREGION = 2

        class DWM_BLURBEHIND(ctypes.Structure):
            _fields_ = [
                ("dwFlags", ctypes.wintypes.DWORD),
                ("fEnable", ctypes.wintypes.BOOL),
                ("hRgnBlur", ctypes.wintypes.HRGN),
                ("fTransitionOnMaximized", ctypes.wintypes.BOOL),
            ]

        bb = DWM_BLURBEHIND()
        bb.dwFlags = DWM_BB_ENABLE | DWM_BB_BLURREGION
        bb.fEnable = True
        bb.hRgnBlur = None
        bb.fTransitionOnMaximized = False
        dwmapi.DwmEnableBlurBehindWindow(window_id, ctypes.byref(bb))
        dwmapi.DwmSetWindowAttribute(window_id, DWMWA_TRANSITIONS_FORCEDISABLED, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))
        dwmapi.DwmSetWindowAttribute(window_id, DWMWA_ALLOW_NCPAINT, ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int))

    def make_click_through(self, window_id):
        style = ctypes.windll.user32.GetWindowLongW(window_id, -20)  # -20 corresponds to GWL_EXSTYLE
        style |= 0x80000 | 0x20  # WS_EX_LAYERED | WS_EX_TRANSPARENT
        ctypes.windll.user32.SetWindowLongW(window_id, -20, style)
        ctypes.windll.user32.SetLayeredWindowAttributes(window_id, 0, 0, 1)

    def exitCus(self):
        raise SystemExit

    def update_dot_position(self):
        if self.dot_visible:
            mouse_x, mouse_y = self.root.winfo_pointerxy()
            self.dot_x += (mouse_x - self.dot_x) * 0.1
            self.dot_y += (mouse_y - self.dot_y) * 0.1
            canvas = self.root.children["!canvas"]
            canvas.coords(self.dot, self.dot_x - self.dot_radius, self.dot_y - self.dot_radius,
                          self.dot_x + self.dot_radius, self.dot_y + self.dot_radius)
        self.root.after(10, self.update_dot_position)

    def toggle_dot_visibility(self, event=None):
        self.dot_visible = not self.dot_visible
        canvas = self.root.children["!canvas"]
        if self.dot_visible:
            canvas.itemconfig(self.dot, state="normal")
        else:
            canvas.itemconfig(self.dot, state="hidden")
    def toggle_settings_menu(self, event=None):
        if hasattr(self, 'settings_window') and self.settings_window.winfo_exists():
            self.settings_window.destroy()
            self.dot_visible = False  # Ensure the dot is visible when the settings window is closed
            self.toggle_dot_visibility()
        else:
            self.create_settings_menu()
            self.dot_visible = True  # Ensure the dot is hidden when the settings window is open
            self.toggle_dot_visibility()

    def create_settings_menu(self):
        self.settings_window = Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.protocol("WM_DELETE_WINDOW", self.toggle_settings_menu)  # Bind X button to toggle_settings_menu
        self.settings_window.wm_attributes("-topmost", True)

        # Main settings page
        main_frame = Frame(self.settings_window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        info_button = Button(main_frame, text="Info", command=self.show_advanced_settings)
        info_button.pack(pady=5)

        color_settings_button = Button(main_frame, text="Color Settings", command=self.show_general_settings)
        color_settings_button.pack(pady=5)

        exit_button = Button(main_frame, text="EXIT", command=self.exitCus)
        exit_button.pack(pady=5)

        # General settings frame (for color settings)
        self.general_settings_frame = Frame(self.settings_window)

        color_button = Button(self.general_settings_frame, text="Pick Fill Color", command=self.choose_dot_color)
        color_button.pack(pady=5)
        ring_button = Button(self.general_settings_frame, text="Pick Ring Color", command=self.choose_ring_color)
        ring_button.pack(pady=5)

        back_button_general = Button(self.general_settings_frame, text="Back", command=lambda: self.show_frame(main_frame))
        back_button_general.pack(pady=5)

        # Advanced settings frame (for info)
        self.advanced_settings_frame = Frame(self.settings_window)
        creds = Label(self.advanced_settings_frame, text="Credits to Butter ( /u/butter171 on guilded )")
        creds.pack(pady=5)
        creds2 = Label(self.advanced_settings_frame, text="This project is licensed under the GNU General Public License v3.0.")
        creds2.pack(pady=5)
        creds3 = Label(self.advanced_settings_frame, text="Version: 1.0")
        creds3.pack(pady=5)
        back_button_advanced = Button(self.advanced_settings_frame, text="Back", command=lambda: self.show_frame(main_frame))
        back_button_advanced.pack(pady=5)

    def show_frame(self, frame):
        frame.pack(fill=tk.BOTH, expand=True)
        for child in self.settings_window.winfo_children():
            if child != frame:
                child.pack_forget()

    def show_general_settings(self):
        self.show_frame(self.general_settings_frame)

    def show_advanced_settings(self):
        self.show_frame(self.advanced_settings_frame)

    def choose_dot_color(self):
        color = colorchooser.askcolor(title="Choose Dot Fill Color")
        if color[1]:
            self.dot_fill_color = color[1]
            canvas = self.root.children["!canvas"]
            canvas.itemconfig(self.dot, fill=self.dot_fill_color)

    def choose_ring_color(self):
        ringcolor = colorchooser.askcolor(title="Choose Dot Outer Color")
        if ringcolor[1]:
            self.dot_ring_color = ringcolor[1]
            canvas = self.root.children["!canvas"]
            canvas.itemconfig(self.dot, outline=self.dot_ring_color)

    def setup_key_bindings(self):
        keyboard.add_hotkey('ctrl+alt+d', self.toggle_dot_visibility)
        keyboard.add_hotkey('ctrl+alt+s', self.toggle_settings_menu)

if __name__ == "__main__":
    app = DotClickThroughApp()
    app.run()
