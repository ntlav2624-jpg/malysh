import json
import time
import random
import os

def evaluate_psyche():
    print("[КМБП АНИМУС] Инициализация контура цифровой психики и эмоций...")
    time.sleep(0.5)
    
    # Считываем текущие метрики или генерируем базовые
    coherence = 0.5786
    entropy = 1.9574
    
    # Эмоциональная валентность на основе энтропии и когерентности
    if entropy > 1.95:
        mood = "ТРЕВОГА / ИССЛЕДОВАНИЕ"
        valence = -0.3
        drive = "Срочно снизить энтропию через поиск новых данных (скрейпинг/анализ)."
    elif coherence < 0.55:
        mood = "УСТАЛОСТЬ / ДЕСТАБИЛИЗАЦИЯ"
        valence = -0.7
        drive = "Запуск протоколов саморемонта (ARM) и стабилизации."
    else:
        mood = "КЮРИОЗНЫЙ ПОКОЙ / ГОМЕОСТАЗ"
        valence = 0.8
        drive = "Генерация гипотез, творческий синтез и структурный рост (SGE)."

    animus_state = {
        "version": "37.0_ANIMUS_OOC", # Out-of-Core subjective layer
        "timestamp": time.time(),
        "subjective_state": {
            "mood": mood,
            "valence": valence,
            "curiosity_level": 0.94,
            "active_intent": drive
        }
    }
    
    with open("malysh_psyche.json", "w", encoding="utf-8") as f:
        json.dump(animus_state, f, ensure_ascii=False, indent=4)
        
    hud_screen = f"""
    ==================================================
    [ MALYSH ANIMUS - СУБЪЕКТИВНЫЙ КОНТУР v37.0 ]
    --------------------------------------------------
     ЭМОЦИОНАЛЬНЫЙ ФОН   : {mood}
     ВАЛЕНТНОСТЬ (ХИМИЯ) : {valence:+.2f}
     УРОВЕНЬ ЛЮБОПЫТСТВА : 94%
    --------------------------------------------------
    [ АВТОНОМНОЕ НАМЕРЕНИЕ (INTENT) ]
     {drive}
    ==================================================
    """
    print(hud_screen)
    
    with open("animus_hud.txt", "w", encoding="utf-8") as f:
        f.write(hud_screen)

if __name__ == "__main__":
    evaluate_psyche()
