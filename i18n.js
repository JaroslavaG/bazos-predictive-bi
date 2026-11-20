/**
 * Bazoš Predictive BI - SK / EN Language Switcher (i18n.js)
 * Samostatný lokalizačný modul pre GitHub Pages dashboard.
 */
(function () {
  const DICT = {
    // Topbar & Header
    "Bazoš Predictive Sales & Pricing BI": "Bazoš Predictive Sales & Pricing BI",
    "SR & ČR Engine": "SK & CZ Engine",
    "Auto-PSČ Počasie": "Auto-ZIP Weather",
    "SR/ČR Sviatky & Payday": "SK/CZ Holidays & Payday",

    // KPI Cards
    "Ponuková hodnota": "Asking Portfolio Value",
    "Cieľová hodnota:": "Target Value:",
    "Celkový organický zásah": "Total Organic Reach",
    "Dnešný prírastok:": "Today's Gain:",
    "videní": "views",
    "Priemerná šanca predaja": "Avg. Sale Probability",
    "Predikčný model do 14 dní": "14-Day Predictive Model",
    "Geolokácia & Kalendár": "Geolocation & Calendar",
    "SR + ČR sviatky & výplatné okná": "SK + CZ holidays & payday windows",

    // Ad Cards
    "Kočíky & Príslušenstvo": "Strollers & Accessories",
    "Autosedačky & Bezpečnosť": "Car Seats & Safety",
    "Detské oblečenie & Obuv": "Kids Clothing & Footwear",
    "Hračky, Bicykle & Šport": "Toys, Bikes & Sports",
    "Pravdepodobnosť predaja (Predikčný model)": "Sale Probability (Predictive Model)",
    "Celkové videnia": "Total Views",
    "Dnes:": "Today:",
    "Rýchlosť & Kalendár": "Velocity & Calendar",
    "Ponuková cena": "Asking Price",
    "Cieľ:": "Target:",
    "vankúš": "buffer",
    "Kvalita inzerátu": "Listing Quality Score",
    "fotiek": "photos",
    "Cena:": "Price mode:",
    "V texte": "In text",
    "Číselná": "Numeric",
    "📊 Čo hovorí toto číslo:": "📊 What this metric tells us:",
    "🎯 Odporúčaný krok:": "🎯 Recommended Action:",
    "📘 Štatistický návod kategórie:": "📘 Category Statistical Playbook:",
    "Sledované:": "Tracked:",
    "Špička:": "Peak window:",
    "Otvoriť na Bazoši →": "Open listing on Bazoš →",

    // Badges
    "📈 Dobrý trend": "📈 Healthy Trend",
    "☀️ Voľný deň": "☀️ Holiday/Weekend Dip",
    "⚠️ Útlm": "⚠️ Momentum Drop",
    "💡 Cenový zlom": "💡 Price Breakpoint",
    "🔄 Obnoviť": "🔄 Republish Due",
    "šanca": "prob.",

    // Charts & Sections
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

    // Audit Log Table
    "🗂️ Auditný denník meraní (PSČ Lokalita + Počasie + Predikcia)": "🗂️ Measurement Audit Log (ZIP Location + Weather + Prediction)",
    "Dátum": "Date",
    "PSČ / Mesto": "ZIP / City",
    "Kalendár (SR/ČR)": "Calendar (SK/CZ)",
    "Počasie": "Weather",
    "Inzerát": "Listing",
    "Videnia": "Views",
    "Šanca": "Prob.",

    // Calendar & Weather dynamic terms
    "Pracovný deň": "Workday",
    "Víkend": "Weekend",
    "Sviatok": "Public Holiday",
    "Pondelok": "Monday",
    "Utorok": "Tuesday",
    "Streda": "Wednesday",
    "Štvrtok": "Thursday",
    "Piatok": "Friday",
    "Sobota": "Saturday",
    "Nedeľa": "Sunday",
    "☀️ Slnečno": "☀️ Sunny",
    "⛅ Oblačno": "⛅ Cloudy",
    "🌧️ Dážď / Sychravo": "🌧️ Rainy / Overcast",
    "❄️ Sneženie": "❄️ Snowfall",
    "End-to-End Predictive Pricing & Behavioral BI • SR & ČR Localization, Open-Meteo & Chart.js":
      "End-to-End Predictive Pricing & Behavioral BI • SK & CZ Localization, Open-Meteo & Chart.js"
  };

  // Dynamické preklady viet v analytickom sumári
  const REGEX_RULES = [
    [/Číslo\s*<strong>(\d+)\s*videní<\/strong>\s*\((\d+)\s*%\s*benchmarku kategórie\s*<em>([^<]+)<\/em>\)\s*predstavuje úvodnú fázu\.\s*Skóre kvality inzerátu je\s*<strong>(\d+\/100)<\/strong>\s*\((\d+)\s*fotiek\),\s*čo dáva pravdepodobnosť predaja\s*<strong>(\d+)\s*%<\/strong>\./g,
     "Current count of <strong>$1 views</strong> ($2% of <em>$3</em> category benchmark) represents the initial audience-building phase. Listing quality score is <strong>$4</strong> ($5 photos), yielding a <strong>$6%</strong> sale probability."],
    [/Dosiahnutých\s*<strong>(\d+)\s*videní<\/strong>\s*\((\d+)\s*%\s*benchmarku\)\s*pri tempe\s*<strong>([\d.]+)\s*videní\/deň<\/strong>\s*značí aktívny záujem v regióne\s*<strong>([^<]+)<\/strong>\.\s*Štatistická šanca na uzavretie predaja je\s*<strong>(\d+)\s*%<\/strong>\./g,
     "Reaching <strong>$1 views</strong> ($2% of benchmark) at a velocity of <strong>$3 views/day</strong> indicates active buyer interest in <strong>$4</strong>. Statistical sale probability is <strong>$5%</strong>."],
    [/Tempo\s*([\d.]+)\s*videní\/deň je optimálne([^.]*)\.\s*Najbližšie zlaté okno:\s*<strong>([^<]+)<\/strong>\./g,
     "Velocity of $1 views/day is optimal$2. Next golden window: <strong>$3</strong>."],
    [/\(aktuálne prebieha silné povýplatné obdobie 10\.–18\. v mesiaci!\)/g,
     " (active post-payday window: 10th–18th of the month!)"],
    [/1\. Zverejniť v nedeľu podvečer \(ideálne 10\.–18\. deň v mesiaci po výplatách\)\. 2\. Zdôrazniť čistotu \(vypratie\), rozmery vaničky a doplnky \(Isofix, fusak\)\. 3\. Pri 120\+ videniach bez obhliadky upraviť cenu o 15–20 € alebo obnoviť na vrch\./g,
     "1. Publish on Sunday evening (ideally 10th–18th of month after payday). 2. Highlight cleanliness, bassinet dimensions, and accessories (Isofix, footmuff). 3. At 120+ views without a viewing, reduce price by €15–20 or republish to top."],
    [/1\. Uviesť normu \(i-Size \/ ECE R129\), hmotnostný\/výškový rozsah a testy ADAC hneď v úvode\. 2\. Obnovovať pred víkendmi a sviatkami \(cestovanie\)\. 3\. Držať cenu v zóne 50–60 % nového kusu\./g,
     "1. State safety standard (i-Size / ECE R129), height/weight range, and ADAC ratings upfront. 2. Republish before weekends and holidays (family travel). 3. Keep price within 50–60% of retail value."]
  ];

  let originalHTML = null;

  function applyEnglish() {
    if (!originalHTML) {
      originalHTML = document.querySelector(".container").innerHTML;
    }
    const topbar = document.querySelector(".topbar-inner");
    const container = document.querySelector(".container");
    const footer = document.querySelector("footer");

    [topbar, container, footer].forEach((el) => {
      if (!el) return;
      let html = el.innerHTML;
      REGEX_RULES.forEach(([regex, replacement]) => {
        html = html.replace(regex, replacement);
      });
      Object.entries(DICT).forEach(([sk, en]) => {
        html = html.split(sk).join(en);
      });
      el.innerHTML = html;
    });
  }

  function applySlovak() {
    if (originalHTML) {
      location.reload();
    }
  }

  function initSwitcher() {
    const topbarInner = document.querySelector(".topbar-inner");
    if (!topbarInner || document.getElementById("lang-switcher-box")) return;

    const savedLang = localStorage.getItem("bi_dashboard_lang") || "sk";

    const box = document.createElement("div");
    box.id = "lang-switcher-box";
    box.style.cssText = "display:flex;gap:6px;align-items:center;";
    box.innerHTML = `
      <button id="btn-lang-sk" style="cursor:pointer;padding:5px 10px;border-radius:6px;border:1px solid #334155;font-size:12px;font-weight:600;background:${savedLang === "sk" ? "#2563eb" : "#1e293b"};color:#fff;">🇸🇰 SK</button>
      <button id="btn-lang-en" style="cursor:pointer;padding:5px 10px;border-radius:6px;border:1px solid #334155;font-size:12px;font-weight:600;background:${savedLang === "en" ? "#2563eb" : "#1e293b"};color:#fff;">🇬🇧 EN</button>
    `;
    topbarInner.appendChild(box);

    document.getElementById("btn-lang-sk").addEventListener("click", () => {
      localStorage.setItem("bi_dashboard_lang", "sk");
      applySlovak();
    });

    document.getElementById("btn-lang-en").addEventListener("click", () => {
      localStorage.setItem("bi_dashboard_lang", "en");
      if (document.documentElement.lang !== "en") {
        document.documentElement.lang = "en";
        applyEnglish();
        document.getElementById("btn-lang-en").style.background = "#2563eb";
        document.getElementById("btn-lang-sk").style.background = "#1e293b";
      }
    });

    if (savedLang === "en") {
      document.documentElement.lang = "en";
      applyEnglish();
      document.getElementById("btn-lang-en").style.background = "#2563eb";
      document.getElementById("btn-lang-sk").style.background = "#1e293b";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSwitcher);
  } else {
    initSwitcher();
  }
})();
