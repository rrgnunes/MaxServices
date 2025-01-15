from funcoes_zap import * 
import time
import random
from datetime import datetime
from funcoes import carregar_configuracoes, inicializa_conexao_mysql, print_log
from campanha_mensagens import mensagens

def gerar_horarios():
    inicio = random.randint(7 * 60, 8 * 60)  # Gera minutos entre 7h e 8h
    fim = random.randint(17 * 60, 18 * 60)  # Gera minutos entre 17h e 18h
    return inicio, fim

def minutos_para_horas(minutos):
    horas = minutos // 60
    minutos_restantes = minutos % 60
    return f"{horas:02d}:{minutos_restantes:02d}"

# Gerar horários aleatórios para o dia
inicio_minutos, fim_minutos = gerar_horarios()
horario_inicio = minutos_para_horas(inicio_minutos)
horario_fim = minutos_para_horas(fim_minutos)

print(f"Hoje as mensagens serão enviadas entre {horario_inicio} e {horario_fim}.")

name_session = "70369921151"
token = generate_token(name_session)
parametros.TOKEN_ZAP = token['token']
retorno = start_session(name_session)

database = parametros.BASEMYSQL = 'maxservices'            
carregar_configuracoes()
inicializa_conexao_mysql()

nome_servico = 'Campanha ZAP'

print_log("Pega dados local", nome_servico)

cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
cur_con.execute(f'''select REPLACE(SUBSTRING_INDEX(cl.telefone, ' ', 2), ' ', '') as telefone
                    from cliente_lead cl 
                    WHERE ((cl.cnae LIKE '%4782201%') OR 
                          (cl.cnae LIKE '%4772500%') OR 
                          (cl.cnae LIKE '%4781400%') OR 
                          (cl.cnae LIKE '%4782202%') OR 
                          (cl.cnae LIKE '%4783101%') OR 
                          (cl.cnae LIKE '%4755502%') OR 
                          (cl.cnae LIKE '%4789001%') OR 
                          (cl.cnae LIKE '%4781400%') OR 
                          (cl.cnae LIKE '%4782201%') OR 
                          (cl.cnae LIKE '%4783101%') OR 
                          (cl.cnae LIKE '%4789001%') OR 
                          (cl.cnae LIKE '%4781400%') OR 
                          (cl.cnae LIKE '%4789002%') OR 
                          (cl.cnae LIKE '%4789003%') OR 
                          (cl.cnae LIKE '%4789004%'))
                      and cl.localidade = 'RR' ''')
obj_empresas = cur_con.fetchall()
cur_con.close()
 
# Contatos teste
# contatos_teste = [
#     {"nome": "Marcelo", "telefone": "6697145422"},
#     {"nome": "Gessica", "telefone": "6699564339"},
#     {"nome": "Maxsuport", "telefone": "6696353159"},
#     {"nome": "Rodrigo", "telefone": "6692825191"}
# ]
 
if obj_empresas:

    # Mostrar o total de números únicos
    print_log(f"Total de números únicos: {len(obj_empresas)}")
    
    contador = 0
    for numero in obj_empresas:
        # Verificar se está dentro do intervalo de horário permitido
        hora_atual = datetime.now()
        minutos_atual = hora_atual.hour * 60 + hora_atual.minute

        if minutos_atual < inicio_minutos or minutos_atual > fim_minutos:
            print_log("Fora do horário de envio. Aguardando...")
            time.sleep(60)  # Aguardar 1 minuto antes de verificar novamente
            continue

        mensagem_aleatoria = random.choice(mensagens)
        print_log(f'Enviando para o número {numero['telefone']}')        
        retorno = envia_mensagem_zap(name_session, str(numero['telefone']), mensagem_aleatoria)
        print_log(f' O envio para o número {numero['telefone']} foi um {retorno['status']}')  

        contador += 1
        
        print_log(f'Enviei {contador} mensagens')

        tempo_aleatorio = random.uniform(30, 70)
        time.sleep(tempo_aleatorio)        
        
        # Simular pausas humanas mais longas após cada 20 mensagens
        if contador % 20 == 0:
            pausa_longa = random.uniform(300, 600)  # Pausa de 5 a 10 minutos
            print_log(f'Pausa longa de {pausa_longa / 60:.2f} minutos após {contador} mensagens.')
            time.sleep(pausa_longa)
          
        print_log('Pausando o envio')
