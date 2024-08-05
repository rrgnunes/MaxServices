import os
import sys
import time
import subprocess
import schedule
import concurrent.futures
import datetime
import pathlib
import servicemanager
import win32event
import win32service
import win32serviceutil


class PythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AgendadorMax"
    _svc_display_name_ = "AgendadorMax"
    _svc_description_ = "Executa serviços do sistema periodicamente."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        schedule.every(60).seconds.do(multi_exec, verifica_arquivos())
        while self.running:
            schedule.run_pending()
            time.sleep(1)


def out_file(msg):
    caminho_arquivo = pathlib.Path(__file__).parent
    with open(os.path.join(caminho_arquivo,'log' ,'agendador_max.txt'), 'a') as arq:
        arq.write(f'{datetime.datetime.now()} - {msg}\n')


def verifica_arquivos():
    caminho_arquivos = pathlib.Path(__file__).parent
    out_file(caminho_arquivos)
    arquivos = os.listdir(caminho_arquivos)
    comandos = []
    for arquivo in arquivos:
        if (arquivo.startswith('thread_')) and (arquivo.endswith('.py')):
            comandos.append(['pythonw.exe', f'{os.path.join(caminho_arquivos, arquivo)}'])
    return comandos


def is_running(script_name):
    try:
        result = subprocess.check_output(f'tasklist /FI "IMAGENAME eq pythonw.exe" /FI "WINDOWTITLE eq {script_name}"', shell=True)
        return script_name in result.decode('utf-8')
    except subprocess.CalledProcessError:
        return False


def exec_comando(comando):
    script_name = comando[1]
    if not is_running(script_name):
        try:
            out_file(f'Executando comando: {comando}')
            subprocess.check_call(comando)
        except Exception as e:
            out_file(f'Não foi possivel executar comando: "{comando}" motivo: "{e}"')
    else:
        out_file(f'Script já está em execução: {script_name}')


def multi_exec(comandos):
    try:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for comando in comandos:
                executor.submit(exec_comando, comando)
    except Exception as e:
        out_file(f'{e}')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PythonService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(PythonService)
