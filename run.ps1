$p = (Invoke-RestMethod -Uri 'https://raw.githubusercontent.com/sannchar/discord_quest_completer/main/Program.cs')
$d = (Invoke-RestMethod -Uri 'https://raw.githubusercontent.com/sannchar/discord_quest_completer/main/GameDatabase.cs')
$code = [string]::Concat($p, "
", $d)
Add-Type -TypeDefinition $code -ReferencedAssemblies 'System.Windows.Forms', 'System.Drawing'
[DiscordQuest.Program]::Main()
