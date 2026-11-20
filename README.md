# 📊 Bazoš Predictive BI & Listing Monitor (SK & CZ)

[![CI/CD Monitoring](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/JaroslavaG/bazos-predictive-bi)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Bilingual](https://img.shields.io/badge/Dashboard-SK%20%2F%20EN-16a34a)](https://jaroslavag.github.io/bazos-predictive-bi/)

> 🇬🇧 **English Summary below** | 🇸🇰 **Slovenský popis projektu**

🔗 **Live Dashboard (GitHub Pages):** [https://jaroslavag.github.io/bazos-predictive-bi/](https://jaroslavag.github.io/bazos-predictive-bi/)

---

## 🖼️ Ukážka živého BI Dashboardu / Dashboard Preview

### 🇸🇰 Prehľad portfólia, predikcie predaja a kontext počasia (SK)
![Bazoš Predictive BI Dashboard SK](assets/dashboard-sk.png)

### 🇬🇧 Interaktívne grafy vývoja a bilingválne rozhranie (EN)
![Bazoš Predictive BI Charts EN](assets/dashboard-charts-en.png)

---

## ⚙️ Architektúra riešenia (End-to-End CI/CD & BI Pipeline)

```mermaid
flowchart LR
    A[Bazoš.sk / .cz HTML] -->|BeautifulSoup4 Scraper| B(monitor.py)
    C[Open-Meteo API<br/>Auto-PSČ & GPS] --> B
    D[SR & ČR Kalendár<br/>Sviatky + Payday] --> B
    E[test_monitor.py<br/>8 Unit & Int. Testov] -->|GitHub Actions CI| B
    B -->|Časové rady| F[(historia_videni.csv)]
    B -->|Generovanie UI| G[index.html + i18n.js<br/>GitHub Pages]
    B -->|Detekcia zlomu| H[SMTP E-mail Alert]
