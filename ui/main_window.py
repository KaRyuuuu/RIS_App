import customtkinter as ctk
from core.logic import additionner, message_bienvenue

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 🌙 Mode sombre
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # 📏 Taille et titre
        self.title("KaRyuu App - CTk Edition")
        self.geometry("600x400")

        # 🏷️ Titre principal
        self.label_title = ctk.CTkLabel(self, text="🐉 KaRyuu App", font=("Orbitron", 24, "bold"))
        self.label_title.pack(pady=20)

        # 🧮 Entrées
        self.entry_a = ctk.CTkEntry(self, placeholder_text="Nombre A")
        self.entry_b = ctk.CTkEntry(self, placeholder_text="Nombre B")
        self.entry_a.pack(pady=5)
        self.entry_b.pack(pady=5)

        # 🔘 Bouton de calcul
        self.button_calc = ctk.CTkButton(self, text="Additionner", command=self.calculer)
        self.button_calc.pack(pady=10)

        # 💬 Zone de résultat
        self.label_result = ctk.CTkLabel(self, text="Résultat : ", font=("Arial", 14))
        self.label_result.pack(pady=5)

        # 🌸 Bienvenue
        self.entry_nom = ctk.CTkEntry(self, placeholder_text="Ton nom")
        self.entry_nom.pack(pady=10)

        self.button_hello = ctk.CTkButton(self, text="Dire bonjour", command=self.saluer)
        self.button_hello.pack(pady=5)

        self.label_hello = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.label_hello.pack(pady=10)

    def calculer(self):
        """Récupère les valeurs et affiche la somme."""
        try:
            a = float(self.entry_a.get())
            b = float(self.entry_b.get())
            total = additionner(a, b)
            self.label_result.configure(text=f"Résultat : {total}")
        except ValueError:
            self.label_result.configure(text="❌ Entrées invalides")

    def saluer(self):
        """Affiche un message de bienvenue."""
        nom = self.entry_nom.get().strip() or "KaRyuu"
        msg = message_bienvenue(nom)
        self.label_hello.configure(text=msg)
