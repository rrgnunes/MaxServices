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

def atualizar_horarios():
    global inicio_minutos, fim_minutos, horario_inicio, horario_fim
    inicio_minutos, fim_minutos = gerar_horarios()
    horario_inicio = minutos_para_horas(inicio_minutos)
    horario_fim = minutos_para_horas(fim_minutos)
    print_log(f"Hoje as mensagens serão enviadas entre {horario_inicio} e {horario_fim}.")

atualizar_horarios()

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
cur_con.execute(f'''select codigo, REPLACE(SUBSTRING_INDEX(cl.telefone, ' ', 2), ' ', '') as telefone
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
                      and cl.localidade = 'AM' 
                      and campanha_enviado is null  ''')
obj_empresas = cur_con.fetchall()
cur_con.close()

if obj_empresas:
    print_log(f"Total de números únicos: {len(obj_empresas)}")
    contador = 0
    for numero in obj_empresas:
        try:
            while True:
                dia_semana = datetime.now().weekday()
                hora_atual = datetime.now()
                minutos_atual = hora_atual.hour * 60 + hora_atual.minute
                
                if dia_semana != datetime.now().weekday():
                    atualizar_horarios()
                
                if dia_semana in [0, 1, 2, 3, 4] and inicio_minutos <= minutos_atual <= fim_minutos:
                    break
                else:
                    print_log("Fora do horário de envio ou fim de semana. Aguardando...")
                    time.sleep(60)
                    
            if not parametros.MYSQL_CONNECTION.is_connected():
              inicializa_conexao_mysql()    

            mensagem_aleatoria = random.choice(mensagens)
            print_log(f'Enviando para o número {numero["telefone"]}')
            retorno = envia_mensagem_zap(name_session, str(numero['telefone']), mensagem_aleatoria)
            print_log(f' O envio para o número {numero["telefone"]} foi um {retorno["status"]}')

            contador += 1
            print_log(f'Enviei {contador} mensagens')
            
            cur_con = parametros.MYSQL_CONNECTION.cursor(dictionary=True)
            cur_con.execute(f'''UPDATE cliente_lead SET campanha_enviado = 1 WHERE codigo = {numero['codigo']}''')
            cur_con.close()
            parametros.MYSQL_CONNECTION.commit()

 
            
            if contador % 20 == 0:
                pausa_longa = random.uniform(300, 600)
                print_log(f'Pausa longa de {pausa_longa / 60:.2f} minutos após {contador} mensagens.')
                time.sleep(pausa_longa)
            else:
                
                tempo_aleatorio = random.uniform(30, 70)
                print_log(f'Pausando o envio em {tempo_aleatorio} segundos')
                time.sleep(tempo_aleatorio)       
                
                
            
            
        except Exception as e:
            print_log('Erro: ' + str(e))
