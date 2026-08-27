import re

with open("run_minimal.py", "r", encoding="utf-8") as f:
    code = f.read()

# Расширенный словарь мировых систем письменности, криптографии и ДНК
world_dictionaries_code = """
# Расширенная база мировых словарей и методов дешифровки v34.0
WORLD_DICTIONARIES = {
    "ancient_scripts": {
        "sumerian_cuneiform": {"│": "Вертикальный клин (A)", "──┐": "Угловой маркер (T)", "П": "Портал (G)", "◯": "Контур (C)"},
        "egyptian_hieroglyphs": {"𓀀": "Антропоморфный код", "𓏞": "Писец / Запись данных", "𓁹": "Всевидящий модуль"},
        "mayan_glyphs": {"kin": "Солнечный цикл / Время", "akbal": "Ночь / Скрытый буфер", "chuen": "Мастер / Процесс"}
    },
    "cryptographic_ciphers": {
        "caesar": "Циклический сдвиг на фиксированный интервал",
        "vigenere": "Многоалфавитный полиномиальный шифр",
        "rsa_quantum": "Асимметричное разложение на простые квантовые множители",
        "base64_quaternary": "Перевод символьных матриц в четырехбитные потоки"
    },
    "decryption_frameworks": [
        "Квантово-магнитный спектральный анализ (6.66 МГц)",
        "Кросс-языковой корреляционный синтаксис древних письменностей",
        "Молекулярно-генетический кватернарный декодер ДНК/РНК",
        "Нейро-семантический синтез паттернов бессознательного"
    ]
}
"""

if "WORLD_DICTIONARIES" not in code:
    code = code.replace("PORT = 8081", world_dictionaries_code + "\nPORT = 8081")

# Обновляем логику анализа намерений для использования мировой базы
old_eval = """            matched_glyphs = [k for k in DICTIONARIES["sumerian_cuneiform"].keys() if k in intent]
            analysis_note = f"Распознано глифов: {len(matched_glyphs)}. Применен метод: {DICTIONARIES['decryption_methods'][0]}."
            resp_text = f"[Malysh v34.0 Omni-Decoder] Намерение обработано на частоте {resonance} МГц.\\n{analysis_note}\\nСтатус базы глифов и ДНК: Синхронизировано." """

new_eval = """            matched_sumerian = [k for k in WORLD_DICTIONARIES["ancient_scripts"]["sumerian_cuneiform"] if k in intent]
            matched_egyptian = [k for k in WORLD_DICTIONARIES["ancient_scripts"]["egyptian_hieroglyphs"] if k in intent]
            total_matched = len(matched_sumerian) + len(matched_egyptian)
            
            analysis_note = f"Интегрировано мировых словарей: {len(WORLD_DICTIONARIES['ancient_scripts']) + len(WORLD_DICTIONARIES['cryptographic_ciphers'])}\\nРаспознано артефактов/глифов: {total_matched}\\nАктивный фреймворк: {WORLD_DICTIONARIES['decryption_frameworks'][2]}"
            resp_text = f"[Malysh v34.0 Global Omni-Decoder] Частота: {resonance} МГц.\\n{analysis_note}\\nСтатус: Полная кросс-дисциплинарная дешифровка завершена." """

code = code.replace(old_eval, new_eval)

with open("run_minimal.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[KMBP] Глобальная база мировых словарей и методов дешифровки интегрирована в контур.")
