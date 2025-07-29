import sys

# def run_servico():
#     import servico
#     servico.MaxServices()

def run_thread_verifica_remoto():
    from threads import thread_verifica_remoto 
    thread_verifica_remoto.salva_json()

def run_thread_backup_local():
    from threads import thread_backup_local
    thread_backup_local.backup()

def run_thread_servidor_socket():
    from threads import thread_servidor_socket
    thread_servidor_socket.servidor_socket()

def run_thread_xml_contador():
    from threads import thread_xml_contador
    thread_xml_contador.xmlcontador()

def run_thread_atualiza_banco():
    from threads import thread_atualiza_banco
    thread_atualiza_banco.atualiza_banco()

def run_thread_zap_automato():
    from threads import thread_zap_automato
    thread_zap_automato.zapautomato()

def run_thread_IBPT_NCM_CEST():
    from threads import thread_IBPT_NCM_CEST
    thread_IBPT_NCM_CEST.IBPTNCMCEST()

# def run_thread_MaxUpdate():
#     import MaxUpdate
#     MaxUpdate.MaxUpdate()

if __name__ == '__main__':
    option = "scheduler"
    
    if option == 'servico':
        # run_servico()
        ...
    elif option == 'scheduler':
        # run_thread_MaxUpdate()
        ...
    elif option == 'MaxUpdate':
        # run_thread_MaxUpdate()
        ...
    elif option == 'verifica_remoto':#OK
        run_thread_verifica_remoto()
    elif option == 'backup_local': #OK
        run_thread_backup_local()
    elif option == 'servidor_socket':#OK
        run_thread_servidor_socket()
    elif option == 'xml_contador':#OK
        run_thread_xml_contador()
    elif option == 'atualiza_banco':#OK
        run_thread_atualiza_banco()
    elif option == 'zap_automato':#OK
        run_thread_zap_automato()
    elif option == 'IBPT_NCM_CEST':#OK
        run_thread_IBPT_NCM_CEST()
    else:
        print("Opção inválida.")
        sys.exit(1)
