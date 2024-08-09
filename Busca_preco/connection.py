import socket
import time
import psutil
import os
import win32serviceutil
import win32service
import win32event
import servicemanager
from terminal import await_terminal_query, check_terminal_alive, set_always_on
from commands import Receive_Cmd, Send_Cmd
from rich import print

class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MaxSuport_BuscaPreco"
    _svc_display_name_ = "Busca Preço"
    _svc_description_ = "Serviço MaxSuport para consulta de preços com GERTEC"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.stop_requested = False
        self.server = None
        self.client = None

    def SvcStop(self):
        self.stop_requested = True
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.cleanup()

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_, ""))
        self.main()

    def log_error(self, message):
        with open("C:\\connection_error.log", "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

    def cleanup(self):
        if self.client:
            self.client.close()
        if self.server:
            self.server.close()
        servicemanager.LogInfoMsg("MaxSuport_BuscaPreco - Socket server closed.")

    def main(self):
        try:
            # Cria um socket do servidor
            ip_server = "192.168.10.99"
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((ip_server, 6500))
            self.server.listen()
            print(f'Listening: {ip_server}:6500')

            # Aceita uma conexão de um cliente
            self.client, _ = self.server.accept()

            # Envia um comando para o cliente
            self.client.send(Send_Cmd.OK.value)
            time.sleep(0.5)

            while not self.stop_requested:
                try:
                    # Recebe uma resposta do cliente
                    response = self.client.recv(255)
                    response = response.decode("ascii")
                    self.log_error(response)

                    if '|' in response:
                        print(response)
                        cmd = response.split('|')[0]
                        if Receive_Cmd(cmd[:6]) == Receive_Cmd.RESPONSE_ALWAYS_VERSAO:
                            print('Versão g2 E')
                            check_terminal_alive(self.client)
                            set_always_on(self.client)
                            await_terminal_query(self.client)
                        elif Receive_Cmd(cmd[:3]) == Receive_Cmd.RESPONSE_OK:
                            print('Client connected')
                            check_terminal_alive(self.client)
                            set_always_on(self.client)
                            await_terminal_query(self.client)
                            print('fim')
                except Exception as e:
                    self.log_error(f"Erro no loop principal: {e.__class__.__name__} - {e}")
                    break

        except Exception as e:
            self.log_error(f"Erro ao iniciar o servidor: {e.__class__.__name__} - {e}")
        finally:
            self.cleanup()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(MyService)
