import requests
import datetime
import sys
import os
import json
from decimal import Decimal, InvalidOperation
from datetime import datetime as dt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from credenciais import parametros
from funcoes.funcoes import (selectfb, insertfb, updatefb, inicializa_conexao_firebird)


# ==========================================================
# FUNÇÕES DE NORMALIZAÇÃO
# ==========================================================

def normaliza_data(sData):
    if not sData:
        return "1900.01.01"
    sData = str(sData).replace('T00:00:00', '').replace('/', '-')
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y%m%d"):
        try:
            return dt.strptime(sData, fmt).strftime("%d.%m.%Y")
        except:
            continue
    return "1900.01.01"

def normaliza_decimal(v):
    try:
        n = float(Decimal(str(v).replace(',', '.')))
        if abs(n) > 9999999999:
            return 0.0
        return round(n, 6)
    except (InvalidOperation, TypeError, ValueError):
        return 0.0
    
def esc_fb(s):
    return (s or '').replace("'", "''")

# ==========================================================
# SALVAR RETORNO IMENDES
# ==========================================================
def salvar_retorno_imendes(oJson):
    if isinstance(oJson, str):
        oJson = json.loads(oJson)

    if 'grupo' not in oJson:
        print("❌ Nenhum grupo encontrado no retorno.")
        return

    for grupo in oJson['grupo']:
        iCodigoGrupo   = grupo.get('codigo', 0)
        sNCM           = grupo.get('ncm', '')
        sCEST          = grupo.get('cest', '')
        sLista         = grupo.get('lista', '')
        sTipo          = grupo.get('tipo', '')
        sCodANP        = grupo.get('codanp', '')
        sRawJsonGrupo  = json.dumps(grupo, ensure_ascii=False)
        iCodigoProduto = grupo['produto'][0] if 'produto' in grupo and grupo['produto'] else 0

        # === IMENDES_GRUPO ===
        sSqlCheck = f"SELECT CODIGO FROM IMENDES_GRUPO WHERE CODIGO_GRUPO={iCodigoGrupo} AND CODIGO_EMPRESA=1"
        oExiste = selectfb(sSqlCheck)

        if oExiste:
            sSql = f"""
                UPDATE IMENDES_GRUPO SET
                    NCM='{sNCM}', CEST='{sCEST}', LISTA='{sLista}', TIPO='{sTipo}', CODANP='{sCodANP}',
                    ATUALIZADO_EM=CURRENT_TIMESTAMP, RAW_JSON=?, CODIGO_USUARIO=-1
                WHERE CODIGO_GRUPO={iCodigoGrupo} AND CODIGO_EMPRESA=1
            """
            updatefb(sSql, [sRawJsonGrupo])
        else:
            sSql = f"""
                INSERT INTO IMENDES_GRUPO (
                    CODIGO, CODIGO_EMPRESA, CODIGO_GLOBAL, CODIGO_GRUPO,
                    NCM, CEST, LISTA, TIPO, CODANP, ATUALIZADO_EM, RAW_JSON, CODIGO_USUARIO
                ) VALUES (
                    (SELECT COALESCE(MAX(CODIGO),0)+1 FROM IMENDES_GRUPO),
                    1, NULL, {iCodigoGrupo},
                    '{sNCM}', '{sCEST}', '{sLista}', '{sTipo}', '{sCodANP}',
                    CURRENT_TIMESTAMP, ?, -1
                )
            """
            insertfb(sSql, [sRawJsonGrupo])

        # === PIS/COFINS ===
        if 'piscofins' in grupo and grupo['piscofins']:
            pis = grupo['piscofins']
            sSqlCheck = f"SELECT CODIGO FROM IMENDES_GRUPO_PISCOFINS WHERE CODIGO_GRUPO={iCodigoGrupo} AND CODIGO_EMPRESA=1"
            oExiste = selectfb(sSqlCheck)
            if oExiste:
                sSql = f"""
                    UPDATE IMENDES_GRUPO_PISCOFINS SET
                        CST_ENT='{pis.get('cstEnt','')}', CST_SAI='{pis.get('cstSai','')}',
                        ALIQ_PIS={normaliza_decimal(pis.get('aliqPIS',0))},
                        ALIQ_COFINS={normaliza_decimal(pis.get('aliqCOFINS',0))},
                        NRI='{pis.get('nri','')}', AMP_LEGAL='{pis.get('ampLegal','')}',
                        VIG_INI='{normaliza_data(pis.get('dtVigIni'))}', VIG_FIM='{normaliza_data(pis.get('dtVigFin'))}',
                        CODIGO_USUARIO=-1
                    WHERE CODIGO_GRUPO={iCodigoGrupo} AND CODIGO_EMPRESA=1
                """
                updatefb(sSql, [])
            else:
                sSql = f"""
                    INSERT INTO IMENDES_GRUPO_PISCOFINS (
                        CODIGO, CODIGO_GRUPO, CST_ENT, CST_SAI,
                        ALIQ_PIS, ALIQ_COFINS, NRI, AMP_LEGAL, VIG_INI, VIG_FIM,
                        CODIGO_EMPRESA, CODIGO_USUARIO
                    ) VALUES (
                        (SELECT COALESCE(MAX(CODIGO),0)+1 FROM IMENDES_GRUPO_PISCOFINS),
                        {iCodigoGrupo},
                        '{pis.get('cstEnt','')}', '{pis.get('cstSai','')}',
                        {normaliza_decimal(pis.get('aliqPIS',0))}, {normaliza_decimal(pis.get('aliqCOFINS',0))},
                        '{pis.get('nri','')}', '{pis.get('ampLegal','')}',
                        '{normaliza_data(pis.get('dtVigIni'))}', '{normaliza_data(pis.get('dtVigFin'))}',
                        1, -1
                    )
                """
                insertfb(sSql, [])

        # === IPI ===
        if 'ipi' in grupo and grupo['ipi']:
            ipi = grupo['ipi']
            sSqlCheck = f"SELECT CODIGO FROM IMENDES_GRUPO_IPI WHERE CODIGO_GRUPO={iCodigoGrupo} AND CODIGO_EMPRESA=1"
            oExiste = selectfb(sSqlCheck)
            if oExiste:
                sSql = f"""
                    UPDATE IMENDES_GRUPO_IPI SET
                        CST_ENT='{ipi.get('cstEnt','')}', CST_SAI='{ipi.get('cstSai','')}',
                        ALIQ_IPI={normaliza_decimal(ipi.get('aliqIPI',0))},
                        CODENQ='{ipi.get('codenq','')}', EX='{ipi.get('ex','')}',
                        CODIGO_USUARIO=-1
                    WHERE CODIGO_GRUPO={iCodigoGrupo} AND CODIGO_EMPRESA=1
                """
                updatefb(sSql, [])
            else:
                sSql = f"""
                    INSERT INTO IMENDES_GRUPO_IPI (
                        CODIGO, CODIGO_GRUPO, CST_ENT, CST_SAI,
                        ALIQ_IPI, CODENQ, EX, CODIGO_EMPRESA, CODIGO_USUARIO
                    ) VALUES (
                        (SELECT COALESCE(MAX(CODIGO),0)+1 FROM IMENDES_GRUPO_IPI),
                        {iCodigoGrupo},
                        '{ipi.get('cstEnt','')}', '{ipi.get('cstSai','')}',
                        {normaliza_decimal(ipi.get('aliqIPI',0))}, '{ipi.get('codenq','')}',
                        '{ipi.get('ex','')}', 1, -1
                    )
                """
                insertfb(sSql, [])

        # === CBS ===
        if 'cbs' in grupo and grupo['cbs']:
            cbs = grupo['cbs']
            sCClass     = esc_fb(cbs.get('cClassTrib'))
            sDescClass  = esc_fb(cbs.get('descrcClassTrib'))
            sCst        = esc_fb(cbs.get('cst'))
            sDescCst    = esc_fb(cbs.get('descrCST'))
            sAmpLegal   = esc_fb(cbs.get('ampLegal'))
            sSqlCheck = f"SELECT CODIGO FROM IMENDES_GRUPO_CBS WHERE CODIGO_GRUPO={iCodigoGrupo} AND CODIGO_EMPRESA=1"
            oExiste = selectfb(sSqlCheck)
            if oExiste:
                sSql = f"""
                    UPDATE IMENDES_GRUPO_CBS SET
                        CCLASS_TRIB='{sCClass}',
                        DESC_CCLASS_TRIB='{sDescClass}',
                        CST='{sCst}',
                        DESC_CST='{sDescCst}',
                        ALIQUOTA={normaliza_decimal(cbs.get('aliquota',0))},
                        REDUCAO={normaliza_decimal(cbs.get('reducao',0))},
                        REDUCAO_BC_CBS={normaliza_decimal(cbs.get('reducaoBcCBS',0))},
                        AMP_LEGAL='{sAmpLegal}',
                        VIG_INI='{normaliza_data(cbs.get('dtVigIni'))}',
                        VIG_FIM='{normaliza_data(cbs.get('dtVigFin'))}',
                        CODIGO_USUARIO=-1
                    WHERE CODIGO_GRUPO={iCodigoGrupo}
                    AND CODIGO_EMPRESA=1
                """
                updatefb(sSql, [])
            else:
                sSql = f"""
                    INSERT INTO IMENDES_GRUPO_CBS (
                        CODIGO, CODIGO_GRUPO, CCLASS_TRIB, DESC_CCLASS_TRIB, CST, DESC_CST,
                        ALIQUOTA, REDUCAO, REDUCAO_BC_CBS, AMP_LEGAL, VIG_INI, VIG_FIM,
                        CODIGO_EMPRESA, CODIGO_USUARIO
                    ) VALUES (
                        (SELECT COALESCE(MAX(CODIGO),0)+1 FROM IMENDES_GRUPO_CBS),
                        {iCodigoGrupo},
                        '{sCClass}', '{sDescClass}',
                        '{sCst}', '{sDescCst}',
                        {normaliza_decimal(cbs.get('aliquota',0))}, {normaliza_decimal(cbs.get('reducao',0))},
                        {normaliza_decimal(cbs.get('reducaoBcCBS',0))}, '{sAmpLegal}',
                        '{normaliza_data(cbs.get('dtVigIni'))}', '{normaliza_data(cbs.get('dtVigFin'))}',
                        1, -1
                    )
                """
                insertfb(sSql, [])

        # === REGRA e IBS ===
        if 'regra' in grupo:
            for regra in grupo['regra']:
                iCodigoRegra = regra.get('codigo', 0)

                sUF       = esc_fb(regra.get('uf'))
                sCST      = esc_fb(regra.get('cst'))
                sAmpLegal = esc_fb(regra.get('ampLegal'))

                sSqlCheck = f"""
                    SELECT CODIGO
                    FROM IMENDES_REGRA
                    WHERE REGRA_CODIGO={iCodigoRegra}
                    AND CODIGO_EMPRESA=1
                """
                oExiste = selectfb(sSqlCheck)

                if oExiste:
                    sSql = f"""
                        UPDATE IMENDES_REGRA SET
                            UF='{sUF}',
                            CST='{sCST}',
                            ALIQ_ICMS={normaliza_decimal(regra.get('aliqicms',0))},
                            ALIQ_ICMS_ST={normaliza_decimal(regra.get('aliqicmsst',0))},
                            IVA={normaliza_decimal(regra.get('iva',0))},
                            FCP={normaliza_decimal(regra.get('fcp',0))},
                            CFOP_COMPRA={regra.get('cfopCompra',0)},
                            CFOP_VENDA={regra.get('cfopVenda',0)},
                            VIG_INI='{normaliza_data(regra.get('dtVigIni'))}',
                            VIG_FIM='{normaliza_data(regra.get('dtVigFin'))}',
                            AMP_LEGAL='{sAmpLegal}',
                            CODIGO_USUARIO=-1
                        WHERE REGRA_CODIGO={iCodigoRegra}
                        AND CODIGO_EMPRESA=1
                    """
                    updatefb(sSql, [])
                else:
                    sSql = f"""
                        INSERT INTO IMENDES_REGRA (
                            CODIGO, CODIGO_GRUPO, REGRA_CODIGO, UF, CST,
                            ALIQ_ICMS, ALIQ_ICMS_ST, IVA, FCP,
                            CFOP_COMPRA, CFOP_VENDA, VIG_INI, VIG_FIM, AMP_LEGAL,
                            CODIGO_EMPRESA, CODIGO_USUARIO
                        ) VALUES (
                            (SELECT COALESCE(MAX(CODIGO),0)+1 FROM IMENDES_REGRA),
                            {iCodigoGrupo}, {iCodigoRegra}, '{sUF}', '{sCST}',
                            {normaliza_decimal(regra.get('aliqicms',0))},
                            {normaliza_decimal(regra.get('aliqicmsst',0))},
                            {normaliza_decimal(regra.get('iva',0))},
                            {normaliza_decimal(regra.get('fcp',0))},
                            {regra.get('cfopCompra',0)}, {regra.get('cfopVenda',0)},
                            '{normaliza_data(regra.get('dtVigIni'))}', '{normaliza_data(regra.get('dtVigFin'))}',
                            '{sAmpLegal}',
                            1, -1
                        )
                    """
                    insertfb(sSql, [])

                if 'ibs' in regra and regra['ibs']:
                    ibs = regra['ibs']

                    sIbsClass      = esc_fb(ibs.get('cClassTrib'))
                    sIbsDescClass  = esc_fb(ibs.get('descrcClassTrib'))
                    sIbsCst        = esc_fb(ibs.get('cst'))
                    sIbsDescCst    = esc_fb(ibs.get('descrCST'))
                    sIbsAmpLegal   = esc_fb(ibs.get('ampLegal'))

                    sSqlCheck = f"""
                        SELECT CODIGO
                        FROM IMENDES_REGRA_IBS
                        WHERE CODIGO_REGRA={iCodigoRegra}
                        AND CODIGO_EMPRESA=1
                    """
                    oExiste = selectfb(sSqlCheck)

                    if oExiste:
                        sSql = f"""
                            UPDATE IMENDES_REGRA_IBS SET
                                CCLASS_TRIB='{sIbsClass}',
                                DESC_CCLASS_TRIB='{sIbsDescClass}',
                                CST='{sIbsCst}',
                                DESC_CST='{sIbsDescCst}',
                                IBS_UF={normaliza_decimal(ibs.get('ibsUF',0))},
                                IBS_MUN={normaliza_decimal(ibs.get('ibsMun',0))},
                                RED_ALIQ_IBS={normaliza_decimal(ibs.get('reducaoaliqIBS',0))},
                                RED_BC_IBS={normaliza_decimal(ibs.get('reducaoBcIBS',0))},
                                AMP_LEGAL='{sIbsAmpLegal}',
                                VIG_INI='{normaliza_data(ibs.get('dtVigIni'))}',
                                VIG_FIM='{normaliza_data(ibs.get('dtVigFin'))}',
                                CODIGO_USUARIO=-1
                            WHERE CODIGO_REGRA={iCodigoRegra}
                            AND CODIGO_EMPRESA=1
                        """
                        updatefb(sSql, [])
                    else:
                        sSql = f"""
                            INSERT INTO IMENDES_REGRA_IBS (
                                CODIGO, CODIGO_REGRA, CCLASS_TRIB, DESC_CCLASS_TRIB, CST, DESC_CST,
                                IBS_UF, IBS_MUN, RED_ALIQ_IBS, RED_BC_IBS,
                                AMP_LEGAL, VIG_INI, VIG_FIM,
                                CODIGO_EMPRESA, CODIGO_USUARIO
                            ) VALUES (
                                (SELECT COALESCE(MAX(CODIGO),0)+1 FROM IMENDES_REGRA_IBS),
                                {iCodigoRegra},
                                '{sIbsClass}', '{sIbsDescClass}',
                                '{sIbsCst}', '{sIbsDescCst}',
                                {normaliza_decimal(ibs.get('ibsUF',0))}, {normaliza_decimal(ibs.get('ibsMun',0))},
                                {normaliza_decimal(ibs.get('reducaoaliqIBS',0))}, {normaliza_decimal(ibs.get('reducaoBcIBS',0))},
                                '{sIbsAmpLegal}',
                                '{normaliza_data(ibs.get('dtVigIni'))}', '{normaliza_data(ibs.get('dtVigFin'))}',
                                1, -1
                            )
                        """
                        insertfb(sSql, [])

        # === BAIXA SIMILARIDADE ===
        if 'baixaSimilaridade' in oJson and oJson['baixaSimilaridade']:
            for idx, item in enumerate(oJson['baixaSimilaridade']):
                sRawItem = json.dumps(item, ensure_ascii=False)
                sSqlCheck = f"SELECT CODIGO FROM IMENDES_BAIXA_SIMILARIDADE WHERE ITEM_IDX={idx} AND CODIGO_EMPRESA=1"
                oExiste = selectfb(sSqlCheck)
                if oExiste:
                    sSql = f"""
                        UPDATE IMENDES_BAIXA_SIMILARIDADE SET RAW_JSON=?, CODIGO_USUARIO=-1
                        WHERE ITEM_IDX={idx} AND CODIGO_EMPRESA=1
                    """
                    updatefb(sSql, [sRawItem])
                else:
                    sSql = f"""
                        INSERT INTO IMENDES_BAIXA_SIMILARIDADE (
                            CODIGO, ITEM_IDX, RAW_JSON, CODIGO_EMPRESA, CODIGO_USUARIO
                        ) VALUES (
                            (SELECT COALESCE(MAX(CODIGO),0)+1 FROM IMENDES_BAIXA_SIMILARIDADE),
                            {idx}, ?, 1, -1
                        )
                    """
                    insertfb(sSql, [sRawItem])

        print(f"✅ Grupo {iCodigoGrupo} salvo com sucesso (produto {iCodigoProduto}).")

    print("✅ Todos os dados da iMendes foram processados e salvos com sucesso.")



# ==========================================================
# CONSULTA E ENVIO PARA IMENDES
# ==========================================================
def obter_produtos_para_imendes():
    sSQL = """
        SELECT
            CODIGO, DESCRICAO, NCM, CEST, CODBARRA, TIPO_TRIBUTACAO, RESTAUTANTE
        FROM PRODUTO
        WHERE ATUALIZAR_IMENDES = 1
          AND ATIVO = 'S'
    """
    return selectfb(sSQL)


def montar_payload_imendes():
    sLogin = "19775656000104"

    oPayload = {
        "env": 1,
        "cabecalho": {
            "cnpj": sLogin,
            "cnae": "4711302",
            "cnaeSecundario": "1091102",
            "fabricacaoPropria": True,
            "crt": 3,
            "regimeEspecial": "",
            "codFaixa": 99,
            "amb": 1,
            "municipio": "3550308",
            "dia": datetime.datetime.now().day,
            "mes": datetime.datetime.now().month,
            "ano": datetime.datetime.now().year,
            "dthr": datetime.datetime.now().isoformat(),
            "prodEnv": 1,
            "prodRet": 0,
            "transacao": "AutoIMendes",
            "mensagem": "Consulta em homologacao",
            "aces_primeiro": "",
            "aces_expirar": "",
            "versao": "3.43",
            "regimeTrib": "R",
            "contribuinte": 1
        },
        "uf": ["MT"],
        "produto": []
    }

    aProdutos = obter_produtos_para_imendes()

    for prod in aProdutos:
        oPayload["produto"].append({
            "codigo": prod[4],
            "codIMendes": "",
            "descricao": prod[1],
            "ncm": prod[2],
            "cest": prod[3],
            "tipoCodigo": 0,
            "refeicao": "S" if str(prod[6]).upper() == "S" else "N",
            "encontrado": True
        })

    with open("retorno_imendes.json", "w", encoding="utf-8") as f:
        json.dump(oPayload, f, ensure_ascii=False, indent=4)

    print("✅ Arquivo 'retorno_imendes.json' salvo com sucesso.")
    return oPayload


def consultar_regras_fiscais():
    sLogin = "19775656000104"
    sSenha = "QsuS21Pd3dtI"
    sUrl   = "https://consultatributos.com.br:8443/api/v2/public/RegrasFiscais"

    oPayload = montar_payload_imendes()
    oHeaders = {"Login": sLogin, "Senha": sSenha, "Content-Type": "application/json"}

    try:
        oResp = requests.post(sUrl, headers=oHeaders, json=oPayload, timeout=60)
        oResp.raise_for_status()
        oData = oResp.json()

        with open("resposta_imendes.json", "w", encoding="utf-8") as f:
            json.dump(oData, f, ensure_ascii=False, indent=4)

        print("✅ Resposta salva em 'resposta_imendes.json'")
        salvar_retorno_imendes(oData)
        return oData

    except Exception as e:
        print("❌ Erro ao consultar iMendes:", e)
        return {"erro": str(e)}


if __name__ == "__main__":
    inicializa_conexao_firebird()
    consultar_regras_fiscais()
