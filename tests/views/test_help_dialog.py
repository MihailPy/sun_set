def test_help_dialog_loads_markdown(qtbot, tmp_path):
    from sun_set.views.help_dialog import HelpDialog

    guide_path = tmp_path / "guide.md"
    guide_path.write_text("# Тестовое руководство", encoding="utf-8")

    dialog = HelpDialog(guide_path)
    qtbot.addWidget(dialog)

    assert "Тестовое руководство" in dialog.text_browser.toPlainText()


def test_help_dialog_shows_error_when_guide_missing(qtbot, tmp_path):
    from sun_set.views.help_dialog import HelpDialog

    dialog = HelpDialog(tmp_path / "missing.md")
    qtbot.addWidget(dialog)

    assert dialog.text_browser.toPlainText() == (
        "Не удалось загрузить руководство пользователя."
    )
