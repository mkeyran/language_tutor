# Definitions for Portuguese Writing Exercises

EXERCISE_DEFINITIONS = {
    'votos / felicitações (wishes / congratulations)': {
        'expected_length': (25, 30),
        'requirements': 'Incluir local e data, destinatário (opcional em estilo neutro), conteúdo principal especificando a ocasião e texto ajustado a ela, assinatura. Usar saudações formais e nome completo para votos/felicitações oficiais, saudações informais e primeiro nome para privados.'
    },
    'saudações (greetings)': {
        'expected_length': (25, 30),
        'requirements': 'Incluir local e data, destinatário (opcional em estilo neutro), conteúdo principal, assinatura. Usar saudações formais e nome completo para saudações oficiais, saudações informais e primeiro nome para saudações privadas. Frequentemente enviado em postais.'
    },
    'convite (invitation)': {
        'expected_length': (25, 30), # Based on examples specifying 30 words, fitting within 25-30 range.
        'requirements': 'Especificar quem convida quem, a ocasião, e onde/quando o evento ocorre. Pode incluir informações sobre o código de vestimenta (dress code) e pedido de RSVP (confirmação de presença). Usar saudações formais e nome completo para convites oficiais, saudações informais e primeiro nome para convites privados.'
    },
    'aviso / comunicado (notice)': {
        'expected_length': (25, 30), # Deduced short form
        'requirements': 'Texto informativo sobre um evento que aconteceu ou vai acontecer. O conteúdo varia com base na natureza oficial/privada, remetente/destinatário e tipo de evento. Deve incluir local e data, o quê/onde/quando, e quem está a notificar/comunicar.'
    },
    'anúncio (announcement/advertisement)': {
        'expected_length': (25, 30), # Based on examples specifying 30 words
        'requirements': 'Texto informativo, frequentemente sobre venda, troca, aluguer, ofertas de emprego, itens perdidos/achados. Deve ser conciso. Deve incluir quem anuncia, o propósito (vender, comprar, etc.), o assunto (emprego, carro, animal de estimação, etc.) e informações de contacto.'
    },
    'carta (letter - formal/informal private)': {
        'expected_length': (170, 175), # Based on examples specifying 170 or 175 words
        'requirements': 'Incluir local e data (canto superior direito), saudação ao destinatário, conteúdo principal (introdução declarando o propósito, desenvolvimento, conclusão), saudações de despedida e assinatura. O estilo (formal/informal) depende do contexto.'
    },
    'descrição (description - person, object, place)': {
        'expected_length': (170, 175), # Deduced long form
        'requirements': 'Retrato detalhado baseado na observação. Deve ser realista e objetivo. Descrever características numa ordem específica (ex: do geral para o específico). Inclui introdução, desenvolvimento e conclusão. Elementos específicos variam para pessoa, objeto ou lugar.'
    },
    'caracterização de pessoa (characterization of a person)': {
        'expected_length': (170, 175), # Deduced long form, matches example for similar task
        'requirements': 'Descrição combinada com avaliação, cobrindo aspetos externos e internos. Incluir dados pessoais (nome, idade, profissão), aparência, traços de caráter distintos (positivos/negativos), traços intelectuais, interesses e avaliação geral.'
    },
    'narração / história (story / narrative)': {
        'expected_length': (170, 175), # Based on examples specifying 170 words
        'requirements': 'Narra uma sequência de eventos reais ou fictícios. Consiste em introdução, desenvolvimento e conclusão. Geralmente escrito no pretérito (passado), pode incluir diálogo. Pode ser contado na 1ª ou 3ª pessoa. Deve seguir uma sequência lógica de eventos.'
    },
    'relato / relatório (report)': {
        'expected_length': (170, 175), # Deduced long form
        'requirements': 'Relata eventos nos quais o escritor participou ou testemunhou (ex: viagem, concerto). Descreve os eventos cronologicamente. Geralmente escrito no pretérito (passado). Deve incluir tempo, lugar, circunstâncias, propósito, curso dos eventos e avaliação.'
    },
    'crítica / resenha (review)': {
        'expected_length': (170, 175), # Deduced long form
        'requirements': 'Expressa opinião pessoal sobre um filme, livro, espetáculo, etc. Consiste em introdução (identificando o objeto), desenvolvimento (elementos de descrição, resumo, relato) e conclusão (avaliação subjetiva com justificação). Foco na opinião pessoal.'
    },
    'ensaio / redação (essay)': {
        'expected_length': (170, 175), # Deduced long form
        'requirements': 'Escrita reflexivo-informativa que desenvolve e explica um tópico com as opiniões do escritor. Ensaios/redações escolares precisam de introdução, desenvolvimento, conclusão. Deve incluir visões subjetivas (opinião, comentário, interpretação, sentimentos) e argumentos de apoio.'
    },
}


# List of Portuguese Exercise Types for UI or Selection
EXERCISE_TYPES = [
    ("votos / felicitações (wishes / congratulations)", "votos / felicitações (wishes / congratulations)"),
    ("saudações (greetings)", "saudações (greetings)"),
    ("convite (invitation)", "convite (invitation)"),
    ("aviso / comunicado (notice)", "aviso / comunicado (notice)"),
    ("anúncio (announcement/advertisement)", "anúncio (announcement/advertisement)"),
    ("carta (letter - formal/informal private)", "carta (letter - formal/informal private)"),
    ("descrição (description - person, object, place)", "descrição (description - person, object, place)"),
    ("caracterização de pessoa (characterization of a person)", "caracterização de pessoa (characterization of a person)"),
    ("narração / história (story / narrative)", "narração / história (story / narrative)"),
    ("relato / relatório (report)", "relato / relatório (report)"),
    ("crítica / resenha (review)", "crítica / resenha (review)"),
    ("ensaio / redação (essay)", "ensaio / redação (essay)"),
]