import sys

def run_servico():
    from servico import MaxServices
    args = ['dummy_arg']
    service = MaxServices(args)
    service.SvcDoRun()

def run_thread_verifica_remoto():
    from thread_verifica_remoto import threadverificaremoto
    thread = threadverificaremoto()
    thread.run()

def run_thread_backup_local():
    from thread_backup_local import threadbackuplocal
    thread = threadbackuplocal()
    thread.run()

def run_thread_servidor_socket():
    from thread_servidor_socket import threadservidorsocket
    thread = threadservidorsocket()
    thread.run()

def run_thread_xml_contador():
    from thread_xml_contador import threadxmlcontador
    thread = threadxmlcontador()
    thread.run()

def run_thread_atualiza_banco():
    from thread_atualiza_banco import threadatualizabanco
    thread = threadatualizabanco()
    thread.run()

def run_thread_zap_automato():
    from thread_zap_automato import threadzapautomato
    thread = threadzapautomato()
    thread.run()

def run_thread_IBPT_NCM_CEST():
    from thread_IBPT_NCM_CEST import threadIBPTNCMCEST
    thread = threadIBPTNCMCEST()
    thread.run()

if __name__ == '__main__':
    option = "atualiza_banco"
    
    if option == 'servico':
        run_servico()
    elif option == 'verifica_remoto':#OK
        run_thread_verifica_remoto()
    elif option == 'backup_local': #ok
        run_thread_backup_local()
    elif option == 'servidor_socket':#ok
        run_thread_servidor_socket()
    elif option == 'xml_contador':#ok
        run_thread_xml_contador()
    elif option == 'atualiza_banco':
        run_thread_atualiza_banco()
    elif option == 'zap_automato':#OK
        run_thread_zap_automato()
    elif option == 'IBPT_NCM_CEST':
        run_thread_IBPT_NCM_CEST()
    else:
        print("Opção inválida.")
        sys.exit(1)
