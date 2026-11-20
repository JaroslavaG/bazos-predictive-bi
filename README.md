# 📊 Bazoš Predictive Sales & Pricing BI

[![CI/CD Monitoring](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Bilingual](https://img.shields.io/badge/Dashboard-EN%20%2F%20SK-16a34a)](#)

An end-to-end automated analytics and predictive intelligence dashboard designed to monitor, evaluate, and optimize classified listings on **Bazoš.sk / Bazoš.cz**. The system integrates targeted HTML scraping, real-time price and cover-photo extraction, local ZIP-code weather, SK/CZ public holiday calendars, post-payday behavioral windows, and a 14-day sale probability model into a responsive **GitHub Pages BI dashboard** with instant **SK / EN** language switching.

> 🇸🇰 **Slovenský popis:** Automatizovaný analytický a predikčný BI nástroj na sledovanie výkonnosti inzerátov na portáli **Bazoš.sk / Bazoš.cz**. Spája automatické sťahovanie titulných fotiek a živých cien, lokálne počasie podľa PSČ, kalendár sviatkov SR/ČR, povýplatné okná a predikčný model pravdepodobnosti predaja do 14 dní v prehľadnom dvojjazyčnom dashboarde (**SK / EN**).

---

## 🖼️ Live Dashboard Preview

> *Note: Upload a screenshot of your live dashboard as `dashboard-preview.png` into the root of this repository to display it automatically below.*

![Bazoš Predictive BI Dashboard Preview](dashboard-preview.png)

Each listing card automatically pulls its **live cover thumbnail** directly from Bazoš and displays:
* **14-Day Sale Probability** calculated by the conservative category-calibrated predictive model.
* **Total Views & Daily Velocity** benchmarked against category saturation thresholds.
* **Local ZIP-Code Weather & Calendar Context** (workday, weekend, SK/CZ holiday, payday window).
* **Live Asking Price vs. Target Price Buffer** (automatically synced from either the price table or *"In text"* descriptions).
* **Listing Quality Score** (ID-scoped photo count, presence of exact dimensions/weight, description richness).

---

## 🏗️ System Architecture & Data Pipeline

```text
┌─────────────────────┐      ┌──────────────────────────────────────────┐
│   inzeraty.json     │─────▶│               monitor.py                 │
│ (Tracked Listings & │      │ 1. ID-scoped HTML scraping (Bazoš)       │
│  Category Targets)  │      │ 2. Live price & cover photo extraction   │
└─────────────────────┘      │ 3. ZIP/GPS geocoding + Open-Meteo API    │
                             │ 4. SK/CZ holidays & payday context       │
                             │ 5. 14-day sale probability & elasticity  │
                             └────────────────────┬─────────────────────┘
                                                  │
                 ┌────────────────────────────────┼────────────────────────────────┐
                 ▼                                ▼                                ▼
┌─────────────────────────────────┐  ┌─────────────────────────┐  ┌────────────────────────────────┐
│       historia_videni.csv       │  │       index.html        │  │      SMTP Email Alerts         │
│  (Time-series audit log of      │  │ (Interactive Chart.js   │  │ (Automated action triggers on  │
│   views, weather & prices)      │  │  BI Dashboard + i18n)   │  │  momentum drops / breakpoints) │
└─────────────────────────────────┘  └────────────┬────────────┘  └────────────────────────────────┘
                                                  │
                                                  ▼
                                     ┌─────────────────────────┐
                                     │         i18n.js         │
                                     │ (Non-destructive SK/EN  │
                                     │  DOM text switcher)     │
                                     └─────────────────────────┘
