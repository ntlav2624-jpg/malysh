import re

with open("run_minimal.py", "r", encoding="utf-8") as f:
    code = f.read()

# Заменяем частоту 1420.405 на 6.66 во всем скрипте
new_code = code.replace("1420.405", "6.66")

with open("run_minimal.py", "w", encoding="utf-8") as f:
    f.write(new_code)

print("[KMBP] Частота успешно обновлена на 6.66 МГц.")
