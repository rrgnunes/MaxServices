import os
import time
import subprocess
import schedule
import pathlib
import psutil
from funcoes.funcoes import *

name_script = os.path.basename(sys.argv[0]).replace('.py', '')

def is_running(script_path):
    script_name = os.path.basename(script_path)
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            if (proc.info['name'].lower() == 'python.exe') and any(script_name in cmd for cmd in proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as e:
            print_log(f'Erro ao verificar se servico esta em execução: {e}', name_script)
    return False

def run_script(script_path):
    if not is_running(script_path):
        try:
            subprocess.Popen(['python.exe', script_path])
            print_log(f"Executando {script_path}", name_script)
        except Exception as e:
            print_log(f"Erro ao executar {script_path}: {e}", name_script)
    else:
        print_log(f"{script_path} já está em execução.", name_script)

def setup_schedules():
    scripts_directory = pathlib.Path(__file__).parent
    scripts_directory = os.path.join(scripts_directory, 'threads')

    # Defina os scripts e seus agendamentos em segundos
    scripts = [
        {'path': os.path.join(scripts_directory, 'thread_backup_local.pyc'), 'interval': 3600},  # 1 hora
        {'path': os.path.join(scripts_directory, 'thread_atualiza_banco.pyc'), 'interval': 10},  # 10 segundos
        {'path': os.path.join(scripts_directory, 'thread_IBPT_NCM_CEST.pyc'), 'interval': 1800},  # 30 minutos
        {'path': os.path.join(scripts_directory, 'thread_servidor_socket.pyc'), 'interval': 0},  # Executa uma vez
        {'path': os.path.join(scripts_directory, 'thread_api_maxsuport.pyc'), 'interval': 0}, # Executa uma vez
        {'path': os.path.join(scripts_directory, 'thread_verifica_remoto.pyc'), 'interval': 15},  # 15 segundos
        {'path': os.path.join(scripts_directory, 'thread_zap_automato.pyc'), 'interval': 60},  # 1 minuto
        {'path': os.path.join(scripts_directory, 'thread_bloqueio.pyc'), 'interval': 5},  # 5 segundos
        {'path': os.path.join(scripts_directory, 'thread_replicador_envio.pyc'), 'interval': 10}, # 10 segundos
        {'path': os.path.join(scripts_directory, 'thread_replicador_retorno.pyc'), 'interval': 10}, # 10 segundos
        {'path': os.path.join(scripts_directory, 'thread_usuario.pyc'), 'interval': 10} # 10 segundos
    ]

    for script in scripts:
        if script['interval'] > 0:
            schedule.every(script['interval']).seconds.do(run_script, script['path'])
            print_log(f'Agendando o script: {script["path"]}', name_script)
        else:
            run_script(script['path'])  # Executa uma vez imediatamente

if __name__ == "__main__":
    setup_schedules()
    while True:
        schedule.run_pending()
        time.sleep(1)
