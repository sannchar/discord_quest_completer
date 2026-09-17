import os
import sys
import shutil
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

PRESET_GAMES = {
    "Arknights: Endfield": {
        "rel_dir": os.path.join("fake_games", "Arknights Endfield", "EndField Game"),
        "exe_name": "endfield.exe",
        "title": "Arknights: Endfield"
    },
    "Where Winds Meet": {
        "rel_dir": os.path.join("fake_games", "Where Winds Meet", "Engine", "Binaries", "Win64r"),
        "exe_name": "wwm.exe",
        "title": "Where Winds Meet"
    },
    "Marvel Rivals": {
        "rel_dir": os.path.join("fake_games", "MarvelRivals", "MarvelGame", "Marvel", "Binaries", "Win64"),
        "exe_name": "Marvel-Win64-Shipping.exe",
        "title": "Marvel Rivals"
    },
    "Genshin Impact": {
        "rel_dir": os.path.join("fake_games", "Genshin Impact"),
        "exe_name": "genshinimpact.exe",
        "title": "Genshin Impact"
    },
    "Honkai: Star Rail": {
        "rel_dir": os.path.join("fake_games", "Honkai Star Rail", "games"),
        "exe_name": "starrail.exe",
        "title": "Honkai: Star Rail"
    },
    "VALORANT": {
        "rel_dir": os.path.join("fake_games", "VALORANT", "live", "ShooterGame", "Binaries", "Win64"),
        "exe_name": "valorant-win64-shipping.exe",
        "title": "VALORANT"
    },
    "Fortnite": {
        "rel_dir": os.path.join("fake_games", "Fortnite", "FortniteGame", "Binaries", "Win64"),
        "exe_name": "fortniteclient-win64-shipping.exe",
        "title": "Fortnite"
    },
    "Cyberpunk 2077": {
        "rel_dir": os.path.join("fake_games", "Cyberpunk 2077", "bin", "x64"),
        "exe_name": "cyberpunk2077.exe",
        "title": "Cyberpunk 2077"
    },
    "League of Legends": {
        "rel_dir": os.path.join("fake_games", "League of Legends", "Game"),
        "exe_name": "league of legends.exe",
        "title": "League of Legends"
    },
    "Apex Legends": {
        "rel_dir": os.path.join("fake_games", "Apex Legends"),
        "exe_name": "r5apex_dx12.exe",
        "title": "Apex Legends"
    },
    "World of Warcraft": {
        "rel_dir": os.path.join("fake_games", "World of Warcraft", "_retail_"),
        "exe_name": "wow.exe",
        "title": "World of Warcraft"
    },
    "Counter-Strike 2": {
        "rel_dir": os.path.join("fake_games", "Counter-Strike Global Offensive", "game", "bin", "win64"),
        "exe_name": "cs2.exe",
        "title": "Counter-Strike 2"
    },
    "Dota 2": {
        "rel_dir": os.path.join("fake_games", "dota 2 beta", "game", "bin", "win64"),
        "exe_name": "dota2.exe",
        "title": "Dota 2"
    },
    "Пользовательская игра (.exe)": {
        "rel_dir": os.path.join("fake_games", "Custom"),
        "exe_name": "",
        "title": ""
    }
}

class DiscordQuestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Quest Runner")
        self.root.geometry("520x620")
        self.root.minsize(500, 600)
        self.root.configure(bg="#1E1F22")

        self.current_process = None
        self.is_running = False
        self.total_seconds = 16 * 60
        self.remaining_seconds = self.total_seconds
        self.timer_thread = None

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Custom ttk styles for dark theme
        style.configure("TCombobox", fieldbackground="#313338", background="#2B2D31",
                        foreground="#FFFFFF", arrowcolor="#F2F3F5")
        style.map("TCombobox", fieldbackground=[("readonly", "#313338")],
                  selectbackground=[("readonly", "#5865F2")],
                  selectforeground=[("readonly", "#FFFFFF")])

        style.configure("Horizontal.TProgressbar", troughcolor="#313338",
                        background="#5865F2", bordercolor="#1E1F22", lightcolor="#5865F2", darkcolor="#5865F2")

        # Header Frame
        header = tk.Frame(self.root, bg="#1E1F22")
        header.pack(fill=tk.X, padx=24, pady=(20, 10))

        title_lbl = tk.Label(header, text="Discord Quest Runner", font=("Segoe UI", 18, "bold"),
                             fg="#F2F3F5", bg="#1E1F22")
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(header, text="Безопасная эмуляция без сторонних exe и вирусов",
                                font=("Segoe UI", 9), fg="#949BA4", bg="#1E1F22")
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Main Card Frame
        card = tk.Frame(self.root, bg="#2B2D31", highlightthickness=1, highlightbackground="#35373C")
        card.pack(fill=tk.BOTH, expand=True, padx=24, pady=10)

        # 1. Game Selection
        sec1 = tk.Frame(card, bg="#2B2D31")
        sec1.pack(fill=tk.X, padx=20, pady=(16, 8))

        lbl1 = tk.Label(sec1, text="ВЫБЕРИТЕ ИГРУ", font=("Segoe UI", 9, "bold"),
                        fg="#B5BAC1", bg="#2B2D31")
        lbl1.pack(anchor="w", pady=(0, 6))

        self.game_var = tk.StringVar(value=list(PRESET_GAMES.keys())[0])
        self.game_combo = ttk.Combobox(sec1, textvariable=self.game_var,
                                       values=list(PRESET_GAMES.keys()), state="readonly",
                                       font=("Segoe UI", 11))
        self.game_combo.pack(fill=tk.X)
        self.game_combo.bind("<<ComboboxSelected>>", self.on_game_selected)

        # Custom game exe input (hidden by default)
        self.custom_frame = tk.Frame(card, bg="#2B2D31")
        self.custom_lbl = tk.Label(self.custom_frame, text="Имя файла игры (например, game.exe):",
                                   font=("Segoe UI", 9), fg="#B5BAC1", bg="#2B2D31")
        self.custom_lbl.pack(anchor="w", pady=(2, 4))
        self.custom_entry = tk.Entry(self.custom_frame, font=("Segoe UI", 10),
                                     bg="#313338", fg="#F2F3F5", insertbackground="#FFFFFF",
                                     relief="flat", highlightthickness=1, highlightbackground="#35373C")
        self.custom_entry.pack(fill=tk.X)

        # 2. Duration Selection
        sec2 = tk.Frame(card, bg="#2B2D31")
        sec2.pack(fill=tk.X, padx=20, pady=8)

        lbl2 = tk.Label(sec2, text="ДЛИТЕЛЬНОСТЬ", font=("Segoe UI", 9, "bold"),
                        fg="#B5BAC1", bg="#2B2D31")
        lbl2.pack(anchor="w", pady=(0, 6))

        dur_frame = tk.Frame(sec2, bg="#2B2D31")
        dur_frame.pack(fill=tk.X)

        self.duration_var = tk.IntVar(value=16)
        durations = [(16, "16 минут (Стандарт)"), (20, "20 минут (С запасом)"), (1, "1 мин (Тест)")]

        for mins, txt in durations:
            rb = tk.Radiobutton(dur_frame, text=txt, variable=self.duration_var, value=mins,
                                font=("Segoe UI", 9), fg="#F2F3F5", bg="#2B2D31",
                                selectcolor="#313338", activebackground="#2B2D31", activeforeground="#FFFFFF")
            rb.pack(side=tk.LEFT, padx=(0, 10))

        # 3. Status & Timer Display
        status_box = tk.Frame(card, bg="#1E1F22", highlightthickness=1, highlightbackground="#35373C")
        status_box.pack(fill=tk.X, padx=20, pady=(12, 10))

        self.status_title = tk.Label(status_box, text="Готов к запуску",
                                     font=("Segoe UI", 10, "bold"), fg="#57F287", bg="#1E1F22")
        self.status_title.pack(pady=(10, 2))

        self.timer_label = tk.Label(status_box, text="16:00", font=("Segoe UI", 28, "bold"),
                                    fg="#F2F3F5", bg="#1E1F22")
        self.timer_label.pack()

        self.progress = ttk.Progressbar(status_box, orient=tk.HORIZONTAL, mode="determinate",
                                       style="Horizontal.TProgressbar")
        self.progress.pack(fill=tk.X, padx=16, pady=(4, 8))
        self.progress["value"] = 0

        self.status_detail = tk.Label(status_box, text="Активируйте квест в Discord и нажмите «Запустить»",
                                      font=("Segoe UI", 8), fg="#949BA4", bg="#1E1F22", wraplength=420)
        self.status_detail.pack(pady=(0, 10))

        # 4. Action Buttons
        btn_frame = tk.Frame(card, bg="#2B2D31")
        btn_frame.pack(fill=tk.X, padx=20, pady=(8, 16))

        self.start_btn = tk.Button(btn_frame, text="▶  Запустить квест", font=("Segoe UI", 11, "bold"),
                                   bg="#5865F2", fg="#FFFFFF", activebackground="#4752C4", activeforeground="#FFFFFF",
                                   relief="flat", cursor="hand2", pady=8, command=self.toggle_run)
        self.start_btn.pack(fill=tk.X)

        # Footer Frame
        footer = tk.Frame(self.root, bg="#1E1F22")
        footer.pack(fill=tk.X, padx=24, pady=(5, 15))

        clean_btn = tk.Button(footer, text="🗑️ Очистить папку фейк-игр", font=("Segoe UI", 8),
                              bg="#2B2D31", fg="#949BA4", activebackground="#35373C", activeforeground="#F2F3F5",
                              relief="flat", cursor="hand2", command=self.cleanup_fake_games)
        clean_btn.pack(side=tk.LEFT)

        folder_btn = tk.Button(footer, text="📁 Открыть папку", font=("Segoe UI", 8),
                               bg="#2B2D31", fg="#949BA4", activebackground="#35373C", activeforeground="#F2F3F5",
                               relief="flat", cursor="hand2", command=self.open_folder)
        folder_btn.pack(side=tk.RIGHT)

    def on_game_selected(self, event=None):
        selected = self.game_var.get()
        if selected == "Пользовательская игра (.exe)":
            self.custom_frame.pack(fill=tk.X, padx=20, pady=(0, 8), before=self.start_btn.master)
        else:
            self.custom_frame.pack_forget()

    def toggle_run(self):
        if self.is_running:
            self.stop_process("Остановлено пользователем")
        else:
            self.start_process()

    def start_process(self):
        selected_game = self.game_var.get()
        info = PRESET_GAMES.get(selected_game, {})

        if selected_game == "Пользовательская игра (.exe)":
            custom_exe = self.custom_entry.get().strip()
            if not custom_exe:
                messagebox.showerror("Ошибка", "Введите имя исполняемого файла (например, game.exe)")
                return
            if not custom_exe.lower().endswith(".exe"):
                custom_exe += ".exe"
            rel_dir = os.path.join("fake_games", "Custom")
            exe_name = custom_exe
            game_title = custom_exe
        else:
            rel_dir = info["rel_dir"]
            exe_name = info["exe_name"]
            game_title = info["title"]

        target_dir = os.path.join(self.base_dir, rel_dir)
        os.makedirs(target_dir, exist_ok=True)
        target_exe = os.path.join(target_dir, exe_name)

        # Use system cmd.exe as dummy executable (100% clean, signed by Microsoft)
        source_exe = os.environ.get("COMSPEC", r"C:\Windows\System32\cmd.exe")
        try:
            shutil.copyfile(source_exe, target_exe)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать файл игры:\n{e}")
            return

        minutes = self.duration_var.get()
        self.total_seconds = minutes * 60
        self.remaining_seconds = self.total_seconds

        # Launch the dummy game
        cmd_args = [
            target_exe,
            "/k",
            f"title {game_title} & echo [Discord Quest] Эмуляция {game_title} запущена! & echo Окно закроется автоматически через {minutes} мин. & timeout /t {self.total_seconds} & exit"
        ]

        try:
            self.current_process = subprocess.Popen(cmd_args, creationflags=0)
        except Exception as e:
            messagebox.showerror("Ошибка запуска", f"Не удалось запустить процесс:\n{e}")
            return

        self.is_running = True
        self.start_btn.configure(text="⏹  Остановить досрочно", bg="#DA373C", activebackground="#A12828")
        self.status_title.configure(text=f"Эмуляция активна: {game_title}", fg="#5865F2")
        self.status_detail.configure(text="Процесс запущен. Discord должен показывать игру в активности.")
        self.game_combo.configure(state="disabled")

        # Start timer thread
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()

    def run_timer(self):
        while self.is_running and self.remaining_seconds > 0:
            time.sleep(1)
            self.remaining_seconds -= 1

            mins = self.remaining_seconds // 60
            secs = self.remaining_seconds % 60
            progress_pct = ((self.total_seconds - self.remaining_seconds) / self.total_seconds) * 100

            self.root.after(0, self.update_timer_display, f"{mins:02d}:{secs:02d}", progress_pct)

        if self.is_running and self.remaining_seconds <= 0:
            self.root.after(0, self.on_time_finished)

    def update_timer_display(self, text, pct):
        self.timer_label.configure(text=text)
        self.progress["value"] = pct

    def on_time_finished(self):
        self.stop_process("Квест выполнен! Награда готова в Discord.", completed=True)

    def stop_process(self, message="", completed=False):
        self.is_running = False

        if self.current_process:
            try:
                # Terminate process tree cleanly using taskkill
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.current_process.pid)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            self.current_process = None

        self.start_btn.configure(text="▶  Запустить квест", bg="#5865F2", activebackground="#4752C4")
        self.game_combo.configure(state="readonly")

        if completed:
            self.status_title.configure(text="🎉 Время вышло! Квест завершён", fg="#57F287")
            self.status_detail.configure(text="Зайдите в Discord -> Квесты и заберите награду!")
            self.timer_label.configure(text="00:00")
            self.progress["value"] = 100
            messagebox.showinfo("Готово!", "Время выполнения квеста истекло!\nПроверьте награду в Discord.")
        else:
            self.status_title.configure(text="Готов к запуску", fg="#57F287")
            self.status_detail.configure(text=message if message else "Процесс остановлен.")
            self.timer_label.configure(text="16:00")
            self.progress["value"] = 0

    def cleanup_fake_games(self):
        if self.is_running:
            messagebox.showwarning("Внимание", "Сначала остановите запущенную игру!")
            return
        fake_path = os.path.join(self.base_dir, "fake_games")
        if os.path.exists(fake_path):
            try:
                shutil.rmtree(fake_path)
                messagebox.showinfo("Очистка", "Папка с временными файлами игр успешно удалена.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить папку:\n{e}")
        else:
            messagebox.showinfo("Очистка", "Папка с играми уже пуста.")

    def open_folder(self):
        os.startfile(self.base_dir)

    def on_close(self):
        if self.is_running:
            if messagebox.askyesno("Выход", "Игра сейчас запущена. Остановить процесс и выйти?"):
                self.stop_process()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DiscordQuestApp(root)
    root.mainloop()
