# 📊 Bazoš Predictive BI & Strážca Inzerátov (SR & ČR)

Automatizovaný systém na sledovanie návštevnosti, denného prírastku videní, cenovej elasticity a predikcie predaja pre inzeráty na portáloch **Bazoš.sk** a **Bazoš.cz**. Projekt beží bezplatne na **GitHub Actions (CI/CD)** a publikuje živý analytický dashboard cez **GitHub Pages**.

## ✨ Hlavné funkcie
* **Automatická geolokácia z PSČ inzerátu:** Skript sám vyčíta PSČ, mesto, krajinu (SR/ČR) a GPS súradnice priamo z URL adresy inzerátu a priradí lokálne počasie cez **Open-Meteo API**.
* **Kalendárny & Payday kontext (SR & ČR):** Rozpoznáva víkendy, fixné aj pohyblivé štátne sviatky pre Slovensko aj Česko (vrátane Veľkého piatku a Veľkonočného pondelka) a sleduje výplatné okná (10. – 18. deň v mesiaci).
* **Predikčný model úspechu predaja (%):** Vypočítava pravdepodobnosť realizácie predaja na základe kategórie produktu, rýchlosti videní (*View Velocity*), skóre kvality inzerátu, počasia a kalendára.
* **Detekcia cenovej elasticity:** Pri úprave ceny v `inzeraty.json` automaticky porovná priemerný denný záujem pred zľavou a po zľave.
* **E-mailové upozornenia & Živý Dashboard (`index.html`):** Pri poklese momenta alebo dosiahnutí cenového zlomu odošle e-mail s odporúčaním presného časového okna na obnovenie inzerátu.

## 🚀 Rýchle nastavenie (Krok za krokom)

### 1. Vytvorenie repozitára a nahratie súborov
1. Vytvor na GitHube nový repozitár (napr. `bazos-predictive-bi`) a nastav ho ako **Public** (potrebné pre bezplatné GitHub Pages).
2. Rozbaľ stiahnutý archív `bazos-strazca-komplet.zip` a nahraj súbory do repozitára (`inzeraty.json`, `monitor.py`, `test_monitor.py`, `requirements.txt`, `README.md`, `AI_KNOW_HOW.md`).
3. **Dôležité pre `.github/workflows/check_ads.yml`:** Pri nahrávaní cez webové rozhranie GitHubu prehliadač niekedy preskočí skrytý priečinok `.github`. Najistejšie je kliknúť na **Add file → Create new file**, do názvu súboru napísať presne `.github/workflows/check_ads.yml` a vložiť jeho obsah.

### 2. Nastavenie e-mailových upozornení (GitHub Secrets)
1. V Google účte zapni dvojstupňové overenie a v sekcii **Heslá aplikácií (App Passwords)** vygeneruj 16-miestne heslo pre *Poštu*.
2. V repozitári choď do **Settings → Secrets and variables → Actions → New repository secret** a pridaj:
   * `EMAIL_USER` – tvoja odosielacia Gmail adresa
   * `EMAIL_PASS` – vygenerované 16-miestne heslo aplikácie
   * `EMAIL_TO` – cieľová e-mailová adresa pre upozornenia

### 3. Prvé spustenie a zapnutie GitHub Pages
1. V záložke **Actions** vyber workflow **Strazca inzeratov Bazos** a klikni na **Run workflow**.
2. Prejdi do **Settings → Pages**, pri **Branch** vyber `main` a priečinok `/ (root)`, a klikni na **Save**.
