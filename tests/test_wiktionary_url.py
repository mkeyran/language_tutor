from language_tutor.utils import build_wiktionary_url


def test_build_wiktionary_url():
    assert build_wiktionary_url("test", "pl") == "https://pl.m.wiktionary.org/wiki/test"
    assert build_wiktionary_url("café", "en") == "https://en.m.wiktionary.org/wiki/caf%C3%A9"
