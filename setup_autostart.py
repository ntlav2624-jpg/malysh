import os
import subprocess

boot_dir = os.path.expanduser("~/.termux/boot")
os.makedirs(boot_dir, exist_ok=True)

script_path = os.path.join(boot_dir, "start_malysh.sh")
home_dir = os.path.expanduser("~")

boot_script_content = f"""#!/data/data/com.termux/files/usr/bin/sh
cd {home_dir}
nohup python evolution_runtime.py > memory.log 2>&1 &
"""

with open(script_path, "w") as f:
    f.write(boot_script_content)

subprocess.run(["chmod", "+x", script_path], check=True)
print("[OK] Autostart configured successfully for Termux:Boot!")

# Также запустим рантайм прямо сейчас в фоне
subprocess.run(f"cd {home_dir} && nohup python evolution_runtime.py > memory.log 2>&1 &", shell=True, check=True)
print("[OK] Malysh runtime started in background daemon mode!")
