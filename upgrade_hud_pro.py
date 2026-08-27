with open("run_minimal.py", "r", encoding="utf-8") as f:
    code = f.read()

# Ультрасовременный киберпанк-интерфейс с вкладками, терминалом, метриками роя и динамическим управлением
pro_html = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Malysh v37.0 // KMBP HUD PRO</title>
    <style>
        :root {
            --bg-color: #05070a;
            --panel-bg: #0b1017;
            --border-color: #00ff66;
            --accent-green: #00ff66;
            --accent-dim: #003311;
            --text-color: #c0ffd0;
            --text-dim: #508060;
            --danger: #ff3333;
            --warning: #ffcc00;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Courier New', Courier, monospace;
            padding: 15px;
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        h1 { font-size: 1.4rem; color: var(--accent-green); text-shadow: 0 0 8px rgba(0,255,102,0.4); }
        .status-badge {
            background: var(--accent-dim);
            border: 1px solid var(--accent-green);
            padding: 4px 10px;
            font-size: 0.8rem;
            border-radius: 4px;
        }
        .grid-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }
        @media (min-width: 768px) {
            .grid-container { grid-template-columns: 1fr 1fr; }
            .full-width { grid-column: span 2; }
        }
        .panel {
            background-color: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 15px;
            box-shadow: 0 0 15px rgba(0,255,102,0.05);
        }
        .panel h3 {
            font-size: 1rem;
            color: var(--accent-green);
            margin-bottom: 12px;
            border-bottom: 1px dashed var(--accent-dim);
            padding-bottom: 6px;
        }
        form { display: flex; flex-direction: column; gap: 10px; }
        textarea, input[type="text"] {
            background: #020406;
            color: var(--accent-green);
            border: 1px solid var(--border-color);
            padding: 10px;
            font-family: monospace;
            resize: vertical;
            border-radius: 4px;
        }
        textarea:focus, input[type="text"]:focus {
            outline: none;
            box-shadow: 0 0 8px rgba(0,255,102,0.3);
        }
        .btn-group { display: flex; gap: 10px; }
        button, input[type="submit"] {
            background: var(--accent-green);
            color: #000;
            border: none;
            padding: 10px 15px;
            font-weight: bold;
            cursor: pointer;
            font-family: monospace;
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        button:hover, input[type="submit"]:hover {
            background: #00cc52;
            box-shadow: 0 0 10px rgba(0,255,102,0.5);
        }
        .btn-secondary {
            background: transparent;
            color: var(--accent-green);
            border: 1px solid var(--accent-green);
        }
        .btn-secondary:hover {
            background: var(--accent-dim);
            color: var(--accent-green);
        }
        pre {
            background: #020406;
            border: 1px solid var(--accent-dim);
            padding: 10px;
            white-space: pre-wrap;
            word-break: break-all;
            font-size: 0.85rem;
            max-height: 250px;
            overflow-y: auto;
            border-radius: 4px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .metric-card {
            background: #020406;
            border: 1px solid var(--text-dim);
            padding: 10px;
            text-align: center;
            border-radius: 4px;
        }
        .metric-value {
            font-size: 1.1rem;
            color: var(--accent-green);
            font-weight: bold;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <header>
        <h1>[MAL_V37.0 // KMBP HYPER-CORE]</h1>
        <div class="status-badge">СТАТУС: АКТИВЕН [PORT 8081]</div>
    </header>

    <div class="grid-container">
        <!-- Панель отправки интенций -->
        <div class="panel">
            <h3>[ИНПУЛЬС И СЕТЕВОЙ РОЙ]</h3>
            <form method="POST">
                <label for="intent" style="font-size: 0.85rem; color: var(--text-dim);">Введите новую задачу для роя агентов:</label>
                <textarea id="intent" name="intent" rows="4" placeholder="Например: Глубокий анализ квантового резонанса..." required></textarea>
                <div class="btn-group">
                    <input type="submit" value="ЗАПУСТИТЬ ИМПУЛЬС" style="flex: 2;">
                    <button type="reset" class="btn-secondary" style="flex: 1;">СБРОС</button>
                </div>
            </form>
        </div>

        <!-- Метрики экосистемы -->
        <div class="panel">
            <h3>[ТЕЛЕМЕТРИЯ И АГЕНТЫ]</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div style="font-size: 0.8rem; color: var(--text-dim);">АНАЛИТИК</div>
                    <div class="metric-value">ACTIVE</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 0.8rem; color: var(--text-dim);">КРИПТОГРАФ</div>
                    <div class="metric-value">ACTIVE</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 0.8rem; color: var(--text-dim);">ПОИСКОВИК</div>
                    <div class="metric-value">ONLINE</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: 0.8rem; color: var(--text-dim);">СИНТЕЗАТОР</div>
                    <div class="metric-value">READY</div>
                </div>
            </div>
            <div style="margin-top: 15px; font-size: 0.85rem; color: var(--text-dim);">
                • Подсистема Self-Healing: <span style="color: var(--accent-green);">Подтверждено</span><br>
                • Контекстный слой RAG: <span style="color: var(--accent-green);">SQLite DB Active</span>
            </div>
        </div>

        <!-- Результат выполнения -->
        <div class="panel full-width">
            <h3>[ВЫХОДНЫЕ ДАННЫЕ ЯДРА]</h3>
            <pre>{response_output}</pre>
        </div>

        <!-- История RAG памяти -->
        <div class="panel full-width">
            <h3>[АРХИВ ПАМЯТИ RAG (memory.db)]</h3>
            <pre>{history_output}</pre>
        </div>
    </div>
</body>
</html>
'''

# Заменяем старые блоки генерации страниц на новую профессиональную разметку
old_get_target = code[code.find("def do_GET(self):"):code.find("def do_POST(self):")]

new_get_code = f"""    def do_GET(self):
        import sqlite3
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        history_text = "Нет записей в памяти."
        try:
            conn = sqlite3.connect("memory.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, intent FROM rag_memory ORDER BY id DESC LIMIT 15")
            rows = cursor.fetchall()
            if rows:
                history_text = "\\n".join([f"ID: {{r[0]:<3}} | [{{r[1]}}] -> {{r[2]}}" for r in rows])
            conn.close()
        except Exception as e:
            history_text = f"Ошибка чтения БД: {{e}}"

        page_out = '''{pro_html}'''.replace('{{response_output}}', 'Система ожидает входящий импульс от оператора...').replace('{{history_output}}', history_text)
        self.wfile.write(page_out.encode('utf-8'))
"""

code = code.replace(old_get_target, new_get_code)

old_post_target = code[code.find("def do_POST(self):"):]

new_post_code = f"""    def do_POST(self):
        import sqlite3
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)
        intent = params.get('intent', [''])[0]

        advanced_out = self.execute_advanced_logic(intent)
        res_str = f"[Malysh v37.0 Hyper-Core Execution Report]\\n-> Интенция: {{intent}}\\n----------------------------------------\\n{{advanced_out}}"

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        history_text = ""
        try:
            conn = sqlite3.connect("memory.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, intent FROM rag_memory ORDER BY id DESC LIMIT 15")
            rows = cursor.fetchall()
            if rows:
                history_text = "\\n".join([f"ID: {{r[0]:<3}} | [{{r[1]}}] -> {{r[2]}}" for r in rows])
            conn.close()
        except Exception as e:
            history_text = f"Ошибка чтения БД: {{e}}"

        page_out = '''{pro_html}'''.replace('{{response_output}}', res_str).replace('{{history_output}}', history_text)
        self.wfile.write(page_out.encode('utf-8'))
"""

code = code.replace(old_post_target, new_post_code)

with open("run_minimal.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[KMBP] HUD PRO успешно развернут.")
