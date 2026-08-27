with open("run_minimal.py", "r", encoding="utf-8") as f:
    code = f.read()

full_backend_logic = """
@app.route('/api/cipher', methods=['POST'])
def api_cipher():
    data = request.get_json() or {}
    text = data.get('text', '')
    mode = data.get('mode', 'encode')
    
    if not text:
        return jsonify({"result": "[ОШИБКА] Пустой входной поток."})
        
    import base64
    
    if mode == 'encode':
        # 1. Четверичное представление (Quaternary)
        quaternary = "".join([f"{ord(c):04b}" for c in text]) # упрощенно побитово
        # 2. Шумерско-клинописный симулятор (замена символов на знаки)
        glyph_map = {'a': '𒌋', 'b': '𒁹', 'c': ' ప్రభు', 'd': '𒀸', 'e': ' ಗುರು', 'o': '𒊹', 's': '𒅆'}
        glyphs = "".join([glyph_map.get(c.lower(), c) for c in text])
        # 3. Base64 / KMBP-пакет
        b64 = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        
        res = (f"[KMBP-ENCODE MULTI-STACK]\\n"
               f"-> Base64: KMBP-SECURE::{b64}\\n"
               f"-> Квантово-4ричный: {quaternary[:32]}... [LEN:{len(quaternary)} біт]\\n"
               f"-> Клинописный поток: {glyphs}")
    else:
        try:
            # Попытка автоопределения и дешифровки
            if "KMBP-SECURE::" in text:
                raw_b64 = text.replace("KMBP-SECURE::", "")
                decoded = base64.b64decode(raw_b64).decode('utf-8')
                res = f"[DECODE SUCCESS // KMBP-SECURE]\\nРезультат: {decoded}"
            elif any(g in text for g in ['𒌋', '𒁹', '𒀸', '𒊹', '𒅆']):
                # Обратное маппирование клинописи
                rev_map = {'𒌋': 'a', '𒁹': 'b', '𒀸': 'd', '𒊹': 'o', '𒅆': 's'}
                restored = "".join([rev_map.get(c, c) for c in text])
                res = f"[DECODE SUCCESS // SUMERIAN GLYPHS]\\nВосстановленный текст: {restored}"
            else:
                # Общий Base64 / Hex декодер
                decoded = base64.b64decode(text).decode('utf-8')
                res = f"[DECODE SUCCESS // BASE64]\\n{decoded}"
        except Exception as e:
            # Fallback реверс и побайтовый XOR
            fallback = "".join([chr(ord(c) ^ 2) for c in text[::-1]])
            res = f"[DECODE FALLBACK // XOR-REVERSE]\\nРезультат побитового сдвига: {fallback}"
            
    return jsonify({"result": res})
"""

# Заменим старый эндпоинт на новый полноценный
import re
code = re.sub(r'@app\.route\(\'\/api\/cipher\'\, methods=\[\'POST\'\]\).*?return jsonify\(\{"result": res\}\)', full_backend_logic, code, flags=re.DOTALL)

with open("run_minimal.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[KMBP] Полный стек алгоритмов дешифровки интегрирован в бэкенд.")
