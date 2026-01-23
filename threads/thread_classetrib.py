import os
import sys
import requests
from requests_pkcs12 import Pkcs12Adapter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros as params
from funcoes.funcoes import *

def realizar_consulta_api():

    print_log(f"Realizando consulta na API...", nome_script)
    url = "https://cff.svrs.rs.gov.br/api/v1/consultas/classTrib"
    # arquivo_certificado = "C:\\Main\\Certificados\\MaxSuport.pfx"
    arquivo_certificado = os.path.join('/', 'home', 'certificado', 'MaxSuport.pfx')
    senha_certificado = "12345678"
    classificacao_tributaria = []
    classificacao_tributaria_detalhe = []
    try:
        with requests.Session() as s:
            s.mount(url, Pkcs12Adapter(pkcs12_filename=arquivo_certificado, pkcs12_password=senha_certificado))

            resposta = s.get(url, verify=True)
            print_log(f"Consula realizada -> status code: {resposta.status_code}", nome_script)
            
            resposta.raise_for_status()
            resposta_json = resposta.json()

    except Exception as e:
        print_log(f"Falha ao realizar a consulta na API -> motivo: {e}", nome_script)

    for cst in resposta_json:

        classificacao_tributaria_detalhe.append((cst['CST'], cst['classificacoesTributarias']))
        dict.pop(cst, 'classificacoesTributarias')
        classificacao_tributaria.append(cst)

    return (classificacao_tributaria, classificacao_tributaria_detalhe)

def realizar_consulta_banco():

    classe_triburia = []
    classe_triburia_detalhe = []
    cursor = None

    try:
        print_log("Realizando consulta no banco de dados...", nome_script)
        cursor = params.MYSQL_CONNECTION.cursor(dictionary=True)

        sql_select = "SELECT * FROM CLASSE_TRIBUTARIA;"
        cursor.execute(sql_select)
        registros = cursor.fetchall()

        for registro in registros:
            classe_triburia.append(registro)

        sql_select = "SELECT * FROM CLASSE_TRIBUTARIA_DETALHE;"
        cursor.execute(sql_select)
        registros = cursor.fetchall()

        for registro in registros:
            classe_triburia_detalhe.append(registro)

    except Exception as e:
        print_log(f"Falha ao realizar a consulta ao banco -> motivo: {e.__class__.__name__} - {e}", nome_script)
        raise e

    finally:
        if cursor:
            cursor.close()

    return (classe_triburia, classe_triburia_detalhe)


def atualizar_classificacao_tributaria():
    
    csts_api = realizar_consulta_api()
    
    if not csts_api:
        print_log(f"Nenhum resultado encontrado na consulta...", nome_script)
        return
    
    csts_banco = realizar_consulta_banco()

    scripts = comparar_tributacoes(csts_api[0], csts_banco[0])
    scripts += comparar_tributacoes_detalhe(csts_api[1], csts_banco[1])

    executar_scripts(scripts)

def comparar_tributacoes(csts_api:list[dict], csts_banco:list[dict]):    
    print_log(f"Comparando tributacoes...", nome_script)
    scripts = []

    for cst_api in csts_api:        
        contem = False
        IndIBSCBS = 1 if cst_api.get('IndIBSCBS', False) else 0
        IndRedBC = 1 if cst_api.get('IndRedBC', False) else 0
        IndRedAliq = 1 if cst_api.get('IndRedAliq', False) else 0
        IndTransfCred = 1 if cst_api.get('IndTransfCred', False) else 0
        IndDif = 1 if cst_api.get('IndDif', False) else 0
        IndAjusteCompet = 1 if cst_api.get('IndAjusteCompet', False) else 0
        IndIBSCBSMono = 1 if cst_api.get('IndIBSCBSMono', False) else 0
        IndCredPresIBSZFM = 1 if cst_api.get('IndCredPresIBSZFM', False) else 0
        publicacao_api = datetime.datetime.strptime(cst_api['Publicacao'], '%Y-%m-%dT%H:%M:%S') if cst_api['Publicacao'] else None
        inicio_vigencia_api = datetime.datetime.strptime(cst_api['InicioVigencia'], '%Y-%m-%dT%H:%M:%S') if cst_api['InicioVigencia'] else None
        fim_vigencia_api = datetime.datetime.strptime(cst_api['FimVigencia'], '%Y-%m-%dT%H:%M:%S') if cst_api['FimVigencia'] else None

        cst_atualizado = (
            1, # código da empresa                        
            cst_api.get('CST', ''), # código CST
            cst_api.get('DescricaoCST', ''), # Descrição do CST
            IndIBSCBS,
            IndRedBC,
            IndRedAliq,
            IndTransfCred,
            IndDif,
            IndAjusteCompet,
            IndIBSCBSMono,
            IndCredPresIBSZFM,
            publicacao_api,
            inicio_vigencia_api,
            fim_vigencia_api
        )

        for cst_banco in csts_banco:
            
            if cst_banco['CST'] == cst_api['CST']:
                contem = True

                if cst_banco['PUBLICACAO'] != publicacao_api:
                    sql_update = "UPDATE CLASSE_TRIBUTARIA SET CODIGO_EMPRESA = %s, CST = %s, DESCRICAO_CST = %s, IND_IBS_CBS = %s, IND_REDBC = %s, " \
                    "IND_REDALIQ = %s, IND_TRANSFCRED = %s, IND_DIF = %s, IND_AJUSTE_COMPET = %s, IND_IBS_CBS_MONO = %s, " \
                    "IND_CRED_PRES_IBS_ZFM = %s, PUBLICACAO = %s, INICIO_VIGENCIA = %s, FIM_VIGENCIA = %s WHERE CST = %s"

                    cst_atualizado += (cst_api.get('CST', ''),)

                    scripts.append({
                        "comando": sql_update,
                        "valores": cst_atualizado,
                        "cst": cst_api['CST'],
                        "cClassTrib": "",
                        "tipo": "UPDATE"
                    })
                    break

        if not contem:
            sql_insert = """INSERT INTO CLASSE_TRIBUTARIA 
            (CODIGO_EMPRESA, CST, DESCRICAO_CST, IND_IBS_CBS, IND_REDBC, IND_REDALIQ, IND_TRANSFCRED, IND_DIF, IND_AJUSTE_COMPET, IND_IBS_CBS_MONO, 
            IND_CRED_PRES_IBS_ZFM, PUBLICACAO, INICIO_VIGENCIA, FIM_VIGENCIA) VALUES ("""
            sql_insert += "," .join(["%s"] * (len(cst_atualizado)))
            sql_insert += ")"

            scripts.append({
                "comando": sql_insert,
                "valores": cst_atualizado,
                "cst": cst_api['CST'],
                "cClassTrib": "",
                "tipo": "INSERT"
            })

    return scripts

def comparar_tributacoes_detalhe(csts_detalhe_api:list[dict], csts_detalhe_banco:list[dict]):
    print_log("Comparando detalhes da tributação...", nome_script)
    scripts = []

    try:
        for cst, detalhes_cst in csts_detalhe_api:
            
            for detalhe in detalhes_cst:
                contem = False

                cclass_trib = detalhe.get('cClassTrib', '')
                DescricaoClassTrib = detalhe.get('DescricaoClassTrib', '')
                pRedIBS = detalhe.get('pRedIBS', '')
                pRedCBS = detalhe.get('pRedCBS', '')
                IndTribRegular = 1 if detalhe.get('IndTribRegular', False) else 0
                IndCredPresOper = 1 if detalhe.get('IndCredPresOper', False) else 0
                IndEstornoCred = 1 if detalhe.get('IndEstornoCred', False) else 0
                MonofasiaSujeitaRetencao = 1 if detalhe.get('MonofasiaSujeitaRetencao', False) else 0
                MonofasiaRetidaAnt = 1 if detalhe.get('MonofasiaRetidaAnt', False) else 0
                MonofasiaDiferimento = 1 if detalhe.get('MonofasiaDiferimento', False) else 0
                MonofasiaPadrao = 1 if detalhe.get('MonofasiaPadrao', False) else 0
                Publicacao = datetime.datetime.strptime(detalhe['Publicacao'][:19],'%Y-%m-%dT%H:%M:%S') if detalhe['Publicacao'] else None
                InicioVigencia = datetime.datetime.strptime(detalhe['InicioVigencia'][:19],'%Y-%m-%dT%H:%M:%S') if detalhe['InicioVigencia'] else None
                FimVigencia = datetime.datetime.strptime(detalhe['FimVigencia'][:19],'%Y-%m-%dT%H:%M:%S') if detalhe['FimVigencia'] else None
                TipoAliquota = detalhe.get('TipoAliquota', '')
                IndNFe = 1 if detalhe.get('IndNFe', False) else 0
                IndNFCe = 1 if detalhe.get('IndNFCe', False) else 0
                IndCTe = 1 if detalhe.get('IndCTe', False) else 0
                IndCTeOS = 1 if detalhe.get('IndCTeOS', False) else 0
                IndBPe = 1 if detalhe.get('IndBPe', False) else 0
                IndNF3e = 1 if detalhe.get('IndNF3e', False) else 0
                IndNFCom = 1 if detalhe.get('IndNFCom', False) else 0
                IndNFSE = 1 if detalhe.get('IndNFSE', False) else 0
                IndBPeTM = 1 if detalhe.get('IndBPeTM', False) else 0
                IndBPeTA= 1 if detalhe.get('IndBPeTA', False) else 0
                IndNFAg = 1 if detalhe.get('IndNFAg', False) else 0
                IndNFSVIA = 1 if detalhe.get('IndNFSVIA', False) else 0
                IndNFABI = 1 if detalhe.get('IndNFABI', False) else 0
                IndNFGas = 1 if detalhe.get('IndNFGas', False) else 0
                IndDERE = 1 if detalhe.get('IndDERE', False) else 0
                Anexo = detalhe.get('Anexo', '')
                Link = detalhe.get('Link', '')

                cst_detalhe_atualizado = (
                    1, # Código empresa,
                    cst, # Código da classe tributaria pai
                    cclass_trib,
                    DescricaoClassTrib,
                    pRedIBS,
                    pRedCBS,
                    IndTribRegular,
                    IndCredPresOper,
                    IndEstornoCred,
                    MonofasiaSujeitaRetencao,
                    MonofasiaRetidaAnt,
                    MonofasiaDiferimento,
                    MonofasiaPadrao,
                    Publicacao,
                    InicioVigencia,
                    FimVigencia,
                    TipoAliquota,
                    IndNFe,
                    IndNFCe,
                    IndCTe,
                    IndCTeOS,
                    IndBPe,
                    IndNF3e,
                    IndNFCom,
                    IndNFSE,
                    IndBPeTM,
                    IndBPeTA,
                    IndNFAg,
                    IndNFSVIA,
                    IndNFABI,
                    IndNFGas,
                    IndDERE,
                    Anexo,
                    Link
                )

                for cst_detalhe_banco in csts_detalhe_banco:

                    if detalhe['cClassTrib'] == cst_detalhe_banco['CCLASS_TRIB']:
                        contem = True

                        if Publicacao != cst_detalhe_banco['PUBLICACAO']:
                            sql_update = """UPDATE CLASSE_TRIBUTARIA_DETALHE SET CODIGO_EMPRESA = %s, CODIGO_CLASSE_TRIBUTARIA = %s, CCLASS_TRIB = %s, DESCRICAO_CLASS_TRIB = %s,
                                        PRED_IBS = %s, PRED_CBS = %s, IND_TRIB_REGULAR = %s, IND_CRED_PRES_OPER = %s, IND_ESTORNO_CRED = %s, MONOFASIASUJEITARETENCAO = %s,
                                        MONOFASIARETIDAANT = %s, MONOFASIADIFERIMENTO = %s, MONOFASIAPADRAO = %s, PUBLICACAO = %s, INICIOVIGENCIA = %s, FIMVIGENCIA = %s,
                                        TIPO_ALIQUOTA = %s, IND_NFE = %s, IND_NFCE = %s, IND_CTE = %s, IND_CTEOS = %s, IND_BPE = %s, IND_NF3E = %s, IND_NFCOM = %s, IND_NFSE = %s,
                                        IND_BPETM = %s, IND_BPETA = %s, IND_NFAG = %s, IND_NFSVIA = %s, IND_NFABI = %s, IND_NFGAS = %s, IND_DERE = %s, ANEXO = %s, LINK = %s
                                        WHERE CODIGO_CLASSE_TRIBUTARIA = %s AND CCLASS_TRIB = %s"""
                            cst_detalhe_atualizado += (cst, cclass_trib)

                            scripts.append({
                                "comando": sql_update,
                                "valores": cst_detalhe_atualizado,
                                "cst": cst,
                                "cClassTrib": cclass_trib,
                                "tipo": "UPDATE"
                            })
                            break

                if not contem:
                    sql_insert = """INSERT INTO CLASSE_TRIBUTARIA_DETALHE (CODIGO_EMPRESA, CODIGO_CLASSE_TRIBUTARIA, CCLASS_TRIB, DESCRICAO_CLASS_TRIB, PRED_IBS, PRED_CBS, IND_TRIB_REGULAR,
                    IND_CRED_PRES_OPER, IND_ESTORNO_CRED, MONOFASIASUJEITARETENCAO, MONOFASIARETIDAANT, MONOFASIADIFERIMENTO, MONOFASIAPADRAO, PUBLICACAO, INICIOVIGENCIA,
                    FIMVIGENCIA, TIPO_ALIQUOTA, IND_NFE, IND_NFCE, IND_CTE, IND_CTEOS, IND_BPE, IND_NF3E, IND_NFCOM, IND_NFSE, IND_BPETM, IND_BPETA, IND_NFAG, IND_NFSVIA,
                    IND_NFABI, IND_NFGAS, IND_DERE, ANEXO, LINK) VALUES ("""

                    sql_insert += "," .join(["%s"] * (len(cst_detalhe_atualizado)))
                    sql_insert += ")"

                    scripts.append({
                        "comando": sql_insert,
                        "valores": cst_detalhe_atualizado,
                        "cst": cst,
                        "cClassTrib": cclass_trib,
                        "tipo": "INSERT"
                    })

        return scripts        
    except Exception as e:
        print_log(f"Erro ao tentar comparar detalhe: {e}", nome_script)
        return scripts



def executar_scripts(scripts:list[dict]):
    cursor = None
    erros = []

    try:
        cursor = params.MYSQL_CONNECTION.cursor()
        for script in scripts:
            print_log(f"Executando Script: {script['tipo']} CST: {script['cst']} cClassTrib: {script['cClassTrib']}", nome_script)
            try:
                cursor.execute(script['comando'], script['valores'])
            except Exception as e:
                erros.append(f"Erro no comando do CST = {script['cst']} cClassTrib: {script['cClassTrib']} -> motivo: {e}")
        params.MYSQL_CONNECTION.commit()

    except Exception as e:
        params.MYSQL_CONNECTION.rollback()
        print_log(f"Erro ao tentar executar scripts -> motivo: {e}", nome_script)

    finally:
        if cursor:
            cursor.close()

    return erros

def replicar_para_cnpj_especifico(cnpj: str):
    cursor = None

    try:
        print_log(f"Adicionando referencias de replicação para CNPJ: {cnpj}", nome_script)
        cursor = params.MYSQL_CONNECTION.cursor()

        sql_consulta = "SELECT CODIGO_GLOBAL FROM CLASSE_TRIBUTARIA;"
        cursor.execute(sql_consulta)
        resultados = cursor.fetchall()

        for resultado in resultados:
            sql_insert = f"INSERT INTO REPLICADOR (TABELA, ACAO, CNPJ_EMPRESA, CODIGO_GLOBAL) VALUES ('CLASSE_TRIBUTARIA', 'I', {cnpj}, {resultado[0]})"
            cursor.execute(sql_insert)

        print_log("Referencias de CLASSE_TRIBUTARIA adicionadas...")

        sql_consulta_detalhe = "SELECT CODIGO_GLOBAL FROM CLASSE_TRIBUTARIA_DETALHE;"
        cursor.execute(sql_consulta_detalhe)
        resultados = cursor.fetchall()

        for resultado in resultados:
            sql_insert = f"INSERT INTO REPLICADOR (TABELA, ACAO, CNPJ_EMPRESA, CODIGO_GLOBAL) VALUES ('CLASSE_TRIBUTARIA_DETALHE', 'I', {cnpj}, {resultado[0]})"
            cursor.execute(sql_insert)

        print_log("Referencias de CLASSE_TRIBUTARIA_DETALHE adicionadas...")

        params.MYSQL_CONNECTION.commit()
        print_log(f"Referencias de replicação adicionadas com sucesso para CNPJ: {cnpj}\n", nome_script)

    except Exception as e:
        params.MYSQL_CONNECTION.rollback()
        print_log(f"Não foi possível adicionar referencias para CNPJ= {cnpj} -> motivo: {e}\n", nome_script)

    finally:
        
        if cursor:
            cursor.close()

def replicar_para_todos_cnpjs():
    cursor = None

    try:
        print_log("Iniciando referências para todos os cnpjs", nome_script)
        sql_select = "SELECT DISTINCT(CNPJ) FROM EMPRESA;"        
        cursor = params.MYSQL_CONNECTION.cursor()
        cursor.execute(sql_select)

        cnpjs = cursor.fetchall()

        if cnpjs:
            for cnpj in cnpjs:
                replicar_para_cnpj_especifico(cnpj[0])

        print_log("Finalizado referências para todos os cnpjs", nome_script)
    except Exception as e:
        print_log(f"Ocorreu um erro ao iniciar referencias para cnpjs -> motivo: {e}", nome_script)
        
    finally:
        if cursor:
            cursor.close()


if __name__ == '__main__':

    nome_script = os.path.basename(sys.argv[0]).replace('.py', '')
    if pode_executar(nome_script):
        criar_bloqueio(nome_script)
        try:
            caminho_sistema = params.SCRIPT_PATH.replace('SERVER', '')
            caminho_banco_ini = os.path.join(caminho_sistema, 'banco.ini')

            banco_ini = obter_dados_ini(caminho_banco_ini)

            if banco_ini['homologacao']:
                params.BASEMYSQL = 'DADOSHM'
                
            inicializa_conexao_mysql()
            
            if (len(sys.argv) > 2) and ('-re' == sys.argv[1]):

                if '-all' in sys.argv:
                    replicar_para_todos_cnpjs()

                elif str.isdigit(sys.argv[2]):
                    replicar_para_cnpj_especifico(sys.argv[2])
            
            elif (len(sys.argv) > 1):
                print_log("Parâmetro invalido.\nOpções disponíveis:\n\t -re [replicao das tributações] {cnpj} -all [para todos os cnpjs]", nome_script)

            else:
                atualizar_classificacao_tributaria()

        except Exception as e:
            print_log(f"Não foi possível executar -> motivo: {e}")
        finally:
            fechar_conexao_mysql()
            remover_bloqueio(nome_script)