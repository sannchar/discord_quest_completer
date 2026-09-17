using System;
using System.IO;
using System.Drawing;
using System.Diagnostics;
using System.Windows.Forms;
using System.Collections.Generic;

namespace DiscordQuest
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            AppDomain.CurrentDomain.UnhandledException += (s, e) => {
                File.WriteAllText("crash.log", e.ExceptionObject.ToString());
            };
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }

    public class Preset
    {
        public string Title { get; set; }
        public string ExeName { get; set; }
        public string RelDir { get; set; }

        public Preset(string title, string exeName, string relDir)
        {
            Title = title;
            ExeName = exeName;
            RelDir = relDir;
        }

        public override string ToString()
        {
            return Title;
        }
    }

    public class MainForm : Form
    {
        private ComboBox cbGame;
        private TextBox txtCustom;
        private Label lblStatus;
        private Label lblTimer;
        private Label lblHint;
        private ProgressBar progressBar;
        private Button btnAction;
        private Timer questTimer;

        private bool isRunning = false;
        private Process runningProcess = null;
        private int totalSeconds = 960;
        private int remainingSeconds = 960;

        public MainForm()
        {
            this.Text = "Discord Quest Runner";
            this.Size = new Size(480, 560);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.BackColor = ColorTranslator.FromHtml("#1E1F22");
            this.ForeColor = ColorTranslator.FromHtml("#F2F3F5");

            // Header
            Label lblTitle = new Label();
            lblTitle.Text = "Discord Quest Runner";
            lblTitle.Font = new Font("Segoe UI", 16, FontStyle.Bold);
            lblTitle.ForeColor = ColorTranslator.FromHtml("#F2F3F5");
            lblTitle.Location = new Point(24, 18);
            lblTitle.Size = new Size(420, 32);
            this.Controls.Add(lblTitle);

            Label lblSub = new Label();
            lblSub.Text = "Работает без Python и сторонних библиотек";
            lblSub.Font = new Font("Segoe UI", 9);
            lblSub.ForeColor = ColorTranslator.FromHtml("#949BA4");
            lblSub.Location = new Point(26, 50);
            lblSub.Size = new Size(420, 20);
            this.Controls.Add(lblSub);

            // Card Panel
            Panel panel = new Panel();
            panel.BackColor = ColorTranslator.FromHtml("#2B2D31");
            panel.Location = new Point(24, 78);
            panel.Size = new Size(416, 380);
            this.Controls.Add(panel);

            // Game Selection
            Label lblGame = new Label();
            lblGame.Text = "ВЫБЕРИТЕ ИГРУ:";
            lblGame.Font = new Font("Segoe UI", 9, FontStyle.Bold);
            lblGame.ForeColor = ColorTranslator.FromHtml("#B5BAC1");
            lblGame.Location = new Point(16, 14);
            lblGame.Size = new Size(380, 20);
            panel.Controls.Add(lblGame);

            cbGame = new ComboBox();
            cbGame.DropDownStyle = ComboBoxStyle.DropDown;
            cbGame.Font = new Font("Segoe UI", 11);
            cbGame.BackColor = ColorTranslator.FromHtml("#313338");
            cbGame.ForeColor = Color.White;
            cbGame.Location = new Point(16, 36);
            cbGame.Size = new Size(384, 30);

            cbGame.AutoCompleteSource = AutoCompleteSource.ListItems;
            cbGame.AutoCompleteMode = AutoCompleteMode.SuggestAppend;
            
            cbGame.BeginUpdate();
            // Popular games at the top for convenience
            cbGame.Items.Add(new Preset("Genshin Impact", "genshinimpact.exe", Path.Combine("fake_games", "Genshin Impact")));
            cbGame.Items.Add(new Preset("Honkai: Star Rail", "starrail.exe", Path.Combine("fake_games", "Honkai Star Rail", "games")));
            cbGame.Items.Add(new Preset("VALORANT", "valorant-win64-shipping.exe", Path.Combine("fake_games", "VALORANT", "live", "ShooterGame", "Binaries", "Win64")));
            cbGame.Items.Add(new Preset("Fortnite", "fortniteclient-win64-shipping.exe", Path.Combine("fake_games", "Fortnite", "FortniteGame", "Binaries", "Win64")));
            cbGame.Items.Add(new Preset("Cyberpunk 2077", "cyberpunk2077.exe", Path.Combine("fake_games", "Cyberpunk 2077", "bin", "x64")));
            cbGame.Items.Add(new Preset("Dota 2", "dota2.exe", Path.Combine("fake_games", "dota 2 beta", "game", "bin", "win64")));
            cbGame.Items.Add(new Preset("Своя игра (.exe)", "", Path.Combine("fake_games", "Custom")));
            
            List<Preset> presets = new List<Preset>(10500);
            foreach (string entry in GameDatabase.Data)
            {
                int pipeIndex = entry.LastIndexOf('|');
                if (pipeIndex > 0)
                {
                    string title = entry.Substring(0, pipeIndex);
                    string exePath = entry.Substring(pipeIndex + 1);
                    
                    exePath = exePath.Replace('/', '\\');
                    
                    try 
                    {
                        string exeName = Path.GetFileName(exePath);
                        string safeTitle = string.Join("_", title.Split(Path.GetInvalidFileNameChars()));
                        string relDir = Path.Combine("fake_games", safeTitle, Path.GetDirectoryName(exePath));
                        
                        presets.Add(new Preset(title, exeName, relDir));
                    }
                    catch 
                    {
                    }
                }
            }
            cbGame.Items.AddRange(presets.ToArray());
            cbGame.EndUpdate();

            cbGame.SelectedIndex = 0;
            cbGame.SelectedIndexChanged += CbGame_SelectedIndexChanged;
            panel.Controls.Add(cbGame);

            txtCustom = new TextBox();
            txtCustom.Font = new Font("Segoe UI", 10);
            txtCustom.BackColor = ColorTranslator.FromHtml("#313338");
            txtCustom.ForeColor = Color.White;
            txtCustom.Location = new Point(16, 72);
            txtCustom.Size = new Size(384, 26);
            txtCustom.Text = "game.exe";
            txtCustom.Visible = false;
            panel.Controls.Add(txtCustom);

            // Status Box
            Panel statusBox = new Panel();
            statusBox.BackColor = ColorTranslator.FromHtml("#1E1F22");
            statusBox.Location = new Point(16, 110);
            statusBox.Size = new Size(384, 170);
            panel.Controls.Add(statusBox);

            lblStatus = new Label();
            lblStatus.Text = "Готов к запуску";
            lblStatus.Font = new Font("Segoe UI", 10, FontStyle.Bold);
            lblStatus.ForeColor = ColorTranslator.FromHtml("#57F287");
            lblStatus.TextAlign = ContentAlignment.MiddleCenter;
            lblStatus.Location = new Point(10, 15);
            lblStatus.Size = new Size(364, 24);
            statusBox.Controls.Add(lblStatus);

            lblTimer = new Label();
            lblTimer.Text = "16:00";
            lblTimer.Font = new Font("Segoe UI", 28, FontStyle.Bold);
            lblTimer.ForeColor = ColorTranslator.FromHtml("#F2F3F5");
            lblTimer.TextAlign = ContentAlignment.MiddleCenter;
            lblTimer.Location = new Point(10, 42);
            lblTimer.Size = new Size(364, 52);
            statusBox.Controls.Add(lblTimer);

            progressBar = new ProgressBar();
            progressBar.Location = new Point(20, 102);
            progressBar.Size = new Size(344, 14);
            progressBar.Maximum = 960;
            progressBar.Value = 0;
            statusBox.Controls.Add(progressBar);

            lblHint = new Label();
            lblHint.Text = "Примите квест в Discord и нажмите кнопку запуска";
            lblHint.Font = new Font("Segoe UI", 8);
            lblHint.ForeColor = ColorTranslator.FromHtml("#949BA4");
            lblHint.TextAlign = ContentAlignment.MiddleCenter;
            lblHint.Location = new Point(10, 126);
            lblHint.Size = new Size(364, 34);
            statusBox.Controls.Add(lblHint);

            // Action Button
            btnAction = new Button();
            btnAction.Text = "▶  Запустить квест (16 мин)";
            btnAction.Font = new Font("Segoe UI", 11, FontStyle.Bold);
            btnAction.BackColor = ColorTranslator.FromHtml("#5865F2");
            btnAction.ForeColor = Color.White;
            btnAction.FlatStyle = FlatStyle.Flat;
            btnAction.FlatAppearance.BorderSize = 0;
            btnAction.Location = new Point(16, 305);
            btnAction.Size = new Size(384, 46);
            btnAction.Cursor = Cursors.Hand;
            btnAction.Click += BtnAction_Click;
            panel.Controls.Add(btnAction);

            // Cleanup button
            Button btnClean = new Button();
            btnClean.Text = "Очистить файлы фейк-игр";
            btnClean.Font = new Font("Segoe UI", 8);
            btnClean.BackColor = ColorTranslator.FromHtml("#2B2D31");
            btnClean.ForeColor = ColorTranslator.FromHtml("#949BA4");
            btnClean.FlatStyle = FlatStyle.Flat;
            btnClean.FlatAppearance.BorderSize = 0;
            btnClean.Location = new Point(24, 470);
            btnClean.Size = new Size(180, 28);
            btnClean.Cursor = Cursors.Hand;
            btnClean.Click += BtnClean_Click;
            this.Controls.Add(btnClean);

            questTimer = new Timer();
            questTimer.Interval = 1000;
            questTimer.Tick += QuestTimer_Tick;

            this.FormClosing += MainForm_FormClosing;
        }

        private void CbGame_SelectedIndexChanged(object sender, EventArgs e)
        {
            Preset selected = cbGame.SelectedItem as Preset;
            txtCustom.Visible = (selected != null && selected.Title == "Своя игра (.exe)");
        }

        private void BtnAction_Click(object sender, EventArgs e)
        {
            if (isRunning)
            {
                StopQuest(false);
            }
            else
            {
                StartQuest();
            }
        }

        private void StartQuest()
        {
            string appDir = AppDomain.CurrentDomain.BaseDirectory;
            string relDir = "";
            string exeName = "";
            string gameTitle = "";

            Preset selectedPreset = cbGame.SelectedItem as Preset;
            if (selectedPreset == null)
            {
                MessageBox.Show("Пожалуйста, выберите игру из выпадающего списка!", "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (selectedPreset.Title == "Своя игра (.exe)")
            {
                string custom = txtCustom.Text.Trim();
                if (string.IsNullOrEmpty(custom))
                {
                    MessageBox.Show("Введите имя .exe файла игры!", "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }
                if (!custom.ToLower().EndsWith(".exe")) custom += ".exe";
                relDir = selectedPreset.RelDir;
                exeName = custom;
                gameTitle = custom;
            }
            else
            {
                relDir = selectedPreset.RelDir;
                exeName = selectedPreset.ExeName;
                gameTitle = selectedPreset.Title;
            }

            string targetDir = Path.Combine(appDir, relDir);
            Directory.CreateDirectory(targetDir);
            string targetExe = Path.Combine(targetDir, exeName);

            string cmdPath = Environment.GetEnvironmentVariable("COMSPEC");
            if (string.IsNullOrEmpty(cmdPath)) cmdPath = @"C:\Windows\System32\cmd.exe";

            try
            {
                File.Copy(cmdPath, targetExe, true);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Не удалось создать файл игры:\n" + ex.Message, "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            totalSeconds = 960;
            remainingSeconds = totalSeconds;

            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = targetExe;
            psi.Arguments = string.Format("/k \"title {0} & echo [Discord Quest] {0} запущена... & echo Окно закроется через 16 минут. & timeout /t {1} & exit\"", gameTitle, totalSeconds);
            psi.WindowStyle = ProcessWindowStyle.Normal;

            try
            {
                runningProcess = Process.Start(psi);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Не удалось запустить процесс:\n" + ex.Message, "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            isRunning = true;
            btnAction.Text = "⏹  Остановить досрочно";
            btnAction.BackColor = ColorTranslator.FromHtml("#DA373C");
            lblStatus.Text = "Эмуляция активна: " + gameTitle;
            lblStatus.ForeColor = ColorTranslator.FromHtml("#5865F2");
            lblHint.Text = "Discord должен обнаружить игру. Не закрывайте открывшееся окно.";
            cbGame.Enabled = false;
            txtCustom.Enabled = false;

            progressBar.Maximum = totalSeconds;
            progressBar.Value = 0;
            questTimer.Start();
        }

        private void QuestTimer_Tick(object sender, EventArgs e)
        {
            if (remainingSeconds > 0)
            {
                remainingSeconds--;
                int m = remainingSeconds / 60;
                int s = remainingSeconds % 60;
                lblTimer.Text = string.Format("{0:D2}:{1:D2}", m, s);
                progressBar.Value = totalSeconds - remainingSeconds;
            }
            else
            {
                questTimer.Stop();
                StopQuest(true);
            }
        }

        private void StopQuest(bool completed)
        {
            isRunning = false;
            questTimer.Stop();

            if (runningProcess != null)
            {
                try
                {
                    Process.Start(new ProcessStartInfo("taskkill", string.Format("/F /T /PID {0}", runningProcess.Id))
                    {
                        CreateNoWindow = true,
                        UseShellExecute = false
                    });
                }
                catch { }
                runningProcess = null;
            }

            btnAction.Text = "▶  Запустить квест (16 мин)";
            btnAction.BackColor = ColorTranslator.FromHtml("#5865F2");
            cbGame.Enabled = true;
            txtCustom.Enabled = true;

            if (completed)
            {
                lblStatus.Text = "🎉 Время вышло! Квест завершён";
                lblStatus.ForeColor = ColorTranslator.FromHtml("#57F287");
                lblHint.Text = "Зайдите в Discord и заберите вашу награду!";
                lblTimer.Text = "00:00";
                progressBar.Value = totalSeconds;
                MessageBox.Show("Время выполнения квеста истекло!\nПроверьте награду в Discord.", "Квест выполнен!", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            else
            {
                lblStatus.Text = "Готов к запуску";
                lblStatus.ForeColor = ColorTranslator.FromHtml("#57F287");
                lblHint.Text = "Процесс остановлен.";
                lblTimer.Text = "16:00";
                progressBar.Value = 0;
            }
        }

        private void BtnClean_Click(object sender, EventArgs e)
        {
            if (isRunning)
            {
                MessageBox.Show("Сначала остановите запущенную игру!", "Внимание", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            string fakeDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "fake_games");
            if (Directory.Exists(fakeDir))
            {
                try
                {
                    Directory.Delete(fakeDir, true);
                    MessageBox.Show("Папка фейк-игр успешно очищена.", "Очистка", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Ошибка при удалении:\n" + ex.Message, "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
            else
            {
                MessageBox.Show("Папка уже пуста.", "Очистка", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (isRunning)
            {
                StopQuest(false);
            }
        }
    }
}
