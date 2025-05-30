from datetime import datetime
import random

mensagens = [
    "Oi, tudo bem? Sou Marcelo Lima, da Max Suport Sistemas. Temos o sistema mais completo e acessível do mercado para empresas de varejo, a partir de apenas R$ 150,00 por mês!\n\nCom ele, você terá:\n✅ Suporte humanizado\n✅ Atendimento rápido e início em minutos\n✅ Controle total de estoque e vendas\n✅ Emissão de documentos fiscais \n✅ Integração TEF\n✅ Geração de etiquetas\n✅ Relatórios personalizados\n✅ E muito mais!\n\nPosso te explicar em 2 minutos como ele pode transformar sua empresa?\n\nAcesse nosso site: https://maxsuport.com\n\nMax Suport Sistemas\nCNPJ: 19.775.656/0001-04\n\n😊 Não cobramos taxa de instalação",
    "Olá! Sou Marcelo Lima da Max Suport Sistemas. Nosso sistema para empresas de varejo é o mais completo e acessível do mercado, começando por apenas R$ 150,00 por mês!\n\nCom ele, você terá:\n✅ Controle total de estoque\n✅ Emissão de documentos fiscais\n✅ Relatórios personalizados\n✅ E muito mais!\n\nQuer saber como ele pode ajudar sua empresa? Acesse nosso site: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Olá aqui é Marcelo da Max Suport Sistemas. Estamos oferecendo um sistema completo para varejo por apenas R$ 150,00 mensais!\n\nCom ele, você terá:\n✅ Integração TEF\n✅ Controle de vendas\n✅ Suporte humanizado\n✅ Geração de etiquetas\n✅ E muito mais!\n\nGostaria de conhecer? Visite: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Ei! Sou Marcelo da Max Suport Sistemas. Oferecemos o melhor sistema para empresas de varejo a partir de R$ 150,00 por mês!\n\nDestaques:\n✅ Suporte imediato\n✅ Relatórios detalhados\n✅ Controle de estoque eficiente\n✅ Emissão de notas fiscais\n✅ Integração TEF\n\nAcesse https://maxsuport.com para saber mais!\n\n😊 Não cobramos taxa de instalação",
    "Olá, tudo bem? Aqui é Marcelo da Max Suport Sistemas. Estamos ajudando empresas de varejo com um sistema completo e acessível.\n\nPor apenas R$ 150,00 por mês, você terá:\n✅ Controle total de estoque e vendas\n✅ Emissão de documentos fiscais\n✅ Geração de etiquetas\n✅ Relatórios personalizados\n✅ Suporte humanizado\n\nAcesse nosso site e saiba mais: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Olá Sou Marcelo Lima, da Max Suport Sistemas. Nosso sistema de gestão foi criado especialmente para empresas de varejo.\n\nCom apenas R$ 150,00 por mês, você terá:\n✅ Controle de vendas\n✅ Relatórios sob medida\n✅ Suporte ágil\n✅ Integração TEF\n✅ E muito mais!\n\nPosso te explicar como ele funciona? Acesse: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Ei! Aqui é Marcelo da Max Suport. Já pensou em transformar a gestão da sua empresa? Por apenas R$ 150,00 mensais, nós podemos ajudar!\n\nDestaques:\n✅ Controle de estoque\n✅ Emissão de notas fiscais\n✅ Suporte humanizado\n✅ Relatórios detalhados\n✅ E muito mais!\n\nConfira no site: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Oi, tudo bem? Sou Marcelo da Max Suport Sistemas. Com nosso sistema, empresas de varejo têm gestão completa e acessível por apenas R$ 150,00 por mês!\n\nBenefícios:\n✅ Suporte humanizado\n✅ Relatórios personalizados\n✅ Controle total de estoque\n✅ Emissão de notas fiscais\n✅ Integração TEF\n\nQuer saber mais? Acesse: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Olá! Sou Marcelo da Max Suport Sistemas. Nosso sistema pode transformar sua empresa de varejo.\n\nPor apenas R$ 150,00 por mês, você terá:\n✅ Controle total do seu negócio\n✅ Suporte rápido e eficiente\n✅ Relatórios detalhados\n✅ Geração de etiquetas\n✅ E muito mais!\n\nQuer saber como? Acesse: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Oi! Aqui é Marcelo da Max Suport. Estamos oferecendo o sistema mais completo para varejo, a partir de R$ 150,00 por mês!\n\nDestaques:\n✅ Atendimento rápido\n✅ Controle de estoque e vendas\n✅ Integração TEF\n✅ Geração de etiquetas\n✅ Suporte humanizado\n\nVisite: https://maxsuport.com e saiba mais!\n\n😊 Não cobramos taxa de instalação",
    "Sou Marcelo Lima, da Max Suport Sistemas. Estamos revolucionando a gestão de empresas de varejo com nosso sistema acessível.\n\nPor R$ 150,00/mês você terá:\n✅ Relatórios personalizados\n✅ Controle total do estoque\n✅ Integração TEF\n✅ Emissão de documentos fiscais\n✅ Suporte humanizado\n\nSaiba mais em nosso site: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Olá! Aqui é Marcelo da Max Suport. Oferecemos um sistema ideal para empresas de varejo.\n\nCom apenas R$ 150,00 mensais, você terá:\n✅ Gestão completa do seu negócio\n✅ Suporte rápido\n✅ Geração de etiquetas\n✅ Relatórios detalhados\n✅ E muito mais!\n\nAcesse: https://maxsuport.com e descubra mais!\n\n😊 Não cobramos taxa de instalação",
    "Oi, tudo bem? Sou Marcelo Lima da Max Suport Sistemas. Nosso sistema é ideal para empresas de varejo, começando por R$ 150,00 mensais.\n\nDestaques:\n✅ Controle de vendas\n✅ Relatórios detalhados\n✅ Suporte eficiente\n✅ Integração com TEF\n✅ Geração de etiquetas\n\nConfira em nosso site: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Sou Marcelo da Max Suport Sistemas. Estamos oferecendo soluções completas para empresas de varejo.\n\nPor apenas R$ 150,00 mensais, você terá:\n✅ Controle total de estoque e vendas\n✅ Relatórios sob medida\n✅ Suporte humanizado\n✅ Emissão de documentos fiscais\n\nSaiba mais acessando: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Oi! Aqui é Marcelo da Max Suport Sistemas. Nossa solução para empresas de varejo é acessível e completa.\n\nPor R$ 150,00/mês, você terá:\n✅ Controle total do seu estoque\n✅ Relatórios detalhados\n✅ Integração TEF\n✅ Suporte rápido\n✅ E muito mais!\n\nVisite nosso site: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Ei! Sou Marcelo Lima, da Max Suport Sistemas. Nosso sistema oferece tudo o que sua empresa de varejo precisa, por apenas R$ 150,00 mensais.\n\nCom ele, você terá:\n✅ Controle de estoque e vendas\n✅ Emissão de documentos fiscais\n✅ Relatórios personalizados\n✅ Suporte humanizado\n\nDescubra mais em: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Olá, tudo bem? Aqui é Marcelo da Max Suport. Estamos transformando a gestão de empresas de varejo com soluções completas e acessíveis.\n\nPor apenas R$ 150,00 por mês, você terá:\n✅ Relatórios detalhados\n✅ Controle total do estoque\n✅ Suporte rápido\n✅ Integração TEF\n✅ E muito mais!\n\nConfira no site: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Sou Marcelo da Max Suport Sistemas. Com nosso sistema, empresas de varejo têm gestão completa e eficiente.\n\nPor R$ 150,00 mensais, você terá:\n✅ Controle total de estoque e vendas\n✅ Relatórios personalizados\n✅ Suporte humanizado\n✅ Integração TEF\n✅ Geração de etiquetas\n\nSaiba mais em: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação",
    "Oi, tudo bem? Sou Marcelo da Max Suport Sistemas. Temos o sistema perfeito para empresas de varejo.\n\nPor R$ 150,00/mês, oferecemos:\n✅ Gestão completa\n✅ Controle de estoque\n✅ Relatórios detalhados\n✅ Suporte humanizado\n✅ E muito mais!\n\nQuer saber mais? Visite: https://maxsuport.com\n\n😊 Não cobramos taxa de instalação"
]


cumprimentos = {
    "manha": [
        "Bom dia, tudo bem com você?",
        "Bom dia, como você está hoje?",
        "Bom dia, como estão as coisas por aí?",
        "Bom dia, tá tudo certo por aí?",
    ],
    "tarde": [
        "Boa tarde, tudo certo com você?",
        "Boa tarde, tá tudo bem por aí?",
        "Boa tarde, como estão as coisas com você?",
        "Boa tarde, como você tem passado?"
    ]
}

def gerar_cumprimento():
    hora = datetime.now().hour

    if hora < 12:
        tipo = "manha"
    elif hora < 18:
        tipo = "tarde"
    else:
        return None

    return random.choice(cumprimentos[tipo])