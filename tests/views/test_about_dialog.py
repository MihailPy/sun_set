from sun_set.views.about_dialog import AboutDialog


def test_about_dialog_shows_application_version(qtbot, monkeypatch):
    monkeypatch.setattr(
        "sun_set.views.about_dialog.get_app_version",
        lambda: "1.2.3",
    )

    dialog = AboutDialog()
    qtbot.addWidget(dialog)

    assert dialog.version_label.text() == "Версия 1.2.3"
