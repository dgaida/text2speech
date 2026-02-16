# Docstring Style Guide

Dieses Projekt folgt dem **Google Python Style Guide** für Docstrings. Dies stellt sicher, dass die Dokumentation konsistent ist und von Tools wie `mkdocstrings` korrekt verarbeitet werden kann.

## Grundformat

Ein Docstring sollte eine kurze Zusammenfassung enthalten, gefolgt von einer detaillierteren Beschreibung (falls erforderlich), den Argumenten, Rückgabewerten und ausgelösten Ausnahmen.

```python
def funktion(name: str, alter: int = 0) -> bool:
    """Kurze Zusammenfassung in einem Satz.

    Eine detailliertere Beschreibung, die erklärt, was die Funktion macht
    und warum man sie verwenden sollte.

    Args:
        name (str): Der Name der Person.
        alter (int): Das Alter der Person (Standard ist 0).

    Returns:
        bool: True, wenn der Vorgang erfolgreich war, andernfalls False.

    Raises:
        ValueError: Wenn der Name leer ist.
    """
    if not name:
        raise ValueError("Name darf nicht leer sein")
    return True
```

## Klassen

Klassen sollten einen Docstring direkt unter der Klassendefinition haben. Die `__init__`-Methode sollte ebenfalls dokumentiert werden.

```python
class Beispiel:
    """Kurze Zusammenfassung der Klasse.

    Längere Beschreibung der Klasse.
    """

    def __init__(self, wert: int):
        """Initialisiert die Klasse.

        Args:
            wert (int): Der Initialisierungswert.
        """
        self.wert = wert
```

## Automatisierung

Wir verwenden `interrogate`, um die Abdeckung der Docstrings zu messen. Jede öffentliche API muss dokumentiert sein.

```bash
# Prüfung der Docstring-Abdeckung
interrogate text2speech/
```
