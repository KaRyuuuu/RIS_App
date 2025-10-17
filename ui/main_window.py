# ui/main_window.py (extrait)
import customtkinter as ctk
from ui.pages.settings import SettingsPage

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("KaRyuu Multi-App")
        self.geometry("1000x650")

        # ---- TabView principal
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # Onglets existants (exemples)
        tab_apps = self.tabs.add("Applications")
        tab_store = self.tabs.add("Boutique")

        # ✅ Nouvel onglet Paramètres
        tab_settings = self.tabs.add("Paramètres")
        self.settings_page = SettingsPage(tab_settings)
        self.settings_page.pack(fill="both", expand=True, padx=6, pady=6)
