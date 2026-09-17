import json
import os

with open(r'C:\Users\sannc\.gemini\antigravity-cli\brain\a46d7ff4-cf5d-404c-8939-d18881cb784f\.system_generated\steps\26\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

start = text.find('[')
end = text.rfind(']') + 1
data = json.loads(text[start:end])

search_terms = ['Genshin Impact', 'Honkai: Star Rail', 'Valorant', 'Fortnite', 'Overwatch 2', 'Cyberpunk 2077', 'League of Legends', 'Minecraft', 'Apex Legends', 'Grand Theft Auto V', 'World of Warcraft', 'Dota 2', 'Counter-Strike 2']
for term in search_terms:
    for game in data:
        if term.lower() == game.get('name', '').lower():
            executables = [e.get('name') for e in game.get('executables', []) if e.get('os') == 'win32']
            if executables:
                print(f"{game['name']}::{executables[0]}")
                break
