# Beitragen

Vielen Dank, dass Sie zum `text2speech`-Projekt beitragen möchten!

## Entwicklungs-Setup

1. Repository klonen
2. Virtuelle Umgebung erstellen
3. Abhängigkeiten installieren:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

## Pull Request Prozess

1. Erstellen Sie einen neuen Branch für Ihr Feature oder Ihren Bugfix.
2. Schreiben Sie Tests für Ihre Änderungen.
3. Stellen Sie sicher, dass alle Tests bestehen (`pytest`).
4. Überprüfen Sie die Code-Qualität (`black`, `ruff`, `mypy`).
5. Achten Sie auf eine vollständige Dokumentation der neuen APIs (Google-Style).
6. Senden Sie Ihren Pull Request.

## Konventionelle Commits

Wir verwenden [Conventional Commits](https://www.conventionalcommits.org/), um automatisierte Changelogs zu generieren.

Beispiele:
- `feat: Unterstützung für neue Sprache hinzufügen`
- `fix: Behebung eines Speicherlecks in der Queue`
- `docs: Aktualisierung der API-Referenz`
