import os
import pytest

PyQt5 = pytest.importorskip("PyQt5")
from PyQt5.QtWidgets import QApplication
from language_tutor.gui_app import LanguageTutorGUI
from language_tutor.languages import exercise_types, definitions


def _make_gui(tmp_path):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    gui = LanguageTutorGUI(exercise_types=exercise_types, exercise_definitions=definitions)
    gui.file_sync_enabled = True
    gui.file_sync_path = str(tmp_path / "sync.txt")
    gui._configure_file_sync()
    return gui


def test_reload_from_file(tmp_path):
    gui = _make_gui(tmp_path)
    path = gui.file_sync_path
    with open(path, "w") as f:
        f.write("hello")
    gui._on_sync_file_changed(path)
    assert gui.writing_input_area.toPlainText() == "hello"


def test_delayed_save(tmp_path):
    gui = _make_gui(tmp_path)
    gui.writing_input_area.setText("new")
    gui._on_writing_changed()
    assert gui._save_timer.isActive()
    gui._save_sync_file()
    with open(gui.file_sync_path) as f:
        assert f.read() == "new"
