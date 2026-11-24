/**
 * Bazoš Predictive BI - Bezpečný SK / EN prepínač (i18n.js)
 * Prekladá iba textové uzly bez ničenia Chart.js canvasov a event listenerov.
 */
(function () {
  const EXACT_DICT = {
    "Ponuková hodnota": "Asking Portfolio Value",
    "Cieľová hodnota:": "Target Value:",
    "Celkový organický zásah": "Total Organic Reach",
    "Priemerná šanca predaja": "Avg. Sale Probability",
    "Predikčný model do 14 dní": "14-Day Predictive Model",
    "Geolokácia & Kalendár": "Geolocation & Calendar",
    "SR + ČR sviatky & výplatné okná": "SK + CZ holidays & payday windows",
    "Pravdepodobnosť predaja (Predikčný model)": "Sale Probability (Predictive Model)",
    "Celkové videnia": "Total Views",
    "Rýchlosť & Kalendár": "Velocity & Calendar",
    "Ponuková cena": "Asking Price",
    "Kvalita inzerátu": "Listing Quality Score",
    "Otvoriť na Bazoši →": "Open listing on Bazoš →",
    "📈 Kumulatívna krivka záujmu (Celkové videnia)": "📈 Cumulative Interest Curve (Total Views)",
    "📊 Denná dynamika prírastkov (Videnia / deň)": "📊 Daily View Velocity (Views / Day)",
    "📘 Štatistický manuál: Kedy a ako predať konkrétny typ produktu": "📘 Statistical Playbook: Optimal Timing & Strategy by Category",
    "Kategória produktu": "Product Category",
    "Zlaté časové okno": "Golden Time Window",
    "Šanca predaja do 14 dní": "14-Day Sale Probability",
    "Odporúčaný postup krok za krokom": "Recommended Step-by-Step Strategy",
    "Kočíky (3v1, športové)": "Strollers (3-in-1, pushchairs)",
    "Nedeľa 17:30–21:00, Streda večer": "Sunday 17:30–21:00, Wednesday evening",
    "Zverejniť po výplatách (10.–18. v mesiaci), uviesť rozmery vaničky a rámu, pri 120+ videniach obnoviť.": "Publish during payday window (10th–18th of month), list exact bassinet/frame dimensions, republish at 120+ views.",
    "Autosedačky (i-Size)": "Car Seats (i-Size)",
    "Pracovné dni 20:00–22:00, Nedeľa": "Weekdays 20:00–22:00, Sunday evening",
    "Uviesť normu ECE R129 a testy ADAC, obnovovať pred sviatkami a prázdninami.": "Highlight ECE R129 standard and ADAC safety ratings; republish ahead of holidays and travel seasons.",
    "Detské oblečenie & Obuv": "Kids Clothing & Footwear",
    "Piatok večer, Nedeľa podvečer": "Friday evening, Sunday late afternoon",
    "Spájať do balíkov podľa veľkosti, obnovovať pri náhlom ochladení alebo daždi.": "Bundle items by size; republish right when temperatures drop or rainy weather hits.",
    "Bicykle, Odrážadlá & Hračky": "Bikes, Balance Bikes & Toys",
    "Štvrtok – Nedeľa večer": "Thursday – Sunday evening",
    "Športové veci nahodiť vo štvrtok pred slnečným víkendom; hračky v daždivých dňoch.": "List bikes/outdoor gear on Thursday before a sunny weekend; list indoor toys on rainy days.",
    "Kolísky, Lehátka & Výbava": "Cradles, Bouncers & Gear",
    "Zverejniť po výplatách alebo v daždivých dňoch, uviesť nosnosť, rozmery a čistotu poťahu.": "Publish during payday windows or rainy days; specify weight limit, dimensions, and fabric cleanliness.",
    "🗂️ Auditný denník meraní (PSČ Lokalita + Počasie + Predikcia)": "🗂️ Measurement Audit Log (ZIP Location + Weather + Prediction)",
    "Dátum": "Date",
    "PSČ / Mesto": "ZIP / City",
    "Kalendár (SR/ČR)": "Calendar (SK/CZ)",
    "Počasie": "Weather",
    "Inzerát": "Listing",
    "Videnia": "Views",
    "Šanca": "Prob.",
    "End-to-End Predictive Pricing & Behavioral BI • SR & ČR Localization, Open-Meteo & Chart.js":
      "End-to-End Predictive Pricing & Behavioral BI • SK & CZ Localization, Open-Meteo & Chart.js"
  };

  const SUBSTRING_PAIRS = [
    ["SR & ČR Engine", "SK & CZ Engine"],
    ["Auto-PSČ Počasie", "Auto-ZIP Weather"],
    ["SR/ČR Sviatky & Payday", "SK/CZ Holidays & Payday"],
    ["Kočíky & Príslušenstvo", "Strollers & Accessories"],
    ["Autosedačky & Bezpečnosť", "Car Seats & Safety"],
    ["Detské oblečenie & Obuv", "Kids Clothing & Footwear"],
    ["Hračky, Bicykle & Šport", "Toys, Bikes & Sports"],
    ["Kolísky, Lehátka & Výbava", "Cradles, Bouncers & Gear"],
    ["📈 Dobrý trend", "📈 Healthy Trend"],
    ["☀️ Voľný deň", "☀️ Holiday/Weekend Dip"],
    ["⚠️ Útlm", "⚠️ Momentum Drop"],
    ["💡 Cenový zlom", "💡 Price Breakpoint"],
    ["🔄 Obnoviť", "🔄 Republish Due"],
    ["šanca)", "prob.)"],
    ["Dnešný prírastok:", "Today's Gain:"],
    ["videní/deň", "views/day"],
    ["videní", "views"],
    ["Dnes:", "Today:"],
    ["Cieľ:", "Target:"],
    ["vankúš", "buffer"],
    ["fotiek", "photos"],
    ["Cena: V texte", "Price: In text"],
    ["Cena: Číselná", "Price: Numeric"],
    ["📊 Čo hovorí toto číslo:", "📊 What this metric tells us:"],
    ["🎯 Odporúčaný krok:", "🎯 Recommended Action:"],
    ["📘 Štatistický návod kategórie:", "📘 Category Statistical Playbook:"],
    ["Sledované:", "Tracked:"],
    ["Špička:", "Peak window:"],
    ["Pracovný deň", "Workday"],
    ["Víkend", "Weekend"],
    ["Sviatok", "Holiday"],
    ["Pondelok", "Monday"],
    ["Utorok", "Tuesday"],
    ["Streda", "Wednesday"],
    ["Štvrtok", "Thursday"],
    ["Piatok", "Friday"],
    ["Sobota", "Saturday"],
    ["Nedeľa", "Sunday"],
    ["☀️ Slnečno", "☀️ Sunny"],
    ["⛅ Oblačno", "⛅ Cloudy"],
    ["🌧️ Dážď / Sychravo", "🌧️ Rainy / Overcast"],
    ["❄️ Sneženie", "❄️ Snowfall"],
    ["Číslo ", "Current count of "],
    ["benchmarku kategórie", "of category benchmark"],
    ["predstavuje úvodnú fázu. Skóre kvality inzerátu je", "represents the initial phase. Listing quality score is"],
    ["čo dáva realistickú pravdepodobnosť predaja do 14 dní", "yielding a realistic 14-day sale probability of"],
    ["Tempo ", "Velocity of "],
    ["je optimálne", "is optimal"],
    ["(aktuálne prebieha silné povýplatné obdobie 10.–18. v mesiaci!)", "(active post-payday window: 10th–18th of the month!)"],
    ["Najbližšie zlaté okno:", "Next golden window:"],
    ["Nedeľa 17:30 – 21:00 a Streda 19:30 – 21:30", "Sunday 17:30–21:00 & Wednesday 19:30–21:30"],
    ["Pracovné dni 20:00 – 22:00 a Nedeľa večer", "Weekdays 20:00–22:00 & Sunday evening"]
  ];

  // Uložíme si pôvodné slovenské texty priamo do každého textového uzla
  function cacheOriginalTextNodes() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
    let node;
    while ((node = walker.nextNode())) {
      if (node.parentElement && ["SCRIPT", "STYLE"].includes(node.parentElement.tagName)) continue;
      if (node.parentElement && node.parentElement.closest("#lang-switcher-box")) continue;
      if (node._skOriginal === undefined) {
        node._skOriginal = node.nodeValue;
      }
    }
  }

  function translateText(skText) {
    const trimmed = skText.trim();
    if (!trimmed) return skText;

    if (EXACT_DICT[trimmed]) {
      return skText.replace(trimmed, EXACT_DICT[trimmed]);
    }

    let out = skText;
    for (const [sk, en] of SUBSTRING_PAIRS) {
      if (out.includes(sk)) {
        out = out.split(sk).join(en);
      }
    }
    return out;
  }

  function setLanguage(lang) {
    cacheOriginalTextNodes();
    localStorage.setItem("bi_dashboard_lang", lang);
    document.documentElement.lang = lang;

    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
    let node;
    while ((node = walker.nextNode())) {
      if (node._skOriginal === undefined) continue;
      node.nodeValue = lang === "en" ? translateText(node._skOriginal) : node._skOriginal;
    }

    // Aktualizácia farby tlačidiel
    const btnSk = document.getElementById("btn-lang-sk");
    const btnEn = document.getElementById("btn-lang-en");
    if (btnSk && btnEn) {
      btnSk.style.background = lang === "sk" ? "#2563eb" : "#1e293b";
      btnEn.style.background = lang === "en" ? "#2563eb" : "#1e293b";
    }
  }

  function initSwitcher() {
    const topbarInner = document.querySelector(".topbar-inner");
    if (!topbarInner || document.getElementById("lang-switcher-box")) return;

    const box = document.createElement("div");
    box.id = "lang-switcher-box";
    box.style.cssText = "display:flex;gap:6px;align-items:center;";
    box.innerHTML = `
      <button type="button" id="btn-lang-sk" style="cursor:pointer;padding:5px 10px;border-radius:6px;border:1px solid #334155;font-size:12px;font-weight:600;background:#2563eb;color:#fff;">🇸🇰 SK</button>
      <button type="button" id="btn-lang-en" style="cursor:pointer;padding:5px 10px;border-radius:6px;border:1px solid #334155;font-size:12px;font-weight:600;background:#1e293b;color:#fff;">🇬🇧 EN</button>
    `;
    topbarInner.appendChild(box);

    document.getElementById("btn-lang-sk").addEventListener("click", () => setLanguage("sk"));
    document.getElementById("btn-lang-en").addEventListener("click", () => setLanguage("en"));

    const saved = localStorage.getItem("bi_dashboard_lang") || "sk";
    setLanguage(saved);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSwitcher);
  } else {
    initSwitcher();
  }
})();
