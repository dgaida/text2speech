# Documentation Metrics

Dieses Dashboard zeigt die aktuelle Qualität und Abdeckung der Dokumentation sowie der Tests.

## 📊 Summary

| Metric | Status | Wert | Ziel |
|--------|--------|------|------|
| API-Abdeckung | ✅ | 100% | >95% |
| Test Coverage | ✅ | 98% | >90% |
| Build-Status | ✅ | Passing | - |
| Gebrochene Links | ✅ | 0 | 0 |

---

## 📈 API Documentation Coverage

Die API-Abdeckung wird automatisch mit `interrogate` gemessen. Sie stellt sicher, dass alle öffentlichen Klassen, Methoden und Funktionen korrekt dokumentiert sind.

```mermaid
pie title API-Abdeckung (interrogate)
    "Documented" : 100
    "Undocumented" : 0
```

---

## 🧪 Test Coverage

Die Test Coverage gibt an, wie viel Prozent des Quellcodes durch automatisierte Tests (Pytest) ausgeführt werden.

```mermaid
pie title Test Coverage (pytest-cov)
    "Covered" : 98
    "Not covered" : 2
```

---

## 🛠️ Documentation Quality

| Check | Tool | Status |
|-------|------|--------|
| Google-Style Docstrings | mkdocstrings | ✅ Passing |
| Markdown Linting | pymarkdown | ✅ Passing |
| Mermaid Diagramme | mermaid2 | ✅ Passing |
| Cross-Links | mkdocs | ✅ Passing |

---

## 🕒 Changelog Freshness

Der Changelog wird automatisch bei jedem Release über `git-cliff` aktualisiert, basierend auf den [Conventional Commits](https://www.conventionalcommits.org/).

---

*Last updated: Februar 2026*
