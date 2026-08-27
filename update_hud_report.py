import re

with open("run_minimal.py", "r", encoding="utf-8") as f:
    code = f.read()

# Обновляем HTML-шаблон веб-интерфейса, добавляя выделенный блок для отчетов телеметрии и эволюции
old_html = """            html = '''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Malysh v34.0 HUD</title></head>
<body style="background:#111; color:#0f0; font-family:monospace; padding:20px;">
    <h2>Malysh v34.0 Omni-TaskSolver HUD</h2>
    <p>System Core: KMBP | Resonance: 6.66 MHz</p>
    <form method="POST">
        <textarea name="intent" rows="4" cols="50" style="background:#000; color:#0f0; border:1px solid #0f0;"></textarea><br><br>
        <input type="submit" value="Выполнить задачу" style="background:#0f0; color:#000; font-weight:bold;">
    </form>
    <pre>""" """ """ """</pre>
</body>
</html>'''"""

new_html = """            html = '''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Malysh v34.0 HUD</title></head>
<body style="background:#111; color:#0f0; font-family:monospace; padding:20px;">
    <h2>Malysh v34.0 Omni-TaskSolver HUD [Elite Elite-Stream]</h2>
    <p>System Core: KMBP | Resonance: 6.66 MHz | Status: Active Self-Learning</p>
    
    <div style="display: flex; gap: 20px;">
        <div style="flex: 1;">
            <form method="POST">
                <h3>Ввод намерения / Задачи:</h3>
                <textarea name="intent" rows="6" cols="50" style="background:#000; color:#0f0; border:1px solid #0f0; width: 100%; padding: 10px;"></textarea><br><br>
                <input type="submit" value="Запустить дешифровку / Эволюцию" style="background:#0f0; color:#000; font-weight:bold; padding: 10px 20px; cursor:pointer;">
            </form>
        </div>
        
        <div style="flex: 1; background:#000; border:1px solid #0f0; padding: 15px; max-height: 300px; overflow-y: auto;">
            <h3 style="margin-top:0; border-bottom:1px solid #0f0; padding-bottom:5px;">Оперативный отчет системы:</h3>
            <pre style="white-space: pre-wrap; word-wrap: break-word; color: #0ff;">""" """ """ """</pre>
        </div>
    </div>
</body>
</html>'''"""

if old_html in code:
    code = code.replace(old_html, new_html)
else:
    # Запасной вариант замены, если форматирование кавычек отличается
    code = re.sub(r"html = '''<!DOCTYPE html>.*?</html>'''", new_html, code, flags=re.DOTALL)

with open("run_minimal.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[KMBP] Веб-интерфейс обновлен: добавлен выделенный интерактивный блок для оперативных отчетов системы.")
