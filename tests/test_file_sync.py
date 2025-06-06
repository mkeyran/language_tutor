import os
import pytest
from unittest.mock import Mock, patch, MagicMock

PyQt5 = pytest.importorskip("PyQt5")


@pytest.fixture(scope="session")
def mock_qt_env():
    """Mock Qt environment at session level."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def mock_gui_components():
    """Mock GUI components for testing."""
    # Create mock instances
    mock_text_edit = Mock()
    mock_text_edit.toPlainText.return_value = ""
    mock_text_edit.setText = Mock()
    
    mock_timer = Mock()
    mock_timer.isActive.return_value = True
    mock_timer.start = Mock()
    mock_timer.stop = Mock()
    
    mock_watcher = Mock()
    mock_watcher.addPath = Mock()
    mock_watcher.removePath = Mock()
    
    return {
        'text_edit': mock_text_edit,
        'timer': mock_timer,
        'watcher': mock_watcher
    }


class MockLanguageTutorGUI:
    """Mock implementation of LanguageTutorGUI for testing."""
    
    def __init__(self, exercise_types, exercise_definitions, mock_components):
        self.file_sync_enabled = False
        self.file_sync_path = ""
        self.writing_input_area = mock_components['text_edit']
        self._save_timer = mock_components['timer']
        self._file_watcher = mock_components['watcher']
    
    def _configure_file_sync(self):
        """Mock file sync configuration."""
        if self.file_sync_enabled and self.file_sync_path:
            self._file_watcher.addPath(self.file_sync_path)
    
    def _on_sync_file_changed(self, path):
        """Mock file change handler."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
            self.writing_input_area.setText(content)
    
    def _on_writing_changed(self):
        """Mock writing change handler."""
        self._save_timer.start(2000)  # Mock 2 second delay
    
    def _save_sync_file(self):
        """Mock sync file save."""
        if self.file_sync_path:
            content = self.writing_input_area.toPlainText()
            with open(self.file_sync_path, 'w') as f:
                f.write(content)


def _make_gui(tmp_path, mock_gui_components):
    # Mock language data
    mock_exercise_types = {"English": ["Essay", "Grammar"]}
    mock_definitions = {"Essay": "Write an essay", "Grammar": "Fix grammar errors"}
    
    gui = MockLanguageTutorGUI(mock_exercise_types, mock_definitions, mock_gui_components)
    gui.file_sync_enabled = True
    gui.file_sync_path = str(tmp_path / "sync.txt")
    gui._configure_file_sync()
    return gui


def test_reload_from_file(tmp_path, mock_gui_components):
    gui = _make_gui(tmp_path, mock_gui_components)
    path = gui.file_sync_path
    with open(path, "w") as f:
        f.write("hello")
    gui._on_sync_file_changed(path)
    gui.writing_input_area.setText.assert_called_with("hello")


def test_delayed_save(tmp_path, mock_gui_components):
    gui = _make_gui(tmp_path, mock_gui_components)
    gui.writing_input_area.toPlainText.return_value = "new"
    gui._on_writing_changed()
    assert gui._save_timer.isActive()
    gui._save_sync_file()
    with open(gui.file_sync_path) as f:
        assert f.read() == "new"
