import language_tutor.languages as langs


def test_custom_task_present():
    for lang, types in langs.exercise_types.items():
        assert types[0] == ("Random", "Random")
        assert types[-1] == ("Custom", "Custom")
