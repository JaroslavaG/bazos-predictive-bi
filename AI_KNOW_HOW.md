# 🤖 AI Know-How & Architektúra projektu (Kontext pre AI asistentov)

Tento dokument slúži ako kompletný technický a analytický kontext pre akýkoľvek AI model (Gemini, Claude, GPT), ktorý bude tento repozitár v budúcnosti upravovať, rozširovať alebo analyzovať dáta.

## 1. Účel a predajná stratégia
* **Cieľ:** Maximalizovať úspešnosť a rýchlosť predaja osobných/rodinných vecí na portáloch **Bazoš.sk** a **Bazoš.cz** za férovú cenu.
* **Stratégia „Cena v texte“:** V poli cena na Bazoši sa používa hodnota `V texte`, čím sa zvyšuje miera prekliku (CTR) zo zoznamu inzerátov. Návštevník si najprv prečíta technické parametre, rozmery a benefity, a až na konci vidí sumu. Systém stráži bod zlomu, kedy inzerát nazbiera veľa videní bez predaja.

## 2. Dátový model a súbory
* **`inzeraty.json`:** Vstupná konfigurácia (`id`, `kategoria` [`kocik`, `autosedacka`, `oblecenie`, `sport_hracky`], `nazov`, `url`, `aktualna_cena`, `cielova_cena`, `min_denny_narast`, `benchmark_videni`).
* **`historia_videni.csv`:** Časová rada so stĺpcami: `datum`, `krajina`, `lokalita`, `den`, `typ_dna`, `pocasie`, `id`, `kategoria`, `nazov`, `videnia`, `narast`, `cena`, `sanca_predaja_pct`.
* **`monitor.py`:** Modulárny Python skript (parsovanie HTML, geokódovanie PSČ, Open-Meteo počasie, kalendár SR/ČR + Veľká noc, Payday efekt 10.–18. deň v mesiaci, pravdepodobnostný model, cenová elasticita, generátor `index.html` a SMTP alerting).
* **`test_monitor.py`:** Sada 8 unit a integračných testov spúšťaných automaticky v CI/CD pred každým zberom dát.

## 3. Pokyny pre AI pri pridávaní nových inzerátov
Pri požiadavke na vytvorenie nového inzerátu:
1. Vytvor dôveryhodný, priateľský a vecný predajný text s overenými technickými parametrami (rozmery, nosnosť, normy) a trhovým návrhom ceny.
2. Vygeneruj pripravený JSON blok na pridanie do `inzeraty.json` so správnou kategóriou a trhovým benchmarkom videní.
