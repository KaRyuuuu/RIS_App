"""
ui/pages/settings.py
Page "Paramètres" en CustomTkinter :
- Affiche la version de l'app
- Liste les serveurs (nom, url, statut, latence)
- Choix d'un serveur par défaut + sauvegarde
- Test/Rafraîchir sans bloquer l'UI (thread)
"""

from __future__ import annotations
import threading
import customtkinter as ctk

from core.app_info import get_app_version, read_settings, write_settings
from core.servers import load_servers, head_ping, Server

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # ==== En-tête ====
        self.label_title = ctk.CTkLabel(self, text="Paramètres", font=("Arial", 20, "bold"))
        self.label_title.pack(pady=(10, 4))

        # ---- Version de l'app
        version = get_app_version()
        self.label_version = ctk.CTkLabel(self, text=f"Version de l’application : {version}")
        self.label_version.pack(pady=(0, 10))

        # ==== Serveurs ====
        self.servers = load_servers()   # liste[Server]
        self.server_rows = []           # mémorise les widgets d'une ligne
        self.test_threads = []          # garder une ref pour éviter GC

        # Bloc choix par défaut
        self.default_server_label = ctk.CTkLabel(self, text="Serveur par défaut :")
        self.default_server_label.pack()

        # valeurs de combo = noms humains, mais on garde un mapping name->Server
        self.name_to_server = {s.name: s for s in self.servers}
        self.combo_default = ctk.CTkComboBox(
            self,
            values=list(self.name_to_server.keys()) if self.servers else ["(aucun)"]
        )
        self.combo_default.pack(pady=(0, 10))

        # Charger la préférence existante
        cfg = read_settings()
        saved = cfg.get("download", "default_server", fallback="")
        if saved and saved in self.name_to_server:
            self.combo_default.set(saved)
        elif self.servers:
            self.combo_default.set(self.servers[0].name)

        # Boutons en ligne
        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.pack(pady=6)
        self.btn_refresh = ctk.CTkButton(self.buttons_frame, text="Rafraîchir la liste", command=self.refresh_list)
        self.btn_refresh.grid(row=0, column=0, padx=5)
        self.btn_test = ctk.CTkButton(self.buttons_frame, text="Tester tous les serveurs", command=self.test_all_servers)
        self.btn_test.grid(row=0, column=1, padx=5)
        self.btn_save = ctk.CTkButton(self.buttons_frame, text="Enregistrer", command=self.save_default)
        self.btn_save.grid(row=0, column=2, padx=5)

        # En-têtes "table"
        self.header = ctk.CTkFrame(self)
        self.header.pack(fill="x", padx=4, pady=(8, 0))
        self._add_header(self.header, "Nom", 0)
        self._add_header(self.header, "URL", 1)
        self._add_header(self.header, "Statut", 2)
        self._add_header(self.header, "Latence (ms)", 3)
        self._add_header(self.header, "Action", 4)

        # Zone scrollable des serveurs
        self.scroll = ctk.CTkScrollableFrame(self, height=230)
        self.scroll.pack(fill="both", expand=True, padx=4, pady=6)

        # Remplir les lignes
        self.populate_rows()

    # ---------- Helpers UI ----------
    def _add_header(self, parent, text: str, col: int):
        lbl = ctk.CTkLabel(parent, text=text, font=("Arial", 12, "bold"))
        lbl.grid(row=0, column=col, padx=6, pady=4, sticky="w")

    def _make_row(self, parent, row_index: int, server: Server):
        """
        Crée une ligne 'table' pour un serveur.
        Chaque ligne = (nom, url, status_label, latency_label, bouton Tester)
        """
        name_label = ctk.CTkLabel(parent, text=server.name)
        name_label.grid(row=row_index, column=0, sticky="w", padx=6, pady=4)

        url_label = ctk.CTkLabel(parent, text=server.url)
        url_label.grid(row=row_index, column=1, sticky="w", padx=6, pady=4)

        status_label = ctk.CTkLabel(parent, text="—")
        status_label.grid(row=row_index, column=2, sticky="w", padx=6, pady=4)

        latency_label = ctk.CTkLabel(parent, text="—")
        latency_label.grid(row=row_index, column=3, sticky="w", padx=6, pady=4)

        def on_test_one():
            # Lance un thread pour ne pas bloquer l'UI
            t = threading.Thread(target=self._measure_server, args=(server, status_label, latency_label), daemon=True)
            t.start()
            self.test_threads.append(t)

        test_btn = ctk.CTkButton(parent, text="Tester", width=80, command=on_test_one)
        test_btn.grid(row=row_index, column=4, sticky="w", padx=6, pady=4)

        # Conserve la ligne pour maj si besoin
        self.server_rows.append((server, status_label, latency_label))

    # ---------- Actions ----------
    def populate_rows(self):
        # Nettoie l'ancien contenu
        for child in self.scroll.winfo_children():
            child.destroy()
        self.server_rows.clear()

        # Regénère
        for i, srv in enumerate(self.servers):
            self._make_row(self.scroll, i, srv)

    def refresh_list(self):
        # Reload depuis le JSON, puis repopulate
        self.servers = load_servers()
        self.name_to_server = {s.name: s for s in self.servers}
        # Met à jour la combo
        self.combo_default.configure(values=list(self.name_to_server.keys()) if self.servers else ["(aucun)"])
        if self.servers and self.combo_default.get() not in self.name_to_server:
            self.combo_default.set(self.servers[0].name)
        self.populate_rows()

    def test_all_servers(self):
        for (srv, status_label, latency_label) in self.server_rows:
            t = threading.Thread(target=self._measure_server, args=(srv, status_label, latency_label), daemon=True)
            t.start()
            self.test_threads.append(t)

    def save_default(self):
        name = self.combo_default.get().strip()
        if name and name in self.name_to_server:
            cfg = read_settings()
            cfg.set("download", "default_server", name)
            write_settings(cfg)
            ctk.CTkMessagebox(title="OK", message=f"Serveur par défaut enregistré : {name}", icon="check")
        else:
            ctk.CTkMessagebox(title="Erreur", message="Choix invalide.", icon="cancel")

    # ---------- Réseau (thread) ----------
    def _measure_server(self, server: Server, status_label: ctk.CTkLabel, latency_label: ctk.CTkLabel):
        # Met un état "en cours"
        self._set_status(status_label, "⏳ Test...", "normal")
        self._set_latency(latency_label, "—")

        ok, latency_ms, err = head_ping(server.url, timeout=5.0)
        if ok:
            self._set_status(status_label, "✅ OK", "green")
            self._set_latency(latency_label, f"{latency_ms:.0f}")
        else:
            self._set_status(status_label, f"❌ {err or 'Erreur'}", "red")
            self._set_latency(latency_label, "—")

    # ---------- UI thread-safe setters ----------
    def _set_status(self, label: ctk.CTkLabel, text: str, color: str = "normal"):
        # Utilise after() pour MAJ depuis le thread
        def _apply():
            kwargs = {"text": text}
            if color == "green":
                kwargs["text_color"] = "#6EE7B7"
            elif color == "red":
                kwargs["text_color"] = "#FCA5A5"
            else:
                kwargs["text_color"] = None
            label.configure(**kwargs)
        self.after(0, _apply)

    def _set_latency(self, label: ctk.CTkLabel, text: str):
        self.after(0, lambda: label.configure(text=text))
