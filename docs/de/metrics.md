# Dokumentations-Metriken

Diese Seite visualisiert die Qualität und den Status der Projektdokumentation.

## Übersicht

| Metrik | Status / Wert | Quelle |
|---|---|---|
| API Doc Abdeckung | [![Interrogate](../assets/interrogate.svg)](../assets/interrogate.svg) | `interrogate` |
| Build Status | [![Docs](https://github.com/dgaida/text2speech/actions/workflows/docs.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/docs.yml) | GitHub Actions |
| Letztes Update | <span id="last-update">Lade...</span> | CI Pipeline |
| Gebrochene Links | <span id="broken-links">Lade...</span> | `lychee` |

## Detaillierte Statistiken

<div id="metrics-dashboard">
  <p>Lade Metriken aus der letzten CI-Ausführung...</p>
</div>

<script>
fetch('../assets/metrics.json')
  .then(response => response.json())
  .then(data => {
    document.getElementById('last-update').textContent = data.timestamp;
    document.getElementById('broken-links').textContent = data.broken_links || 'Keine';

    let html = '<ul>';
    for (const [key, value] of Object.entries(data)) {
      html += `<li><strong>${key}:</strong> ${value}</li>`;
    }
    html += '</ul>';
    document.getElementById('metrics-dashboard').innerHTML = html;
  })
  .catch(error => {
    document.getElementById('metrics-dashboard').innerHTML = '<p>Metriken derzeit nicht verfügbar. Sie werden beim nächsten CI-Lauf generiert.</p>';
  });
</script>
