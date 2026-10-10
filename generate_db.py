import urllib.request
import json
import os

req = urllib.request.Request('https://discord.com/api/v9/applications/detectable', headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)
data = json.loads(response.read().decode('utf-8'))

seen_titles = set()

with open('GameDatabase.cs', 'w', encoding='utf-8') as out:
    out.write('namespace DiscordQuest\n{\n')
    out.write('    public static class GameDatabase\n    {\n')
    out.write('        public static string[] Data = new string[]\n        {\n')
    
    for game in data:
        title = game.get('name', '').strip()
        if not title: continue
        if title in seen_titles: continue
        
        execs = [e.get('name') for e in game.get('executables', []) if e.get('os') == 'win32']
        if not execs: continue
        
        exe_path = execs[0].strip()
        if exe_path.startswith('>'): exe_path = exe_path[1:]
        
        # Format for C# verbatim string
        title = title.replace('\"', '\"\"')
        exe_path = exe_path.replace('\"', '\"\"')
        
        out.write(f'            @\"{title}|{exe_path}\",\n')
        seen_titles.add(title)
        
    out.write('        };\n    }\n}\n')

print(f"Generated GameDatabase.cs with {len(seen_titles)} unique games.")
