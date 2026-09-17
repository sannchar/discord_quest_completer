# Ensure git and gh are available in the current session
$env:Path += ";C:\Program Files\Git\cmd;C:\Program Files\GitHub CLI\"

Write-Host "Проверка авторизации GitHub..."
gh auth status
if ($LASTEXITCODE -ne 0) {
    Write-Host "Пожалуйста, авторизуйтесь в GitHub. Открываю браузер..."
    gh auth login --web -p https
}

Write-Host "Инициализация репозитория..."
if (-Not (Test-Path .git)) {
    git init
    git add .
    git commit -m "Initial release with popular game presets"
} else {
    git add .
    git commit -m "Update presets and dist"
}

Write-Host "Создание репозитория на GitHub..."
gh repo create DiscordQuestRunner --public --source=. --push

Write-Host "Создание релиза..."
gh release create v1.0 dist\DiscordQuestRunner.zip --title "Discord Quest Runner v1.0" --notes "1-клик решение для квестов Discord без скачивания игр."

Write-Host "Готово! Ссылка на ваш репозиторий:"
gh repo view --web
