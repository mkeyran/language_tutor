import os
from language_tutor import config


def test_get_config_dir(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path))
    path = config.get_config_dir()
    assert path == os.path.join(tmp_path, 'language-tutor')
    assert os.path.isdir(path)


def test_get_paths(tmp_path, monkeypatch):
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path))
    config_dir = config.get_config_dir()
    assert config.get_config_path() == os.path.join(config_dir, 'config.json')
    assert config.get_state_path() == os.path.join(config_dir, 'state.json')
    export = config.get_export_path()
    assert os.path.isdir(export)
