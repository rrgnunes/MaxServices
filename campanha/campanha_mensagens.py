from datetime import datetime
import random

mensagens = [
    "Oi, tudo bem? 😊\nSou *Marcelo Lima*, da **Max Suport Sistemas**.\n\n📢 Em 2026, o **TEF será obrigatório no Ceará**!\nNosso sistema já está pronto para essa exigência:\n\n✅ Integração TEF completa\n✅ Controle de estoque e vendas\n✅ Emissão de documentos fiscais\n✅ Relatórios personalizados\n✅ Suporte humanizado\n\n💰 Tudo isso por apenas *R$ 150,00/mês*!\n\n🔗 Saiba mais:\nhttps://maxsuport.com",
    "Olá! 👋\nSou Marcelo da **Max Suport Sistemas**.\n\n⚠️ *Atenção, Ceará!* A partir de 2026, o TEF será obrigatório.\n\nNosso sistema já vem com:\n✅ TEF integrado\n✅ Emissão fiscal\n✅ Relatórios sob medida\n✅ Controle total do estoque\n\n💳 Fique pronto antes do prazo!\n\n🔗 Acesse:\nhttps://maxsuport.com",
    "Oi, tudo bem?\nAqui é *Marcelo Lima*, da **Max Suport Sistemas**.\n\n📌 2026 trará a *obrigatoriedade do TEF no Ceará*.\nEstamos prontos para ajudar:\n\n✅ TEF homologado\n✅ Suporte humanizado\n✅ Controle de vendas\n✅ Relatórios completos\n\n💰 Apenas R$ 150,00/mês!\n\n🔗 Veja mais:\nhttps://maxsuport.com",
    "Ei! 🚀\nMarcelo da **Max Suport Sistemas** aqui.\n\n📢 *Empresário do Ceará*, prepare-se:\nA partir de 2026, o TEF será exigência legal.\n\n✅ TEF integrado\n✅ Emissão fiscal completa\n✅ Relatórios detalhados\n✅ Controle de estoque e vendas\n\n💳 Já quer se adequar?\n\n🔗 Acesse agora:\nhttps://maxsuport.com",
    "Olá! 😃\nSou Marcelo da **Max Suport Sistemas**.\n\n⚠️ TEF será obrigatório no Ceará em 2026.\nGaranta já seu sistema compatível:\n\n✅ TEF homologado\n✅ Relatórios personalizados\n✅ Controle de estoque\n✅ Suporte rápido\n\n💰 Apenas R$ 150,00/mês!\n\n🔗 Confira:\nhttps://maxsuport.com",
    "Oi, tudo bem?\nMarcelo da **Max Suport Sistemas** aqui.\n\n📌 TEF no Ceará será *obrigatório em 2026*.\nNosso sistema já está pronto:\n\n✅ Integração TEF\n✅ Relatórios sob medida\n✅ Controle total do negócio\n✅ Emissão de NF-e e NFC-e\n\n💳 Não deixe para a última hora!\n\n🔗 Saiba mais:\nhttps://maxsuport.com",
    "Ei! 👋\nSou Marcelo Lima, da **Max Suport Sistemas**.\n\n🚨 A partir de 2026, o TEF será obrigatório no Ceará.\n\nCom nosso sistema você tem:\n✅ TEF integrado\n✅ Suporte humanizado\n✅ Controle de estoque e vendas\n✅ Relatórios completos\n\n💰 Só R$ 150,00/mês!\n\n🔗 Veja:\nhttps://maxsuport.com",
    "Oi, tudo bem?\nAqui é Marcelo da **Max Suport Sistemas**.\n\n⚠️ TEF será exigido no Ceará em 2026.\n\n✅ TEF pronto para exigência fiscal\n✅ Emissão fiscal\n✅ Controle de estoque\n✅ Relatórios detalhados\n\n💳 Prepare-se já!\n\n🔗 Acesse:\nhttps://maxsuport.com",
    "Olá! 😀\nSou Marcelo da **Max Suport Sistemas**.\n\n📢 *Ceará*: TEF obrigatório a partir de 2026.\n\nNosso sistema oferece:\n✅ TEF integrado\n✅ Suporte rápido\n✅ Controle de vendas\n✅ Relatórios sob medida\n\n💰 Por apenas R$ 150,00/mês!\n\n🔗 Saiba mais:\nhttps://maxsuport.com",
    "Oi! 👋\nMarcelo da **Max Suport Sistemas** falando.\n\n🚨 TEF será obrigatório no Ceará em 2026.\n\n✅ Integração TEF\n✅ Emissão fiscal\n✅ Relatórios personalizados\n✅ Controle total do estoque\n\n💳 Fique pronto antes da lei entrar em vigor!\n\n🔗 Confira:\nhttps://maxsuport.com",
    "Sou *Marcelo Lima*, da **Max Suport Sistemas**.\n\n⚠️ 2026: TEF será obrigatório no Ceará.\n\n✅ TEF integrado\n✅ Controle de estoque\n✅ Emissão de NF-e e NFC-e\n✅ Suporte humanizado\n\n💰 Apenas R$ 150,00/mês!\n\n🔗 Veja mais:\nhttps://maxsuport.com",
    "Olá! 😊\nAqui é Marcelo da **Max Suport Sistemas**.\n\n📌 TEF será exigência no Ceará a partir de 2026.\n\n✅ TEF homologado\n✅ Gestão completa\n✅ Relatórios detalhados\n✅ Suporte rápido\n\n💳 Comece hoje!\n\n🔗 Acesse:\nhttps://maxsuport.com",
    "Oi, tudo bem?\nSou Marcelo Lima da **Max Suport Sistemas**.\n\n🚨 TEF obrigatório no Ceará a partir de 2026.\n\n✅ TEF integrado\n✅ Controle de vendas\n✅ Relatórios sob medida\n✅ Suporte humanizado\n\n🔗 Saiba mais:\nhttps://maxsuport.com",
    "Sou Marcelo da **Max Suport Sistemas**.\n\n📢 Prepare-se para o TEF obrigatório no Ceará (2026).\n\n✅ Integração TEF\n✅ Emissão fiscal\n✅ Controle total do estoque\n✅ Relatórios completos\n\n💰 Apenas R$ 150,00/mês!\n\n🔗 Confira:\nhttps://maxsuport.com",
    "Oi! 😀\nAqui é Marcelo da **Max Suport Sistemas**.\n\n⚠️ TEF obrigatório no Ceará em 2026.\n\n✅ TEF homologado\n✅ Relatórios detalhados\n✅ Controle de vendas e estoque\n✅ Suporte humanizado\n\n💳 Já quer se adequar?\n\n🔗 Veja:\nhttps://maxsuport.com",
    "Ei! 👋\nSou Marcelo Lima, da **Max Suport Sistemas**.\n\n📌 Ceará: TEF será exigido a partir de 2026.\n\n✅ Integração TEF\n✅ Gestão completa\n✅ Relatórios precisos\n✅ Suporte rápido\n\n💰 Só R$ 150,00/mês!\n\n🔗 Mais detalhes:\nhttps://maxsuport.com",
    "Olá, tudo bem?\nAqui é Marcelo da **Max Suport Sistemas**.\n\n🚨 Prepare-se para o TEF obrigatório no Ceará (2026).\n\n✅ TEF integrado\n✅ Controle de estoque\n✅ Emissão fiscal\n✅ Relatórios personalizados\n\n🔗 Saiba mais:\nhttps://maxsuport.com",
    "Sou Marcelo da **Max Suport Sistemas**.\n\n⚠️ TEF será obrigatório no Ceará em 2026.\n\n✅ TEF homologado\n✅ Suporte humanizado\n✅ Controle total de vendas\n✅ Relatórios completos\n\n💳 Não espere!\n\n🔗 Veja:\nhttps://maxsuport.com",
    "Oi, tudo bem?\nSou Marcelo da **Max Suport Sistemas**.\n\n📌 TEF será exigido no Ceará a partir de 2026.\n\n✅ TEF integrado\n✅ Relatórios sob medida\n✅ Controle de estoque\n✅ Suporte rápido\n\n🔗 Acesse:\nhttps://maxsuport.com",
    "Ei! 🚀\nMarcelo da **Max Suport Sistemas** aqui.\n\n📢 Não espere 2026 para se adequar ao TEF no Ceará.\n\n✅ Integração TEF\n✅ Emissão fiscal\n✅ Controle de estoque e vendas\n✅ Relatórios personalizados\n\n💰 Tudo por R$ 150,00/mês!\n\n🔗 Saiba mais:\nhttps://maxsuport.com"
    "Oi, tudo bem? 😊\nSou *Marcelo Lima*, da **Max Suport Sistemas**.\n\n📢 Em 2026, o **TEF será obrigatório no Ceará**!\nNosso sistema já está pronto para essa exigência:\n\n✅ Integração TEF completa\n✅ Controle de estoque e vendas\n✅ Emissão de documentos fiscais\n✅ Relatórios personalizados\n✅ Suporte humanizado\n\n💰 Tudo isso por apenas *R$ 180,00/mês*!\n\n🔗 Saiba mais:\nhttps://maxsuport.com",
    "Olá! 👋\nSou Marcelo da **Max Suport Sistemas**.\n\n⚠️ *Atenção, Ceará!* A partir de 2026, o TEF será obrigatório.\n\nNosso sistema já vem com:\n✅ TEF integrado\n✅ Emissão fiscal\n✅ Relatórios sob medida\n✅ Controle total do estoque\n\n💳 Fique pronto antes do prazo!\n\n🔗 Acesse:\nhttps://maxsuport.com",
    "Oi, tudo bem?\nAqui é *Marcelo Lima*, da **Max Suport Sistemas**.\n\n📌 2026 trará a *obrigatoriedade do TEF no Ceará*.\nEstamos prontos para ajudar:\n\n✅ TEF homologado\n✅ Suporte humanizado\n✅ Controle de vendas\n✅ Relatórios completos\n\n💰 Apenas R$ 180,00/mês!\n\n🔗 Veja mais:\nhttps://maxsuport.com",
    "Ei! 🚀\nMarcelo da **Max Suport Sistemas** aqui.\n\n📢 *Empresário do Ceará*, prepare-se:\nA partir de 2026, o TEF será exigência legal.\n\n✅ TEF integrado\n✅ Emissão fiscal completa\n✅ Relatórios detalhados\n✅ Controle de estoque e vendas\n\n💳 Já quer se adequar?\n\n🔗 Acesse agora:\nhttps://maxsuport.com",
    "Olá! 😃\nSou Marcelo da **Max Suport Sistemas**.\n\n⚠️ TEF será obrigatório no Ceará em 2026.\nGaranta já seu sistema compatível:\n\n✅ TEF homologado\n✅ Relatórios personalizados\n✅ Controle de estoque\n✅ Suporte rápido\n\n💰 Apenas R$ 180,00/mês!\n\n🔗 Confira:\nhttps://maxsuport.com",
    "Oi, tudo bem?\nMarcelo da **Max Suport Sistemas** aqui.\n\n📌 TEF no Ceará será *obrigatório em 2026*.\nNosso sistema já está pronto:\n\n✅ Integração TEF\n✅ Relatórios sob medida\n✅ Controle total do negócio\n✅ Emissão de NF-e e NFC-e\n\n💳 Não deixe para a última hora!\n\n🔗 Saiba mais:\nhttps://maxsuport.com",
    "Ei! 👋\nSou Marcelo Lima, da **Max Suport Sistemas**.\n\n🚨 A partir de 2026, o TEF será obrigatório no Ceará.\n\nCom nosso sistema você tem:\n✅ TEF integrado\n✅ Suporte humanizado\n✅ Controle de estoque e vendas\n✅ Relatórios completos\n\n💰 Só R$ 180,00/mês!\n\n🔗 Veja:\nhttps://maxsuport.com",
    "Oi, tudo bem?\nAqui é Marcelo da **Max Suport Sistemas**.\n\n⚠️ TEF será exigido no Ceará em 2026.\n\n✅ TEF pronto para exigência fiscal\n✅ Emissão fiscal\n✅ Controle de estoque\n✅ Relatórios detalhados\n\n💳 Prepare-se já!\n\n🔗 Acesse:\nhttps://maxsuport.com",
    "Olá! 😀\nSou Marcelo da **Max Suport Sistemas**.\n\n📢 *Ceará*: TEF obrigatório a partir de 2026.\n\nNosso sistema oferece:\n✅ TEF integrado\n✅ Suporte rápido\n✅ Controle de vendas\n✅ Relatórios sob medida\n\n💰 Por apenas R$ 180,00/mês!\n\n🔗 Saiba mais:\nhttps://maxsuport.com",
    "Oi! 👋\nMarcelo da **Max Suport Sistemas** falando.\n\n🚨 TEF será obrigatório no Ceará em 2026.\n\n✅ Integração TEF\n✅ Emissão fiscal\n✅ Relatórios personalizados\n✅ Controle total do estoque\n\n💳 Fique pronto antes da lei entrar em vigor!\n\n🔗 Confira:\nhttps://maxsuport.com",
    "Sou *Marcelo Lima*, da **Max Suport Sistemas**.\n\n⚠️ 2026: TEF será obrigatório no Ceará.\n\n✅ TEF integrado\n✅ Controle de estoque\n✅ Emissão de NF-e e NFC-e\n✅ Suporte humanizado\n\n💰 Apenas R$ 180,00/mês!\n\n🔗 Veja mais:\nhttps://maxsuport.com",
    "Olá! 😊\nAqui é Marcelo da **Max Suport Sistemas**.\n\n📌 TEF será exigência no Ceará a partir de 2026.\n\n✅ TEF homologado\n✅ Gestão completa\n✅ Relatórios detalhados\n✅ Suporte rápido\n\n💳 Comece hoje!\n\n🔗 Acesse:\nhttps://maxsuport.com",
    "Oi, tudo bem?\nSou Marcelo Lima da **Max Suport Sistemas**.\n\n🚨 TEF obrigatório no Ceará a partir de 2026.\n\n✅ TEF integrado\n✅ Controle de vendas\n✅ Relatórios sob medida\n✅ Suporte humanizado\n\n🔗 Saiba mais:\nhttps://maxsuport.com",
    "Sou Marcelo da **Max Suport Sistemas**.\n\n📢 Prepare-se para o TEF obrigatório no Ceará (2026).\n\n✅ Integração TEF\n✅ Emissão fiscal\n✅ Controle total do estoque\n✅ Relatórios completos\n\n💰 Apenas R$ 180,00/mês!\n\n🔗 Confira:\nhttps://maxsuport.com",
    "Oi! 😀\nAqui é Marcelo da **Max Suport Sistemas**.\n\n⚠️ TEF obrigatório no Ceará em 2026.\n\n✅ TEF homologado\n✅ Relatórios detalhados\n✅ Controle de vendas e estoque\n✅ Suporte humanizado\n\n💳 Já quer se adequar?\n\n🔗 Veja:\nhttps://maxsuport.com",
    "Ei! 👋\nSou Marcelo Lima, da **Max Suport Sistemas**.\n\n📌 Ceará: TEF será exigido a partir de 2026.\n\n✅ Integração TEF\n✅ Gestão completa\n✅ Relatórios precisos\n✅ Suporte rápido\n\n💰 Só R$ 180,00/mês!\n\n🔗 Mais detalhes:\nhttps://maxsuport.com",
    "Olá, tudo bem?\nAqui é Marcelo da **Max Suport Sistemas**.\n\n🚨 Prepare-se para o TEF obrigatório no Ceará (2026).\n\n✅ TEF integrado\n✅ Controle de estoque\n✅ Emissão fiscal\n✅ Relatórios personalizados\n\n🔗 Saiba mais:\nhttps://maxsuport.com",
    "Sou Marcelo da **Max Suport Sistemas**.\n\n⚠️ TEF será obrigatório no Ceará em 2026.\n\n✅ TEF homologado\n✅ Suporte humanizado\n✅ Controle total de vendas\n✅ Relatórios completos\n\n💳 Não espere!\n\n🔗 Veja:\nhttps://maxsuport.com",
    "Oi, tudo bem?\nSou Marcelo da **Max Suport Sistemas**.\n\n📌 TEF será exigido no Ceará a partir de 2026.\n\n✅ TEF integrado\n✅ Relatórios sob medida\n✅ Controle de estoque\n✅ Suporte rápido\n\n🔗 Acesse:\nhttps://maxsuport.com",
    "Ei! 🚀\nMarcelo da **Max Suport Sistemas** aqui.\n\n📢 Não espere 2026 para se adequar ao TEF no Ceará.\n\n✅ Integração TEF\n✅ Emissão fiscal\n✅ Controle de estoque e vendas\n✅ Relatórios personalizados\n\n💰 Tudo por R$ 180,00/mês!\n\n🔗 Saiba mais:\nhttps://maxsuport.com"
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