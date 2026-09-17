<# :
@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Expression ([System.IO.File]::ReadAllText('%~f0'))"
exit /b
#>

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

[System.Windows.Forms.Application]::EnableVisualStyles()

$form = New-Object System.Windows.Forms.Form
$form.Text = "Discord Quest Runner"
$form.Size = New-Object System.Drawing.Size(480, 560)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#1E1F22")
$form.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#F2F3F5")

# Header
$lblTitle = New-Object System.Windows.Forms.Label
$lblTitle.Text = "Discord Quest Runner"
$lblTitle.Font = New-Object System.Drawing.Font("Segoe UI", 16, [System.Drawing.FontStyle]::Bold)
$lblTitle.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#F2F3F5")
$lblTitle.Location = New-Object System.Drawing.Point(24, 18)
$lblTitle.Size = New-Object System.Drawing.Size(420, 32)
$form.Controls.Add($lblTitle)

$lblSub = New-Object System.Windows.Forms.Label
$lblSub.Text = "Работает без Python и сторонних программ"
$lblSub.Font = New-Object System.Drawing.Font("Segoe UI", 9)
$lblSub.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#949BA4")
$lblSub.Location = New-Object System.Drawing.Point(26, 50)
$lblSub.Size = New-Object System.Drawing.Size(420, 20)
$form.Controls.Add($lblSub)

# Card Panel
$panel = New-Object System.Windows.Forms.Panel
$panel.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#2B2D31")
$panel.Location = New-Object System.Drawing.Point(24, 78)
$panel.Size = New-Object System.Drawing.Size(416, 380)
$form.Controls.Add($panel)

# Game Selection
$lblGame = New-Object System.Windows.Forms.Label
$lblGame.Text = "ВЫБЕРИТЕ ИГРУ:"
$lblGame.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
$lblGame.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#B5BAC1")
$lblGame.Location = New-Object System.Drawing.Point(16, 14)
$lblGame.Size = New-Object System.Drawing.Size(380, 20)
$panel.Controls.Add($lblGame)

$cbGame = New-Object System.Windows.Forms.ComboBox
$cbGame.DropDownStyle = [System.Windows.Forms.ComboBoxStyle]::DropDownList
$cbGame.Font = New-Object System.Drawing.Font("Segoe UI", 11)
$cbGame.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#313338")
$cbGame.ForeColor = [System.Drawing.Color]::White
$cbGame.Location = New-Object System.Drawing.Point(16, 36)
$cbGame.Size = New-Object System.Drawing.Size(384, 30)
$cbGame.Items.Add("Arknights: Endfield (endfield.exe)") | Out-Null
$cbGame.Items.Add("Where Winds Meet (wwm.exe)") | Out-Null
$cbGame.Items.Add("Своя игра (.exe)") | Out-Null
$cbGame.SelectedIndex = 0
$panel.Controls.Add($cbGame)

# Custom Game text box
$txtCustom = New-Object System.Windows.Forms.TextBox
$txtCustom.Font = New-Object System.Drawing.Font("Segoe UI", 10)
$txtCustom.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#313338")
$txtCustom.ForeColor = [System.Drawing.Color]::White
$txtCustom.Location = New-Object System.Drawing.Point(16, 72)
$txtCustom.Size = New-Object System.Drawing.Size(384, 26)
$txtCustom.Text = "game.exe"
$txtCustom.Visible = $false
$panel.Controls.Add($txtCustom)

$cbGame.Add_SelectedIndexChanged({
    if ($cbGame.SelectedIndex -eq 2) {
        $txtCustom.Visible = $true
    } else {
        $txtCustom.Visible = $false
    }
})

# Status Box
$statusBox = New-Object System.Windows.Forms.Panel
$statusBox.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#1E1F22")
$statusBox.Location = New-Object System.Drawing.Point(16, 110)
$statusBox.Size = New-Object System.Drawing.Size(384, 170)
$panel.Controls.Add($statusBox)

$lblStatus = New-Object System.Windows.Forms.Label
$lblStatus.Text = "Готов к запуску"
$lblStatus.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$lblStatus.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#57F287")
$lblStatus.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
$lblStatus.Location = New-Object System.Drawing.Point(10, 15)
$lblStatus.Size = New-Object System.Drawing.Size(364, 24)
$statusBox.Controls.Add($lblStatus)

$lblTimer = New-Object System.Windows.Forms.Label
$lblTimer.Text = "16:00"
$lblTimer.Font = New-Object System.Drawing.Font("Segoe UI", 28, [System.Drawing.FontStyle]::Bold)
$lblTimer.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#F2F3F5")
$lblTimer.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
$lblTimer.Location = New-Object System.Drawing.Point(10, 42)
$lblTimer.Size = New-Object System.Drawing.Size(364, 52)
$statusBox.Controls.Add($lblTimer)

$progressBar = New-Object System.Windows.Forms.ProgressBar
$progressBar.Location = New-Object System.Drawing.Point(20, 102)
$progressBar.Size = New-Object System.Drawing.Size(344, 14)
$progressBar.Maximum = 960
$progressBar.Value = 0
$statusBox.Controls.Add($progressBar)

$lblHint = New-Object System.Windows.Forms.Label
$lblHint.Text = "Примите квест в Discord и нажмите кнопку запуска"
$lblHint.Font = New-Object System.Drawing.Font("Segoe UI", 8)
$lblHint.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#949BA4")
$lblHint.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
$lblHint.Location = New-Object System.Drawing.Point(10, 126)
$lblHint.Size = New-Object System.Drawing.Size(364, 34)
$statusBox.Controls.Add($lblHint)

# Action Button
$btnAction = New-Object System.Windows.Forms.Button
$btnAction.Text = "▶  Запустить квест (16 мин)"
$btnAction.Font = New-Object System.Drawing.Font("Segoe UI", 11, [System.Drawing.FontStyle]::Bold)
$btnAction.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#5865F2")
$btnAction.ForeColor = [System.Drawing.Color]::White
$btnAction.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$btnAction.FlatAppearance.BorderSize = 0
$btnAction.Location = New-Object System.Drawing.Point(16, 305)
$btnAction.Size = New-Object System.Drawing.Size(384, 46)
$btnAction.Cursor = [System.Windows.Forms.Cursors]::Hand
$panel.Controls.Add($btnAction)

# Bottom links
$btnClean = New-Object System.Windows.Forms.Button
$btnClean.Text = "Очистить файлы фейк-игр"
$btnClean.Font = New-Object System.Drawing.Font("Segoe UI", 8)
$btnClean.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#2B2D31")
$btnClean.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#949BA4")
$btnClean.FlatStyle = [System.Windows.Forms.FlatStyle]::Flat
$btnClean.FlatAppearance.BorderSize = 0
$btnClean.Location = New-Object System.Drawing.Point(24, 470)
$btnClean.Size = New-Object System.Drawing.Size(180, 28)
$btnClean.Cursor = [System.Windows.Forms.Cursors]::Hand
$form.Controls.Add($btnClean)

# State variables
$script:isRunning = $false
$script:process = $null
$script:totalSec = 960
$script:remSec = 960

$timer = New-Object System.Windows.Forms.Timer
$timer.Interval = 1000

$timer.Add_Tick({
    if ($script:remSec -gt 0) {
        $script:remSec--
        $m = [math]::Floor($script:remSec / 60)
        $s = $script:remSec % 60
        $lblTimer.Text = "{0:D2}:{1:D2}" -f $m, $s
        $progressBar.Value = $script:totalSec - $script:remSec
    } else {
        $timer.Stop()
        Stop-Quest -Completed $true
    }
})

function Stop-Quest([bool]$Completed = $false) {
    $script:isRunning = $false
    $timer.Stop()
    
    if ($script:process -and !$script:process.HasExited) {
        try {
            taskkill /F /T /PID $script:process.Id | Out-Null
        } catch {}
    }
    $script:process = $null

    $btnAction.Text = "▶  Запустить квест (16 мин)"
    $btnAction.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#5865F2")
    $cbGame.Enabled = $true
    $txtCustom.Enabled = $true

    if ($Completed) {
        $lblStatus.Text = "🎉 Время вышло! Квест завершён"
        $lblStatus.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#57F287")
        $lblHint.Text = "Зайдите в Discord и заберите вашу награду!"
        $lblTimer.Text = "00:00"
        $progressBar.Value = $script:totalSec
        [System.Windows.Forms.MessageBox]::Show("Время выполнения квеста истекло!`nПроверьте награду в Discord.", "Квест выполнен!", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    } else {
        $lblStatus.Text = "Готов к запуску"
        $lblStatus.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#57F287")
        $lblHint.Text = "Процесс остановлен."
        $lblTimer.Text = "16:00"
        $progressBar.Value = 0
    }
}

$btnAction.Add_Click({
    if ($script:isRunning) {
        Stop-Quest -Completed $false
        return
    }

    $idx = $cbGame.SelectedIndex
    $baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    if (!$baseDir) { $baseDir = [System.AppDomain]::CurrentDomain.BaseDirectory }

    if ($idx -eq 0) {
        $relDir = "fake_games\Arknights Endfield\EndField Game"
        $exeName = "endfield.exe"
        $gameTitle = "Arknights: Endfield"
    } elseif ($idx -eq 1) {
        $relDir = "fake_games\Where Winds Meet\Engine\Binaries\Win64r"
        $exeName = "wwm.exe"
        $gameTitle = "Where Winds Meet"
    } else {
        $customName = $txtCustom.Text.Trim()
        if (!$customName) {
            [System.Windows.Forms.MessageBox]::Show("Введите имя .exe файла игры!", "Ошибка", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
            return
        }
        if (!$customName.ToLower().EndsWith(".exe")) { $customName += ".exe" }
        $relDir = "fake_games\Custom"
        $exeName = $customName
        $gameTitle = $customName
    }

    $targetDir = Join-Path $baseDir $relDir
    if (!(Test-Path $targetDir)) { New-Item -ItemType Directory -Force -Path $targetDir | Out-Null }
    $targetExe = Join-Path $targetDir $exeName

    $comSpec = [System.Environment]::GetEnvironmentVariable("COMSPEC")
    if (!$comSpec) { $comSpec = "C:\Windows\System32\cmd.exe" }
    Copy-Item -Path $comSpec -Destination $targetExe -Force

    $arg = "/k `"title $gameTitle & echo [Discord Quest] $gameTitle запущена... & echo Окно закроется через 16 минут. & timeout /t 960 & exit`""
    
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $targetExe
    $psi.Arguments = $arg
    $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Normal

    try {
        $script:process = [System.Diagnostics.Process]::Start($psi)
    } catch {
        [System.Windows.Forms.MessageBox]::Show("Не удалось запустить процесс:`n$_", "Ошибка", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        return
    }

    $script:isRunning = $true
    $script:totalSec = 960
    $script:remSec = 960
    $progressBar.Maximum = 960
    $progressBar.Value = 0

    $btnAction.Text = "⏹  Остановить досрочно"
    $btnAction.BackColor = [System.Drawing.ColorTranslator]::FromHtml("#DA373C")
    $lblStatus.Text = "Эмуляция активна: $gameTitle"
    $lblStatus.ForeColor = [System.Drawing.ColorTranslator]::FromHtml("#5865F2")
    $lblHint.Text = "Discord должен обнаружить игру. Не закрывайте открывшееся окно."
    $cbGame.Enabled = $false
    $txtCustom.Enabled = $false

    $timer.Start()
})

$btnClean.Add_Click({
    if ($script:isRunning) {
        [System.Windows.Forms.MessageBox]::Show("Сначала остановите запущенную игру!", "Внимание", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
        return
    }
    $baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    if (!$baseDir) { $baseDir = [System.AppDomain]::CurrentDomain.BaseDirectory }
    $fakeDir = Join-Path $baseDir "fake_games"
    if (Test-Path $fakeDir) {
        Remove-Item -Path $fakeDir -Recurse -Force
        [System.Windows.Forms.MessageBox]::Show("Папка фейк-игр успешно очищена.", "Очистка", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    } else {
        [System.Windows.Forms.MessageBox]::Show("Папка уже пуста.", "Очистка", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    }
})

$form.Add_FormClosing({
    if ($script:isRunning) {
        Stop-Quest -Completed $false
    }
})

$form.ShowDialog() | Out-Null
