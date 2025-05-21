# Definitions for Polish Writing Exercises (B2 Level based on provided PDF)
# Word counts adjusted based on examples +/- 10% tolerance mentioned in PDF

EXERCISE_DEFINITIONS = {
    "życzenia (wishes)": {
        "expected_length": (
            27,
            33,
        ),  # Target 30 words +/- 10% (based on gratulacje example)
        "requirements": "Include place and date, address to the recipient (optional in neutral style), main content specifying the occasion and text adjusted to it, signature. Use formal greetings and full name for official wishes, informal greetings and first name for private wishes.",
    },
    "pozdrowienia (greetings)": {
        "expected_length": (
            27,
            33,
        ),  # No direct example, assuming similar length to życzenia (Target 30 words +/- 10%)
        "requirements": "Include place and date, address to the recipient (optional in neutral style), main content, signature. Use formal greetings and full name for official greetings, informal greetings and first name for private greetings. Often sent on postcards.",
    },
    "zaproszenie (invitation)": {
        "expected_length": (27, 33),  # Target 30 words +/- 10%
        "requirements": "Specify who invites whom, the occasion, and where/when the event takes place. May include dress code information and request for RSVP. Use formal greetings and full name for official invitations, informal greetings and first name for private invitations.",
    },
    "zawiadomienie (notice)": {
        "expected_length": (36, 44),  # Target 40 words +/- 10%
        "requirements": "Informative text about an event that happened or will happen. Content varies based on official/private nature, sender/recipient, and event type. Must include place and date, what/where/when, and who is notifying.",
    },
    "ogłoszenie (announcement)": {
        "expected_length": (36, 44),  # Target 40 words +/- 10%
        "requirements": "Informative text, often about selling, swapping, renting, job offers, lost/found items. Should be concise. Must include who is announcing, the purpose (selling, buying, etc.), the subject (job, car, pet, etc.), and contact information.",
    },
    "odpowiedź na ogłoszenie (response to an announcement)": {
        "expected_length": (
            36,
            44,
        ),  # No direct example, assuming similar length to ogłoszenie (Target 40 words +/- 10%)
        "requirements": "A response addressing a specific announcement, likely expressing interest or providing requested information.",
    },
    "list prywatny (private letter/email - formal/informal)": {
        # Examples: 40 words (email apology -> 36-44), 100 words (letter complaint/advice -> 90-110).
        # Using the range for the 100-word letter examples as it represents a more substantial 'list'.
        "expected_length": (
            90,
            110,
        ),  # Target 100 words +/- 10% (based on letter examples)
        "requirements": "Include place and date (top right for letter), greeting, main content (introduction, development, conclusion), closing, and signature. Style (formal/informal) depends on context and recipient. Note: Shorter email forms (e.g., 40 words) also exist.",
    },
    "list urzędowy (official letter)": {
        "expected_length": (
            243,
            297,
        ),  # No direct example, assuming long form (Target ~270 words +/- 10%)
        "requirements": "Formal letter addressed to an institution or official body, following specific formatting and stylistic conventions. Must clearly state the purpose and provide necessary details/arguments.",
    },
    "list motywacyjny (motivation letter)": {
        "expected_length": (
            243,
            297,
        ),  # No direct example, assuming long form (Target ~270 words +/- 10%)
        "requirements": "Formal letter, typically for job or university applications, outlining qualifications, motivation, and suitability for the position/course.",
    },
    "podanie (application/request)": {
        "expected_length": (
            243,
            297,
        ),  # No direct example, assuming long form (Target ~270 words +/- 10%)
        "requirements": "Formal written request submitted to an authority or institution.",
    },
    "życiorys (CV/resume)": {
        "expected_length": (
            243,
            297,
        ),  # No direct example, assuming long form (Target ~270 words +/- 10%)
        "requirements": "Document summarizing one's professional and educational background.",
    },
    "opis (description - person, object, place, landscape, illustration)": {
        "expected_length": (
            243,
            297,
        ),  # No direct example, aligning with charakterystyka (Target 270 words +/- 10%)
        "requirements": "Detailed portrayal based on observation. Should be realistic and objective. Describe features in a specific order (e.g., general to specific). Includes introduction, development, and conclusion. Specific elements vary for person, object, place, landscape, or illustration.",
    },
    "charakterystyka (characterization - person, environment, etc.)": {
        "expected_length": (243, 297),  # Target 270 words +/- 10%
        "requirements": "Description combined with evaluation, covering external and internal aspects (for person) or key features (for environment/reality). Include relevant details, analysis, traits, and overall assessment.",
    },
    "opowiadanie (story)": {
        "expected_length": (234, 286),  # Target 260 words +/- 10%
        "requirements": "Narrates a sequence of real or fictional events. Consists of introduction, development, and conclusion. Usually written in the past tense, can include dialogue. Can be told in 1st or 3rd person. Should follow a logical sequence of events.",
    },
    "sprawozdanie (report)": {
        "expected_length": (180, 220),  # Target 200 words +/- 10%
        "requirements": "Relates events the writer participated in or witnessed (e.g., trip, concert, exhibition). Describes events chronologically. Usually written in the past tense. Should include time, place, circumstances, purpose, course of events, and evaluation.",
    },
    "recenzja (review)": {
        "expected_length": (243, 297),  # Target 270 words +/- 10%
        "requirements": "Expresses personal opinion about a film, book, show, etc.. Consists of introduction (identifying the subject), development (elements of description, summary, report), and conclusion (subjective evaluation with justification).",
    },
    "reklama (advertisement)": {
        "expected_length": (
            36,
            44,
        ),  # No direct example, assuming long form (Target ~270 words +/- 10%)
        "requirements": "Persuasive text designed to promote a product, service, or event. Should capture attention, highlight benefits, and include a call to action or contact information.",
    },
    "tekst argumentacyjny (rozprawka) (argumentative text/essay)": {
        "expected_length": (234, 286),  # Target 260 words +/- 10%
        "requirements": "Presents and defends a thesis on a given topic using logical arguments, evidence, and examples. Structure typically includes introduction (thesis), development (arguments/counterarguments), and conclusion (summary/reiteration of thesis).",
    },
    "esej (essay - school type)": {
        "expected_length": (
            243,
            297,
        ),  # Examples 260-270 words, using target 270 +/- 10%
        "requirements": "Reflective-informative writing developing and explaining a topic with the writer's views. Needs introduction, development, conclusion. Should include subjective views (opinion, commentary, interpretation, feelings) and supporting arguments/reflections.",
    },
}

# The list of exercise types remains the same
EXERCISE_TYPES = [
    ("życzenia (wishes)", "życzenia (wishes)"),
    ("pozdrowienia (greetings)", "pozdrowienia (greetings)"),
    ("zaproszenie (invitation)", "zaproszenie (invitation)"),
    ("zawiadomienie (notice)", "zawiadomienie (notice)"),
    ("ogłoszenie (announcement)", "ogłoszenie (announcement)"),
    (
        "odpowiedź na ogłoszenie (response to an announcement)",
        "odpowiedź na ogłoszenie (response to an announcement)",
    ),
    (
        "list prywatny (private letter/email - formal/informal)",
        "list prywatny (private letter/email - formal/informal)",
    ),
    ("list urzędowy (official letter)", "list urzędowy (official letter)"),
    ("list motywacyjny (motivation letter)", "list motywacyjny (motivation letter)"),
    ("podanie (application/request)", "podanie (application/request)"),
    ("życiorys (CV/resume)", "życiorys (CV/resume)"),
    (
        "opis (description - person, object, place, landscape, illustration)",
        "opis (description - person, object, place, landscape, illustration)",
    ),
    (
        "charakterystyka (characterization - person, environment, etc.)",
        "charakterystyka (characterization - person, environment, etc.)",
    ),
    ("opowiadanie (story)", "opowiadanie (story)"),
    ("sprawozdanie (report)", "sprawozdanie (report)"),
    ("recenzja (review)", "recenzja (review)"),
    ("reklama (advertisement)", "reklama (advertisement)"),
    (
        "tekst argumentacyjny (rozprawka) (argumentative text/essay)",
        "tekst argumentacyjny (rozprawka) (argumentative text/essay)",
    ),
    ("esej (essay - school type)", "esej (essay - school type)"),
]
