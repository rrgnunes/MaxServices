import os
import time
import subprocess
import schedule
import pathlib
import psutil

def is_running(script_path):
    script_name = os.path.basename(script_path)
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        cmdline = proc.info['cmdline']
        if cmdline and script_name in cmdline:
            return True
    return False

def run_script(script_path):
    if not is_running(script_path):
        try:
            subprocess.Popen(['python', script_path])
            print(f"Executando {script_path}")
        except Exception as e:
            print(f"Erro ao executar {script_path}: {e}")
    else:
        print(f"{script_path} já está em execução.")

def setup_schedules():
    scripts_directory = pathlib.Path(__file__).parent

    # Defina os scripts e seus agendamentos em segundos
    scripts = [
        {'path': scripts_directory / 'thread_backup_local.py', 'interval': 3600},  # 1 hora
        {'path': scripts_directory / 'thread_atualiza_banco.py', 'interval': 10},  # 10 segundos
        {'path': scripts_directory / 'thread_IBPT_NCM_CEST.py', 'interval': 1800},  # 30 minutos
        {'path': scripts_directory / 'thread_servidor_socket.py', 'interval': 0},  # Executa uma vez
        {'path': scripts_directory / 'thread_verifica_remoto.py', 'interval': 5},  # 5 segundos
        {'path': scripts_directory / 'thread_xml_contador.py', 'interval': 600},  # 10 minutos
        {'path': scripts_directory / 'thread_zap_automato.py', 'interval': 60},  # 1 minuto
        {'path': scripts_directory / 'thread_bloqueio.py', 'interval': 5},  # 5 segundos
        {'path': scripts_directory / 'thread_replicador.py', 'interval': 10} # 10 segundos
    ]

    for script in scripts:
        if script['interval'] > 0:
            schedule.every(script['interval']).seconds.do(run_script, script['path'])
        else:
            run_script(script['path'])  # Executa uma vez imediatamente

if __name__ == "__main__":
    setup_schedules()
    
    while True:
        schedule.run_pending()
        time.sleep(1)
