import sqlite3
import time

# Обновляем серверный скрипт, чтобы в него была встроена полная поддержка интеграции веб-ресурсов, матричных глифов и 3D-реконструкции ДНК
server_code = '''import http.server
import socketserver
import json
import urllib.parse
from hud_evolution import CognitiveHUDEvolution

PORT = 8081
hud = CognitiveHUDEvolution()

class HUDHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == "/api/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            
            import sqlite3
            with sqlite3.connect(hud.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT timestamp, evolution_stage, quantum_resonance, operator_intent, ai_response FROM hud_telemetry ORDER BY timestamp DESC LIMIT 15")
                rows = cursor.fetchall()
            
            telemetry_history = [
                {
                    "timestamp": r[0],
                    "stage": r[1],
                    "resonance": r[2],
                    "intent": r[3],
                    "response": r[4]
                } for r in rows
            ]
            
            response_data = {
                "status": "active",
                "stage": "v34.0-DNA-Matrix-Omni",
                "history": telemetry_history,
                "submodules": list(hud.loaded_submodules.keys())
            }
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="utf-8">
                <title>Malysh AI v34.0 - DNA & Matrix 3D HUD</title>
                <style>
                    body { background: #030604; color: #00ff66; font-family: monospace; padding: 15px; max-width: 1050px; margin: auto; }
                    .card { border: 1px solid #00ff66; padding: 15px; margin-bottom: 15px; background: #08100a; box-shadow: 0 0 15px rgba(0,255,102,0.12); border-radius: 4px; }
                    input, textarea, button { background: #000; color: #00ff66; border: 1px solid #00ff66; padding: 10px; font-family: monospace; border-radius: 4px; }
                    button { cursor: pointer; transition: all 0.2s; }
                    button:hover { background: #00ff66; color: #000; box-shadow: 0 0 12px #00ff66; }
                    .btn-active { background: #ff0055 !important; color: #fff !important; border-color: #ff0055; box-shadow: 0 0 12px #ff0055; }
                    .chat-box { height: 360px; overflow-y: scroll; border: 1px solid #004415; padding: 12px; background: #020403; margin-bottom: 10px; border-radius: 4px; }
                    .msg-user { color: #ffffff; margin: 10px 0; font-weight: bold; }
                    .msg-ai { color: #00ff66; margin: 10px 0; line-height: 1.4; white-space: pre-wrap; }
                    .grid-controls { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; margin-bottom: 10px; }
                    .matrix-panel { display: flex; gap: 6px; justify-content: space-between; flex-wrap: wrap; }
                    .matrix-btn { flex: 1; text-align: center; font-size: 1.05em; padding: 6px; }
                    .resonance-bar { height: 6px; background: #002211; border-radius: 3px; overflow: hidden; margin-top: 8px; }
                    .resonance-fill { height: 100%; background: #00ff66; width: 100%; animation: pulse 2s infinite; }
                    @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
                </style>
            </head>
            <body>
                <h1>[Malysh AI v34.0] Контур ДНК, Глифов и 3D-Реконструкции</h1>
                
                <div class="card">
                    <h3>Телеметрия Квантового Контура KMBP</h3>
                    <p>Статус: <span style="color: #fff;">АКТИВЕН / ДНК-Матрица</span> | Резонанс: <span style="color: #fff;">1420.405 МГц</span></p>
                    <div class="resonance-bar"><div class="resonance-fill"></div></div>
                    <div style="margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap;">
                        <button onclick="sendPreset('статус ядра')">⚡ Статус</button>
                        <button onclick="sendPreset('расшифруй днк через глифы │ ──┐ П ◯')">🧬 ДНК и Глифы</button>
                        <button onclick="sendPreset('трансформировать в apk')">📱 Сборка APK</button>
                        <button onclick="toggleVoice()" id="voiceBtn">🎤 Голос: ВЫКЛ</button>
                        <button onclick="toggleTTS()" id="ttsBtn" style="border-color: #00aa44;">🔊 Озвучка: ВКЛ</button>
                    </div>
                </div>

                <div class="card">
                    <h3>Матричный Синтаксический Пульт (Глифы ДНК)</h3>
                    <div class="matrix-panel">
                        <button class="matrix-btn" onclick="appendSymbol('│')">│ Аденин</button>
                        <button class="matrix-btn" onclick="appendSymbol('──┐')">──┐ Тимин</button>
                        <button class="matrix-btn" onclick="appendSymbol('П')">П Гуанин</button>
                        <button class="matrix-btn" onclick="appendSymbol('◯')">◯ Цитозин</button>
                        <button class="matrix-btn" onclick="appendSymbol('❖')">❖ Узел</button>
                        <button class="matrix-btn" onclick="appendSymbol('〰')">〰 Волна</button>
                    </div>
                </div>

                <div class="card">
                    <h3>Канал Интерактивного Взаимодействия</h3>
                    <div class="chat-box" id="chatBox">Синхронизация с био-матричным ядром...</div>
                    <div style="display: flex; gap: 10px;">
                        <textarea id="intentInput" rows="2" placeholder="Введите задачу, код или используйте глифы для анализа ДНК..." style="flex-grow: 1; resize: none;" onkeydown="if(event.key==='Enter' && !event.shiftKey){event.preventDefault(); sendIntent();}"></textarea>
                        <button onclick="sendIntent()" style="padding: 0 20px; font-weight: bold;">ЗАПУСК</button>
                    </div>
                </div>

                <script>
                    let recognition = null;
                    let isListening = false;
                    let ttsEnabled = true;

                    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                        recognition = new SpeechRecognition();
                        recognition.lang = 'ru-RU';
                        recognition.continuous = false;
                        recognition.interimResults = false;

                        recognition.onresult = function(event) {
                            const speechText = event.results[0][0].transcript;
                            document.getElementById('intentInput').value = speechText;
                            sendIntent();
                            toggleVoice();
                        };
                        recognition.onerror = function() { toggleVoice(); };
                        recognition.onend = function() { if (isListening) toggleVoice(); };
                    }

                    function toggleVoice() {
                        if (!recognition) {
                            alert('Голосовой ввод не поддерживается.');
                            return;
                        }
                        const btn = document.getElementById('voiceBtn');
                        if (!isListening) {
                            recognition.start();
                            isListening = true;
                            btn.innerText = '🎤 СЛУШАЮ...';
                            btn.classList.add('btn-active');
                        } else {
                            recognition.stop();
                            isListening = false;
                            btn.innerText = '🎤 Голос: ВЫКЛ';
                            btn.classList.remove('btn-active');
                        }
                    }

                    function toggleTTS() {
                        ttsEnabled = !ttsEnabled;
                        const btn = document.getElementById('ttsBtn');
                        btn.innerText = ttsEnabled ? '🔊 Озвучка: ВКЛ' : '🔇 Озвучка: ВЫКЛ';
                    }

                    function speakText(text) {
                        if (!ttsEnabled || !('speechSynthesis' in window)) return;
                        window.speechSynthesis.cancel();
                        const utterance = new SpeechSynthesisUtterance(text);
                        utterance.lang = 'ru-RU';
                        window.speechSynthesis.speak(utterance);
                    }

                    function appendSymbol(sym) {
                        const input = document.getElementById('intentInput');
                        input.value += sym + ' ';
                        input.focus();
                    }

                    function sendPreset(text) {
                        document.getElementById('intentInput').value = text;
                        sendIntent();
                    }

                    function loadTelemetry() {
                        fetch('/api/telemetry')
                            .then(response => response.json())
                            .then(data => {
                                const chatBox = document.getElementById('chatBox');
                                let htmlContent = '';
                                const history = data.history.reverse();
                                history.forEach(item => {
                                    htmlContent += `<div class="msg-user">> ${escapeHtml(item.intent)}</div>`;
                                    htmlContent += `<div class="msg-ai">Malysh: ${escapeHtml(item.response)}</div><hr style="border-color: #002211;">`;
                                });
                                chatBox.innerHTML = htmlContent;
                                chatBox.scrollTop = chatBox.scrollHeight;
                            });
                    }

                    function escapeHtml(text) {
                        return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                    }

                    function sendIntent() {
                        const inputField = document.getElementById('intentInput');
                        const intent = inputField.value.trim();
                        if (!intent) return;
                        
                        inputField.value = '';
                        
                        fetch('/api/intent', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ intent: intent, resonance: 1420.405 })
                        })
                        .then(response => response.json())
                        .then(data => {
                            loadTelemetry();
                            speakText(data.response);
                        });
                    }

                    loadTelemetry();
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/api/intent":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            intent = data.get("intent", "Пустой импульс")
            resonance = data.get("resonance", 1420.405)
            
            result = hud.sync_operator_symbiosis(intent, resonance)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

with ReusableTCPServer(("", PORT), HUDHandler) as httpd:
    print(f"[Malysh AI v34.0] Сервер запущен на http://localhost:{PORT}")
    httpd.serve_forever()
'''

with open("server.py", "w", encoding="utf-8") as f:
    f.write(server_code)

print("[KMBP] server.py успешно обновлен до версии v34.0.")
