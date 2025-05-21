import language_tutor


def test_version_defined():
    assert isinstance(language_tutor.__version__, str)
    assert language_tutor.__version__
