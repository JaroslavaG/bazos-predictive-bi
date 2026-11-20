# 📊 Bazoš Predictive Sales & Pricing BI

Automatizovaný analytický a predikčný dashboard pre sledovanie výkonnosti inzerátov na portáli **Bazoš.sk / Bazoš.cz**. Projekt spája web scraping, kontextové dáta (lokálne PSČ počasie, štátne sviatky SR/ČR, výplatné okná) a predikčný model pravdepodobnosti predaja do 14 dní do prehľadného GitHub Pages dashboardu s podporou prepínania jazykov (**SK / EN**).

---

## ✨ Hlavné funkcie

* **🖼️ Automatické náhľady a presná extrakcia z Bazoša (`monitor.py`):**
  * Automaticky sťahuje **titulnú fotku** každého inzerátu priamo zo štruktúry Bazoša bez ukladania obrázkov do repozitára.
  * Počíta **presný počet fotografií** prísne podľa ID konkrétneho inzerátu (ignoruje odporúčané a podobné inzeráty v spodnej časti stránky).
* **💶 Inteligentná detekcia režimu a výšky ceny (`extract_live_price`):**
  * Rozlišuje medzi číselnou cenou v tabuľke a režimom **„V texte“**.
  * Ak je na Bazoši nastavené *„V texte“*, automaticky vytiahne aktuálnu sumu priamo z popisu inzerátu, takže zmena ceny na Bazoši sa okamžite premietne do dashboardu aj výpočtu cenovej elasticity bez nutnosti ručne prepisovať konfiguráciu.
* **📈 Predikčný model pravdepodobnosti predaja (14-dňové okno):**
  * Vyhodnocuje skóre kvality inzerátu (počet fotiek, prítomnosť rozmerov/hmotnosti, dĺžku popisu), denné tempo videní (*velocity*), nasýtenie publika oproti benchmarku kategórie aj sezónne vplyvy.
* **🌍 Auto-PSČ Geolocation & Počasie (Open-Meteo API):**
  * Z detailu inzerátu automaticky extrahuje PSČ, mesto a GPS súradnice a priraďuje aktuálne lokálne počasie (dážď/sychravo zvyšuje návštevnosť interiérových kategórií, slnečné víkendy zas športových).
* **📅 Kalendárny & Behaviorálny kontext (SR & ČR):**
  * Zohľadňuje pracovné dni, víkendy, pohyblivé aj pevné štátne sviatky SR a ČR a silné povýplatné obdobie (10. – 18. deň v mesiaci).
* **📉 Analýza cenovej elasticity:**
  * Pri zmene ponukovej ceny automaticky vypočíta percentuálnu zmenu denného záujmu pred a po úprave ceny.
* **🌐 Dvojjazyčné rozhranie SK / EN (`i18n.js`):**
  * Bezpečný klientsky prekladač textových uzlov v reálnom čase bez narušenia interaktívnych grafov `Chart.js`.
* **🔔 Automatické e-mailové notifikácie:**
  * Pri poklese denného záujmu pod stanovené minimum alebo pri dosiahnutí cenového zlomu odošle analytický report s odporúčaným ďalším krokom.

---

## 🗂️ Štruktúra repozitára

| Súbor | Popis |
| :--- | :--- |
| `monitor.py` | Hlavný Python skript – sťahuje dáta z Bazoša, vyhodnocuje metriky, ukladá históriu a generuje `index.html`. |
| `inzeraty.json` | Konfiguračný zoznam sledovaných inzerátov (ID, kategória, názov, URL, východisková a cieľová cena, benchmark). |
| `historia_videni.csv` | Auditný denník denných meraní (dátum, PSČ lokalita, počasie, videnia, denný prírastok, cena, šanca predaja). |
| `index.html` | Automaticky generovaný responzívny BI dashboard s kartami inzerátov, grafmi (`Chart.js`) a auditnou tabuľkou. |
| `i18n.js` | Modul pre okamžité prepínanie jazyka dashboardu medzi slovenčinou (`🇸🇰 SK`) a angličtinou (`🇬🇧 EN`). |
| `.github/workflows/check_ads.yml` | GitHub Actions CI/CD pipeline na pravidelné spúšťanie unit testov, monitoringu a publikovanie zmien. |

---

## ⚙️ Ako pridať sledovaný inzerát

Všetky sledované položky sa spravujú v súbore **`inzeraty.json`**. Pre pridanie nového inzerátu stačí vložiť nový JSON objekt:

```json
{
  "id": "197721729",
  "kategoria": "sport_hracky",
  "nazov": "Fisher-Price Psíkov stolček Smart Stages SK/EN",
  "url": "[https://deti.bazos.sk/inzerat/197721729/fisher-price-psikov-stolcek-smart-stages-sken.php](https://deti.bazos.sk/inzerat/197721729/fisher-price-psikov-stolcek-smart-stages-sken.php)",
  "aktualna_cena": 25,
  "cielova_cena": 20,
  "min_denny_narast": 3,
  "benchmark_videni": 70
}
