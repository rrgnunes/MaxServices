import random

frases_diaria = [
    "🎉 Outubro chegou e o Studio Ruby está em clima de aniversário, @cliente! 🎉\n💝 Todas as clientes que realizarem protocolos neste mês estarão concorrendo automaticamente ao nosso sorteio de prêmios incríveis!\n✨ Venha celebrar com a gente, cuide-se e ainda concorra a presentões.\nAgende já o seu horário! 💫",

    "🎊 O aniversário do Studio Ruby chegou, @cliente! 🎊\n💝 Durante todo o mês de outubro, quem realizar protocolos participa do sorteio de prêmios especiais.\n✨ É mês de comemorar cuidando da sua beleza e autoestima.\nGaranta sua vaga e venha celebrar! 🌟",

    "🎁 Outubro é mês de festa: aniversário do Studio Ruby, @cliente! 🎁\n💝 Todas as clientes que fizerem protocolos já entram automaticamente no sorteio de presentões no fim do mês.\n✨ Venha se cuidar, realçar sua beleza e comemorar com a gente.\nAgende agora mesmo! 🎊",

    "🌸 Outubro é mês de comemoração no Studio Ruby, @cliente! 🌸\n🎉 No nosso aniversário, quem realizar protocolos estará concorrendo a prêmios incríveis no sorteio especial.\n✨ Celebre, cuide-se e aproveite essa festa da beleza.\nReserve já seu horário! 💫",

    "🎊 O Studio Ruby está em festa de aniversário, @cliente! 🎊\n💝 Clientes que fizerem protocolos em outubro participam automaticamente do sorteio de prêmios exclusivos.\n✨ Mês de celebrar, de cuidar e de ganhar!\nAgende já e venha comemorar com a gente. 🌟",

    "🎉 Outubro é aniversário do Studio Ruby, @cliente! 🎉\n💝 Todas as clientes que realizarem protocolos durante este mês já estão dentro do nosso sorteio de prêmios maravilhosos.\n✨ Cuide de você e venha celebrar essa data especial.\nAgende já o seu horário! 💫",

    "🎊 O mês de outubro é especial: aniversário do Studio Ruby, @cliente! 🎊\n💝 Realize seu protocolo e participe automaticamente do sorteio de prêmios incríveis no final do mês.\n✨ Venha se cuidar e celebrar junto conosco.\nAgende já sua vaga! 🌸",

    "🎁 Outubro premiado em comemoração ao aniversário do Studio Ruby, @cliente! 🎁\n💝 Quem fizer protocolos neste mês já estará concorrendo ao nosso sorteio de presentões.\n✨ Venha cuidar da sua beleza e brindar conosco essa data especial.\nReserve seu horário agora mesmo! 🌟",

    "🌟 Outubro de festa no Studio Ruby, @cliente! 🌟\n🎉 Em comemoração ao nosso aniversário, todas as clientes que fizerem protocolos já estarão concorrendo ao sorteio de prêmios exclusivos.\n✨ Autocuidado, beleza e comemoração em um só lugar.\nAgende já o seu! 💝",

    "🎊 Outubro é mês de aniversário do Studio Ruby, @cliente! 🎊\n💝 Quem realizar protocolos em nosso estúdio estará automaticamente participando do sorteio de prêmios incríveis.\n✨ Venha se cuidar e comemorar essa data especial com a gente.\nGaranta já seu horário! 💫",

    "🎉 O aniversário do Studio Ruby merece comemoração, @cliente! 🎉\n💝 Neste mês de outubro, todas as clientes que fizerem protocolos concorrem automaticamente ao sorteio de prêmios.\n✨ Venha se cuidar, valorizar sua beleza e celebrar conosco.\nAgende já e participe!"
]

def selecionar_frase_diaria():
    frase = random.choice(frases_diaria)
    return frase