# Definitions for Polish Writing Exercises

EXCERCISE_DEFINITIONS = {
    'życzenia (wishes)': {
        'expected_length': (25, 30),
        'requirements': 'Include place and date, address to the recipient (optional in neutral style), main content specifying the occasion and text adjusted to it, signature. Use formal greetings and full name for official wishes, informal greetings and first name for private wishes.'
    },
    'pozdrowienia (greetings)': {
        'expected_length': (25, 30),
        'requirements': 'Include place and date, address to the recipient (optional in neutral style), main content, signature. Use formal greetings and full name for official greetings, informal greetings and first name for private greetings. Often sent on postcards.'
    },
    'zaproszenie (invitation)': {
        'expected_length': (25, 30), # Based on examples specifying 30 words, fitting within 25-30 range.
        'requirements': 'Specify who invites whom, the occasion, and where/when the event takes place. May include dress code information and request for RSVP. Use formal greetings and full name for official invitations, informal greetings and first name for private invitations.'
    },
    'zawiadomienie (notice)': {
        'expected_length': (25, 30), # Deduced short form
        'requirements': 'Informative text about an event that happened or will happen. Content varies based on official/private nature, sender/recipient, and event type. Must include place and date, what/where/when, and who is notifying.'
    },
    'ogłoszenie (announcement)': {
        'expected_length': (25, 30), # Based on examples specifying 30 words
        'requirements': 'Informative text, often about selling, swapping, renting, job offers, lost/found items. Should be concise. Must include who is announcing, the purpose (selling, buying, etc.), the subject (job, car, pet, etc.), and contact information.'
    },
    'list (letter - formal/informal private)': {
        'expected_length': (170, 175), # Based on examples specifying 170 or 175 words
        'requirements': 'Include place and date (top right), greeting to the addressee, main content (introduction stating purpose, development, conclusion), closing greetings, and signature. Style (formal/informal) depends on the context.'
    },
    'opis (description - person, object, place)': {
        'expected_length': (170, 175), # Deduced long form
        'requirements': 'Detailed portrayal based on observation. Should be realistic and objective. Describe features in a specific order (e.g., general to specific). Includes introduction, development, and conclusion. Specific elements vary for person, object, or place.'
    },
    'charakterystyka osoby (characterization of a person)': {
        'expected_length': (170, 175), # Deduced long form, matches example for similar task
        'requirements': 'Description combined with evaluation, covering external and internal aspects. Include personal data (name, age, job), appearance, distinguishing character traits (positive/negative), intellectual traits, interests, and overall assessment.'
    },
    'opowiadanie (story)': {
        'expected_length': (170, 175), # Based on examples specifying 170 words
        'requirements': 'Narrates a sequence of real or fictional events. Consists of introduction, development, and conclusion. Usually written in the past tense, can include dialogue. Can be told in 1st or 3rd person. Should follow a logical sequence of events.'
    },
    'sprawozdanie (report)': {
        'expected_length': (170, 175), # Deduced long form
        'requirements': 'Relates events the writer participated in or witnessed (e.g., trip, concert). Describes events chronologically. Usually written in the past tense. Should include time, place, circumstances, purpose, course of events, and evaluation.'
    },
    'recenzja (review)': {
        'expected_length': (170, 175), # Deduced long form
        'requirements': 'Expresses personal opinion about a film, book, show, etc.. Consists of introduction (identifying the subject), development (elements of description, summary, report), and conclusion (subjective evaluation with justification). Note: Refers to expressing an opinion, not journalistic review genre.'
    },
    'esej (essay)': {
        'expected_length': (170, 175), # Deduced long form
        'requirements': 'Reflective-informative writing developing and explaining a topic with the writer\'s views. School essays need introduction, development, conclusion. Should include subjective views (opinion, commentary, interpretation, feelings) and supporting arguments.'
    },
}


EXERCISE_TYPES = [
    ("życzenia (wishes)", "życzenia (wishes)"),
    ("pozdrowienia (greetings)", "pozdrowienia (greetings)"),
    ("zaproszenie (invitation)", "zaproszenie (invitation)"),
    ("zawiadomienie (notice)", "zawiadomienie (notice)"),
    ("ogłoszenie (announcement)", "ogłoszenie (announcement)"),
    ("list (letter - formal/informal private)", "list (letter - formal/informal private)"),
    ("opis (description - person, object, place)", "opis (description - person, object, place)"),
    ("charakterystyka osoby (characterization of a person)", "charakterystyka osoby (characterization of a person)"),
    ("opowiadanie (story)", "opowiadanie (story)"),
    ("sprawozdanie (report)", "sprawozdanie (report)"),
    ("recenzja (review)", "recenzja (review)"),
    ("esej (essay)", "esej (essay)"),
]