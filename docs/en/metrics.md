# Documentation Metrics

This page visualizes the quality and status of the project documentation.

## Overview

| Metric | Status / Value | Source |
|---|---|---|
| API Doc Coverage | [![Interrogate](../assets/interrogate.svg)](../assets/interrogate.svg) | `interrogate` |
| Build Status | [![Docs](https://github.com/dgaida/text2speech/actions/workflows/docs.yml/badge.svg)](https://github.com/dgaida/text2speech/actions/workflows/docs.yml) | GitHub Actions |
| Last Update | <span id="last-update">Loading...</span> | CI Pipeline |
| Broken Links | <span id="broken-links">Loading...</span> | `lychee` |

## Detailed Statistics

<div id="metrics-dashboard">
  <p>Loading metrics from the last CI run...</p>
</div>

<script>
fetch('../assets/metrics.json')
  .then(response => response.json())
  .then(data => {
    document.getElementById('last-update').textContent = data.timestamp;
    document.getElementById('broken-links').textContent = data.broken_links || 'None';

    let html = '<ul>';
    for (const [key, value] of Object.entries(data)) {
      html += `<li><strong>${key}:</strong> ${value}</li>`;
    }
    html += '</ul>';
    document.getElementById('metrics-dashboard').innerHTML = html;
  })
  .catch(error => {
    document.getElementById('metrics-dashboard').innerHTML = '<p>Metrics currently unavailable. They will be generated during the next CI run.</p>';
  });
</script>
