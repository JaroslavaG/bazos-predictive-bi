import json
import os
import re
import csv
import smtplib
import urllib.parse
import urllib.request
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

CONFIG_FILE = "inzeraty.json"
HISTORY_FILE = "historia_videni.csv"
DASHBOARD_FILE = "index.html"

SK_DAYS = ["Pondelok", "Utorok", "Streda", "Štvrtok", "Piatok", "Sobota", "Nedeľa"]

FIXED_HOLIDAYS_SK = {
    "01-01": "Deň vzniku SR", "01-06": "Zjavenie Pána", "05-01": "Sviatok práce",
    "05-08": "Deň víťazstva", "07-05": "Sv. Cyril a Metod", "08-29": "Výročie SNP",
    "09-01": "Deň Ústavy SR", "09-15": "Sedembolestná Panna Mária",
    "11-01": "Sviatok všetkých svätých", "11-17": "Deň boja za slobodu a demokraciu",
    "12-24": "Štedrý deň", "12-25": "1. sviatok vianočný", "12-26": "2. sviatok vianočný"
}

FIXED_HOLIDAYS_CZ = {
    "01-01": "Nový rok / Obnovení samostatného českého státu", "05-01": "Svátek práce",
    "05-08": "Den vítězství", "07-05": "Den slovanských věrozvěstů Cyrila a Metoděje",
    "07-06": "Den upálení mistra Jana Husa", "09-28": "Den české státnosti",
    "10-28": "Den vzniku samostatného československého státu",
    "11-17": "Den boje za svobodu a demokracii",
    "12-24": "Štědrý den", "12-25": "1. svátek vánoční", "12-26": "2. svátek vánoční"
}

# Realistickejšie, konzervatívne bázy pravdepodobnosti predaja do 14 dní
CATEGORY_PROFILES = {
    "kocik": {
        "label": "Kočíky & Príslušenstvo",
        "peak_window": "Nedeľa 17:30 – 21:00 a Streda 19:30 – 21:30",
        "best_step": "1. Zverejniť v nedeľu podvečer (ideálne 10.–18. deň v mesiaci po výplatách). 2. Zdôrazniť čistotu (vypratie), rozmery vaničky a doplnky (Isofix, fusak). 3. Pri 120+ videniach bez obhliadky upraviť cenu o 15–20 € alebo obnoviť na vrch.",
        "base_prob": 42,
        "default_benchmark": 150
    },
    "autosedacka": {
        "label": "Autosedačky & Bezpečnosť",
        "peak_window": "Pracovné dni 20:00 – 22:00 a Nedeľa večer",
        "best_step": "1. Uviesť normu (i-Size / ECE R129), hmotnostný/výškový rozsah a testy ADAC hneď v úvode. 2. Obnovovať pred víkendmi a sviatkami (cestovanie). 3. Držať cenu v zóne 50–60 % nového kusu.",
        "base_prob": 48,
        "default_benchmark": 90
    },
    "oblecenie": {
        "label": "Detské oblečenie & Obuv",
        "peak_window": "Piatok večer a Nedeľa 18:00 – 21:30",
        "best_step": "1. Zlučovať do veľkostných balíkov (vyššia hodnota pre kupujúceho). 2. Načasovať obnovenie presne pri ochladení alebo zmene ročného obdobia.",
        "base_prob": 40,
        "default_benchmark": 60
    },
    "sport_hracky": {
        "label": "Hračky, Bicykle & Šport",
        "peak_window": "Štvrtok – Nedeľa večer",
        "best_step": "1. Šport a bicykle obnovovať vo štvrtok večer pred slnečným víkendom. 2. Hračky cieliť na daždivé dni a obdobie pred sviatkami.",
        "base_prob": 45,
        "default_benchmark": 70
    }
}


def get_easter_sunday(year):
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def get_calendar_context(dt, country="SK"):
    weekday_idx = dt.weekday()
    day_name = SK_DAYS[weekday_idx]
    mm_dd = dt.strftime("%m-%d")
    today_date = dt.date()

    easter = get_easter_sunday(dt.year)
    good_friday = easter - timedelta(days=2)
    easter_monday = easter + timedelta(days=1)

    holidays_map = FIXED_HOLIDAYS_CZ if country == "CZ" else FIXED_HOLIDAYS_SK
    holiday_name = holidays_map.get(mm_dd)
    if today_date == good_friday:
        holiday_name = "Veľký piatok" if country == "SK" else "Velký pátek"
    elif today_date == easter_monday:
        holiday_name = "Veľkonočný pondelok" if country == "SK" else "Velikonoční pondělí"

    is_holiday = holiday_name is not None
    is_weekend = weekday_idx >= 5
    is_payday_window = 10 <= dt.day <= 18

    if is_holiday:
        day_type = f"Sviatok ({country}): {holiday_name}"
    elif is_weekend:
        day_type = f"Víkend ({country})"
    else:
        day_type = f"Pracovný deň ({country})"

    return {
        "weekday_idx": weekday_idx,
        "day_name": day_name,
        "day_type": day_type,
        "is_off_day": is_weekend or is_holiday,
        "is_holiday": is_holiday,
        "holiday_name": holiday_name,
        "is_payday_window": is_payday_window
    }


def extract_location_from_bazos(soup, text, url):
    """Presná extrakcia PSČ (XXX XX), mesta a GPS priamo zo štruktúry Bazoša."""
    country = "CZ" if ".cz" in url.lower() else "SK"
    lat, lon = None, None
    psc, city = None, None

    loc_link = soup.find('a', title=re.compile(r'Približná lokalita|Přibližná lokalita', re.I))
    if loc_link:
        psc_candidate = loc_link.get_text(strip=True)
        if re.match(r'^\d{3}\s\d{2}$', psc_candidate):
            psc = psc_candidate
            next_a = loc_link.find_next_sibling('a')
            if next_a:
                city = next_a.get_text(strip=True)

        if 'google.com/maps/place/' in loc_link.get('href', ''):
            m_coords = re.search(r'place/([-0-9.]+),([-0-9.]+)', loc_link['href'])
            if m_coords:
                lat, lon = float(m_coords.group(1)), float(m_coords.group(2))

    if not psc or not city:
        m_psc = re.search(
            r'(?<!\d)(\d{3}\s\d{2})\s+([A-ZÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽĚŘŮ][a-záčďéíĺľňóôŕšťúýžěřůA-ZÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽĚŘŮ\s-]{2,25})',
            text
        )
        if m_psc:
            psc = m_psc.group(1).strip()
            city = m_psc.group(2).strip().split('\n')[0].strip()

    if not psc or not city:
        psc, city = ("110 00", "Praha") if country == "CZ" else ("040 23", "Košice")

    if lat is None or lon is None:
        for a in soup.find_all('a', href=True):
            if 'google.com/maps/place/' in a['href']:
                m_coords = re.search(r'place/([-0-9.]+),([-0-9.]+)', a['href'])
                if m_coords:
                    lat, lon = float(m_coords.group(1)), float(m_coords.group(2))
                    break

    if lat is None or lon is None:
        try:
            query = urllib.parse.quote(f"{psc} {city}")
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=1&language=sk&format=json"
            with urllib.request.urlopen(geo_url, timeout=8) as resp:
                geo_data = json.loads(resp.read().decode("utf-8"))
            if geo_data.get("results"):
                lat = geo_data["results"][0]["latitude"]
                lon = geo_data["results"][0]["longitude"]
        except Exception:
            lat, lon = (50.0755, 14.4378) if country == "CZ" else (48.7167, 21.2107)

    return {"country": country, "psc": psc, "city": city, "lat": lat, "lon": lon}


def get_weather_for_location(loc):
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={loc['lat']}&longitude={loc['lon']}"
        "&daily=weather_code,temperature_2m_max,precipitation_sum&timezone=Europe%2FBratislava&forecast_days=1"
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            daily = json.loads(resp.read().decode("utf-8"))["daily"]
        code = daily["weather_code"][0]
        temp_max = daily["temperature_2m_max"][0]
        precip = daily["precipitation_sum"][0]

        if code in [0, 1]:
            desc, is_bad = "☀️ Slnečno", False
        elif code in [2, 3, 45, 48]:
            desc, is_bad = "⛅ Oblačno", False
        elif code in [71, 73, 75, 77, 85, 86]:
            desc, is_bad = "❄️ Sneženie", True
        else:
            desc, is_bad = "🌧️ Dážď / Sychravo", True

        return {
            "location_label": f"{loc['psc']} {loc['city']} ({loc['country']})",
            "summary": f"{desc} ({temp_max}°C, {precip} mm)",
            "is_bad_weather": is_bad
        }
    except Exception:
        return {"location_label": f"{loc['psc']} {loc['city']}", "summary": "Neznáme", "is_bad_weather": False}


def parse_bazos_html(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()

    if "Inzerát bol vymazaný" in text or "Inzerát neexistuje" in text:
        return {"status": "inactive"}

    match_views = re.search(r'Videlo:\s*(\d+)\s*ľudí', text)
    views = int(match_views.group(1)) if match_views else 0
    price_mode = "V texte" if "V texte" in text else "Číselná"

    img_srcs = set(
        img['src'] for img in soup.find_all('img', src=True)
        if '/img/' in img['src'] and not img['src'].endswith('next.svg')
    )
    img_count = len(img_srcs)
    has_dimensions = bool(re.search(r'\b\d+\s*[×x]\s*\d+|\b\d+\s*cm\b|\b\d+[.,]?\d*\s*kg\b', text))
    quality_score = min(100, (min(img_count, 8) * 8) + (20 if has_dimensions else 0) + (16 if len(text) > 500 else 8))

    location = extract_location_from_bazos(soup, text, url)

    return {
        "status": "active",
        "views": views,
        "price_mode": price_mode,
        "quality_score": quality_score,
        "img_count": img_count,
        "has_dimensions": has_dimensions,
        "location": location
    }


def get_ad_details(url):
    req = urllib.request.Request(
        url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        return parse_bazos_html(html, url)
    except Exception as e:
        print(f"Chyba pri načítaní {url}: {e}")
        return None


def analyze_price_elasticity(ad_rows, current_price):
    if len(ad_rows) < 2:
        return None
    prices = [float(r['cena']) for r in ad_rows if r.get('cena')]
    if len(set(prices)) <= 1:
        return None

    change_idx = None
    for idx in range(len(ad_rows) - 1, 0, -1):
        if float(ad_rows[idx]['cena']) != float(ad_rows[idx - 1]['cena']):
            change_idx = idx
            break

    if change_idx is None:
        return None

    old_price = float(ad_rows[change_idx - 1]['cena'])
    new_price = float(ad_rows[change_idx]['cena'])
    before_gains = [int(r['narast']) for r in ad_rows[:change_idx]]
    after_gains = [int(r['narast']) for r in ad_rows[change_idx:]]

    avg_before = round(sum(before_gains) / len(before_gains), 1) if before_gains else 0
    avg_after = round(sum(after_gains) / len(after_gains), 1) if after_gains else 0
    lift_pct = round(((avg_after - avg_before) / avg_before) * 100) if avg_before > 0 else 0

    return {
        "old_price": int(old_price),
        "new_price": int(new_price),
        "avg_before": avg_before,
        "avg_after": avg_after,
        "lift_pct": lift_pct
    }


def calculate_sale_probability(ad, views, daily_gain, days_active, velocity, quality_score, cal, weather):
    """Konzervatívny, realistický model pravdepodobnosti predaja do 14 dní (%)."""
    cat_key = ad.get("kategoria", "kocik")
    profile = CATEGORY_PROFILES.get(cat_key, CATEGORY_PROFILES["kocik"])
    benchmark = ad.get("benchmark_videni", profile["default_benchmark"])

    prob = profile["base_prob"]

    if quality_score >= 85:
        prob += 5
    elif quality_score < 50:
        prob -= 10

    if days_active == 1:
        if views >= 15:
            prob += 6
        elif views < 5:
            prob -= 6
    else:
        if velocity >= 10:
            prob += 14
        elif velocity >= 5:
            prob += 7
        elif velocity < 2.5:
            prob -= 15

    if cal["is_payday_window"]:
        prob += 4
    if weather["is_bad_weather"]:
        prob += 3
    if cal["weekday_idx"] == 6:
        prob += 4

    if views > benchmark * 1.1:
        prob -= 18
    if days_active > 14:
        prob -= 15

    return max(10, min(88, round(prob)))


def build_automated_summary(ad, details, daily_gain, days_active, velocity, cal, weather, elasticity=None):
    cat_key = ad.get("kategoria", "kocik")
    profile = CATEGORY_PROFILES.get(cat_key, CATEGORY_PROFILES["kocik"])
    benchmark = ad.get("benchmark_videni", profile["default_benchmark"])
    views = details["views"]
    q_score = details["quality_score"]

    sale_prob = calculate_sale_probability(ad, views, daily_gain, days_active, velocity, q_score, cal, weather)
    pct_bench = round((views / benchmark) * 100) if benchmark > 0 else 0

    elasticity_note = ""
    if elasticity:
        sign = "+" if elasticity["lift_pct"] >= 0 else ""
        elasticity_note = (
            f" Po úprave ceny ({elasticity['old_price']} € &rarr; {elasticity['new_price']} €) sa denný záujem zmenil o "
            f"<strong>{sign}{elasticity['lift_pct']} %</strong> ({elasticity['avg_before']} &rarr; {elasticity['avg_after']} videní/deň)."
        )

    if views < 35:
        meaning = (
            f"Číslo <strong>{views} videní</strong> ({pct_bench} % benchmarku kategórie <em>{profile['label']}</em>) "
            f"predstavuje úvodnú fázu. Skóre kvality inzerátu je <strong>{q_score}/100</strong> ({details['img_count']} fotiek), "
            f"čo dáva realistickú pravdepodobnosť predaja do 14 dní <strong>{sale_prob} %</strong>.{elasticity_note}"
        )
    elif views < benchmark:
        meaning = (
            f"Dosiahnutých <strong>{views} videní</strong> ({pct_bench} % benchmarku) pri tempe <strong>{velocity} videní/deň</strong> "
            f"značí aktívny záujem v regióne <strong>{weather['location_label']}</strong>. Štatistická šanca na uzavretie predaja je <strong>{sale_prob} %</strong>.{elasticity_note}"
        )
    else:
        meaning = (
            f"Prekročenie <strong>{views} videní</strong> ({pct_bench} % benchmarku) bez predaja značí vyčerpanie publika pri cene <strong>{ad['aktualna_cena']} €</strong>. "
            f"Pravdepodobnosť predaja bez zásahu je <strong>{sale_prob} %</strong>.{elasticity_note}"
        )

    payday_note = " (aktuálne prebieha silné povýplatné obdobie 10.–18. v mesiaci!)" if cal["is_payday_window"] else ""

    if days_active >= 2 and daily_gain < ad["min_denny_narast"]:
        if cal["is_off_day"] and not weather["is_bad_weather"]:
            status = ("info", f"☀️ Voľný deň ({sale_prob}% šanca)")
            rec = (
                f"Nižší prírastok (+{daily_gain}) súvisí s voľným dňom ({cal['day_type']}) a pekným počasím ({weather['summary']}). "
                f"S úpravou ceny počkaj na špičku kategórie: <strong>{profile['peak_window']}</strong>."
            )
        else:
            status = ("danger", f"⚠️ Útlm ({sale_prob}% šanca)")
            rec = (
                f"Prírastok klesol na +{daily_gain} videní ({cal['day_type']}, {weather['summary']}). "
                f"Odporúčam inzerát vymazať, nahodiť nanovo v čase <strong>{profile['peak_window']}</strong> a zvážiť cenu <strong>{ad['cielova_cena']} €</strong>{payday_note}."
            )
    elif views >= benchmark and ad["aktualna_cena"] > ad["cielova_cena"]:
        status = ("warn", f"💡 Cenový zlom ({sale_prob}% šanca)")
        rec = (
            f"Inzerát videlo už {views} ľudí. Zníž cenu v texte z <strong>{ad['aktualna_cena']} €</strong> na <strong>{ad['cielova_cena']} €</strong> "
            f"alebo prepni režim 'V texte' na konkrétnu sumu{payday_note}."
        )
    elif days_active >= 14:
        status = ("warn", f"🔄 Obnoviť ({sale_prob}% šanca)")
        rec = f"Inzerát má 14+ dní. Zmaž ho a pridaj ako nový v čase: <strong>{profile['peak_window']}</strong>."
    else:
        status = ("ok", f"📈 Dobrý trend ({sale_prob}% šanca)")
        rec = f"Tempo {velocity} videní/deň je optimálne{payday_note}. Najbližšie zlaté okno: <strong>{profile['peak_window']}</strong>."

    return {
        "profile": profile,
        "benchmark": benchmark,
        "pct_benchmark": min(pct_bench, 100),
        "sale_prob": sale_prob,
        "meaning": meaning,
        "rec": rec,
        "status_type": status[0],
        "status_label": status[1]
    }


def load_all_rows(filepath=HISTORY_FILE):
    if not os.path.exists(filepath):
        return []
    with open(filepath, mode='r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_all_rows(rows, filepath=HISTORY_FILE):
    fieldnames = [
        'datum', 'krajina', 'lokalita', 'den', 'typ_dna', 'pocasie',
        'id', 'kategoria', 'nazov', 'videnia', 'narast', 'cena', 'sanca_predaja_pct'
    ]
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            for col in fieldnames:
                r.setdefault(col, '')
            writer.writerow(r)


def send_email(subject, body_html):
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    recipient = os.environ.get("EMAIL_TO", sender)
    if not sender or not password:
        return

    msg = MIMEMultipart()
    msg['From'] = f"Tvorca inzerátov BI <{sender}>"
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body_html, 'html', 'utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.send_message(msg)


def generate_html_dashboard(ads, rows, summaries, ad_contexts, filepath=DASHBOARD_FILE):
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    dates = sorted(list(set(r['datum'] for r in rows)))
    palette = ['#2563eb', '#0d9488', '#d97706', '#7c3aed', '#db2777']
    
    cumulative_datasets, daily_datasets = [], []
    cards_html, table_rows_html = "", ""
    total_asking = sum(ad['aktualna_cena'] for ad in ads)
    total_target = sum(ad['cielova_cena'] for ad in ads)
    total_views_all, total_daily_gain, prob_list = 0, 0, []

    for idx, ad in enumerate(ads):
        ad_id = ad['id']
        if ad_id not in summaries:
            continue
        color = palette[idx % len(palette)]
        ad_rows = sorted([r for r in rows if r['id'] == ad_id], key=lambda x: x['datum'])
        s = summaries[ad_id]
        ctx = ad_contexts[ad_id]
        
        latest_views = int(ad_rows[-1]['videnia']) if ad_rows else 0
        latest_gain = int(ad_rows[-1]['narast']) if ad_rows else 0
        days_active = max(len(ad_rows), 1)
        velocity = round(latest_views / days_active, 1)

        total_views_all += latest_views
        total_daily_gain += latest_gain
        prob_list.append(s["sale_prob"])

        cards_html += f"""
        <div class="ad-card" style="border-top: 4px solid {color};">
            <div class="ad-header">
                <div>
                    <span class="ad-id">{s['profile']['label']} &bull; 📍 {ctx['weather']['location_label']} &bull; ID: {ad_id}</span>
                    <h3>{ad['nazov']}</h3>
                </div>
                <span class="badge badge-{s['status_type']}">{s['status_label']}</span>
            </div>

            <div class="progress-wrap">
                <div class="progress-labels">
                    <span>Pravdepodobnosť predaja (Predikčný model)</span>
                    <strong style="color:{color}">{s['sale_prob']} %</strong>
                </div>
                <div class="progress-bar"><div class="progress-fill" style="width:{s['sale_prob']}%;background:{color};"></div></div>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-box">
                    <span class="m-label">Celkové videnia</span>
                    <span class="m-val">{latest_views} <small>/ {s['benchmark']}</small></span>
                    <span class="m-sub">Dnes: <strong style="color:{color}">+{latest_gain}</strong> &bull; {ctx['weather']['summary']}</span>
                </div>
                <div class="metric-box">
                    <span class="m-label">Rýchlosť & Kalendár</span>
                    <span class="m-val">{velocity} <small>/deň</small></span>
                    <span class="m-sub">{ctx['cal']['day_type']}</span>
                </div>
                <div class="metric-box">
                    <span class="m-label">Ponuková cena</span>
                    <span class="m-val">{ad['aktualna_cena']} €</span>
                    <span class="m-sub">Cieľ: {ad['cielova_cena']} € (vankúš {ad['aktualna_cena'] - ad['cielova_cena']} €)</span>
                </div>
                <div class="metric-box">
                    <span class="m-label">Kvalita inzerátu</span>
                    <span class="m-val">{ctx['details']['quality_score']}%</span>
                    <span class="m-sub">{ctx['details']['img_count']} fotiek &bull; Cena: {ctx['details']['price_mode']}</span>
                </div>
            </div>

            <div class="summary-box">
                <p><strong>📊 Čo hovorí toto číslo:</strong> {s['meaning']}</p>
                <p><strong>🎯 Odporúčaný krok:</strong> {s['rec']}</p>
                <p class="season-note"><strong>📘 Štatistický návod kategórie:</strong> {s['profile']['best_step']}</p>
            </div>

            <div class="ad-footer">
                <span>Sledované: <strong>{days_active} d.</strong> &bull; Špička: <strong>{s['profile']['peak_window'].split(' a ')[0]}</strong></span>
                <a href="{ad['url']}" target="_blank" class="btn-link">Otvoriť na Bazoši →</a>
            </div>
        </div>
        """

        for r in reversed(ad_rows[-4:]):
            table_rows_html += f"""
            <tr>
                <td>{r['datum']}</td>
                <td>{r.get('lokalita', '')}</td>
                <td>{r.get('den', '')} <small style="color:#64748b">({r.get('typ_dna', '')})</small></td>
                <td>{r.get('pocasie', '')}</td>
                <td><strong>{ad['nazov']}</strong></td>
                <td>{r['videnia']} <span class="pill-gain">+{r['narast']}</span></td>
                <td><strong>{r.get('sanca_predaja_pct', '')}%</strong></td>
            </tr>
            """

        date_map_views = {r['datum']: int(r['videnia']) for r in ad_rows}
        date_map_gains = {r['datum']: int(r['narast']) for r in ad_rows}

        cumulative_datasets.append({
            "label": ad['nazov'], "data": [date_map_views.get(d, None) for d in dates],
            "borderColor": color, "backgroundColor": color + "20", "borderWidth": 2.5, "tension": 0.35, "fill": True
        })
        daily_datasets.append({
            "label": ad['nazov'], "data": [date_map_gains.get(d, 0) for d in dates],
            "backgroundColor": color, "borderRadius": 4
        })

    avg_prob = round(sum(prob_list) / len(prob_list)) if prob_list else 0

    html_content = f"""<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bazoš Predictive BI | SR & ČR Sviatky, PSČ Počasie & Predikcia Predaja</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%232563eb'/%3E%3Cpath d='M16 44l12-14 9 8 13-18' fill='none' stroke='%23ffffff' stroke-width='6' stroke-linecap='round' stroke-linejoin='round'/%3E%3Ccircle cx='50' cy='20' r='4.5' fill='%2338bdf8'/%3E%3C/svg%3E">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{ --bg: #f8fafc; --surface: #ffffff; --navy: #0f172a; --slate: #475569; --muted: #94a3b8; --border: #e2e8f0; --primary: #2563eb; }}
        * {{ box-sizing: border-box; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--navy); margin: 0; line-height: 1.5; }}
        .topbar {{ background: var(--navy); color: #fff; padding: 18px 24px; }}
        .topbar-inner {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
        .brand {{ display: flex; align-items: center; gap: 10px; }}
        .brand h1 {{ margin: 0; font-size: 18px; font-weight: 700; }}
        .tag-pro {{ background: #2563eb; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; text-transform: uppercase; }}
        .context-pill {{ background: #1e293b; border: 1px solid #334155; padding: 6px 12px; border-radius: 8px; font-size: 12px; color: #e2e8f0; }}
        .container {{ max-width: 1200px; margin: 24px auto; padding: 0 20px; }}
        .kpi-strip {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .kpi-card {{ background: var(--surface); padding: 18px 20px; border-radius: 10px; border: 1px solid var(--border); }}
        .kpi-title {{ font-size: 11px; font-weight: 600; color: var(--slate); text-transform: uppercase; }}
        .kpi-value {{ font-size: 24px; font-weight: 700; color: var(--navy); margin: 6px 0 2px 0; }}
        .kpi-desc {{ font-size: 12px; color: var(--muted); }}
        .ads-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-bottom: 24px; }}
        .ad-card {{ background: var(--surface); border-radius: 12px; padding: 22px; border: 1px solid var(--border); display: flex; flex-direction: column; justify-content: space-between; }}
        .ad-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 14px; }}
        .ad-id {{ font-size: 11px; color: var(--muted); font-weight: 600; text-transform: uppercase; }}
        .ad-header h3 {{ margin: 4px 0 0 0; font-size: 16px; font-weight: 700; }}
        .badge {{ font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 99px; white-space: nowrap; }}
        .badge-ok {{ background: #dcfce7; color: #166534; }}
        .badge-info {{ background: #e0f2fe; color: #075985; }}
        .badge-warn {{ background: #fef3c7; color: #92400e; }}
        .badge-danger {{ background: #fee2e2; color: #991b1b; }}
        .progress-wrap {{ margin-bottom: 16px; }}
        .progress-labels {{ display: flex; justify-content: space-between; font-size: 12px; color: var(--slate); margin-bottom: 5px; }}
        .progress-bar {{ height: 8px; background: #e2e8f0; border-radius: 99px; overflow: hidden; }}
        .progress-fill {{ height: 100%; border-radius: 99px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 16px; }}
        .metric-box {{ background: #f8fafc; padding: 10px 12px; border-radius: 8px; border: 1px solid var(--border); }}
        .m-label {{ display: block; font-size: 11px; color: var(--slate); }}
        .m-val {{ display: block; font-size: 19px; font-weight: 700; color: var(--navy); margin: 2px 0; }}
        .m-val small {{ font-size: 12px; font-weight: 500; color: var(--slate); }}
        .m-sub {{ display: block; font-size: 11px; color: var(--muted); }}
        .summary-box {{ background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid var(--primary); padding: 12px 14px; border-radius: 8px; font-size: 12.5px; color: #1e293b; margin-bottom: 16px; }}
        .summary-box p {{ margin: 0 0 8px 0; }}
        .summary-box p:last-child {{ margin-bottom: 0; }}
        .season-note {{ color: var(--slate); font-size: 11.5px; border-top: 1px dashed #cbd5e1; padding-top: 8px; }}
        .ad-footer {{ display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid var(--border); font-size: 12px; color: var(--slate); }}
        .btn-link {{ color: var(--primary); font-weight: 600; text-decoration: none; }}
        .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(460px, 1fr)); gap: 20px; margin-bottom: 24px; }}
        .panel {{ background: var(--surface); padding: 22px; border-radius: 12px; border: 1px solid var(--border); margin-bottom: 20px; }}
        .panel h2 {{ margin: 0 0 16px 0; font-size: 15px; font-weight: 700; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
        th {{ text-align: left; padding: 10px 10px; background: #f8fafc; color: var(--slate); font-weight: 600; border-bottom: 1px solid var(--border); }}
        td {{ padding: 10px 10px; border-bottom: 1px solid var(--border); }}
        .pill-gain {{ background: #eff6ff; color: #1d4ed8; padding: 2px 7px; border-radius: 99px; font-weight: 600; font-size: 11.5px; }}
        footer {{ text-align: center; padding: 20px; font-size: 12px; color: var(--muted); }}
        @media (max-width: 600px) {{ .ads-grid, .charts-grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="topbar">
        <div class="topbar-inner">
            <div class="brand">
                <h1>Bazoš Predictive Sales & Pricing BI</h1>
                <span class="tag-pro">SR & ČR Engine</span>
            </div>
            <div class="context-pill">
                🌍 Auto-PSČ Počasie &bull; 📅 SR/ČR Sviatky & Payday &bull; 🕒 Sync: {now_str}
            </div>
        </div>
    </div>

    <div class="container">
        <div class="kpi-strip">
            <div class="kpi-card">
                <div class="kpi-title">Ponuková hodnota</div>
                <div class="kpi-value">{total_asking} €</div>
                <div class="kpi-desc">Cieľová hodnota: {total_target} €</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Celkový organický zásah</div>
                <div class="kpi-value">{total_views_all}</div>
                <div class="kpi-desc">Dnešný prírastok: +{total_daily_gain} videní</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Priemerná šanca predaja</div>
                <div class="kpi-value">{avg_prob} %</div>
                <div class="kpi-desc">Predikčný model do 14 dní</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Geolokácia & Kalendár</div>
                <div class="kpi-value" style="font-size:16px;margin-top:10px;">Dynamic PSČ</div>
                <div class="kpi-desc">SR + ČR sviatky & výplatné okná</div>
            </div>
        </div>

        <div class="ads-grid">{cards_html}</div>

        <div class="charts-grid">
            <div class="panel" style="margin-bottom:0;">
                <h2>📈 Kumulatívna krivka záujmu (Celkové videnia)</h2>
                <canvas id="cumulativeChart" height="140"></canvas>
            </div>
            <div class="panel" style="margin-bottom:0;">
                <h2>📊 Denná dynamika prírastkov (Videnia / deň)</h2>
                <canvas id="dailyChart" height="140"></canvas>
            </div>
        </div>

        <div class="panel">
            <h2>📘 Štatistický manuál: Kedy a ako predať konkrétny typ produktu</h2>
            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Kategória produktu</th>
                            <th>Zlaté časové okno</th>
                            <th>Šanca predaja do 14 dní</th>
                            <th>Odporúčaný postup krok za krokom</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Kočíky (3v1, športové)</strong></td>
                            <td>Nedeľa 17:30–21:00, Streda večer</td>
                            <td><strong>75 – 85 %</strong></td>
                            <td>Zverejniť po výplatách (10.–18. v mesiaci), uviesť rozmery vaničky a rámu, pri 120+ videniach obnoviť.</td>
                        </tr>
                        <tr>
                            <td><strong>Autosedačky (i-Size)</strong></td>
                            <td>Pracovné dni 20:00–22:00, Nedeľa</td>
                            <td><strong>80 – 90 %</strong></td>
                            <td>Uviesť normu ECE R129 a testy ADAC, obnovovať pred sviatkami a prázdninami.</td>
                        </tr>
                        <tr>
                            <td><strong>Detské oblečenie & Obuv</strong></td>
                            <td>Piatok večer, Nedeľa podvečer</td>
                            <td><strong>70 – 85 %</strong></td>
                            <td>Spájať do balíkov podľa veľkosti, obnovovať pri náhlom ochladení alebo daždi.</td>
                        </tr>
                        <tr>
                            <td><strong>Bicykle, Odrážadlá & Hračky</strong></td>
                            <td>Štvrtok – Nedeľa večer</td>
                            <td><strong>85 – 95 %</strong></td>
                            <td>Športové veci nahodiť vo štvrtok pred slnečným víkendom; hračky v daždivých dňoch.</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="panel">
            <h2>🗂️ Auditný denník meraní (PSČ Lokalita + Počasie + Predikcia)</h2>
            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Dátum</th>
                            <th>PSČ / Mesto</th>
                            <th>Kalendár (SR/ČR)</th>
                            <th>Počasie</th>
                            <th>Inzerát</th>
                            <th>Videnia</th>
                            <th>Šanca</th>
                        </tr>
                    </thead>
                    <tbody>{table_rows_html}</tbody>
                </table>
            </div>
        </div>
    </div>

    <footer>
        End-to-End Predictive Pricing & Behavioral BI &bull; SR & ČR Localization, Open-Meteo & Chart.js
    </footer>

    <script>
        new Chart(document.getElementById('cumulativeChart'), {{
            type: 'line', data: {{ labels: {json.dumps(dates)}, datasets: {json.dumps(cumulative_datasets)} }},
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }}, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});
        new Chart(document.getElementById('dailyChart'), {{
            type: 'bar', data: {{ labels: {json.dumps(dates)}, datasets: {json.dumps(daily_datasets)} }},
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }}, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});
    </script>
    <script src="i18n.js"></script>
</body>
</html>"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        ads = json.load(f)

    now_dt = datetime.now()
    today_str = now_dt.strftime("%Y-%m-%d")

    rows = load_all_rows()
    summaries, ad_contexts, alerts = {}, {}, []

    for ad in ads:
        ad_id = ad['id']
        details = get_ad_details(ad['url'])
        if not details or details["status"] != "active":
            continue

        loc = details["location"]
        cal = get_calendar_context(now_dt, country=loc["country"])
        weather = get_weather_for_location(loc)

        views = details["views"]
        past_rows = [r for r in rows if r['id'] == ad_id and r['datum'] != today_str]
        prev_views = int(past_rows[-1]['videnia']) if past_rows else 0
        daily_gain = views - prev_views if past_rows else views

        ad_rows_temp = past_rows + [{
            'datum': today_str, 'videnia': str(views),
            'narast': str(daily_gain), 'cena': str(ad['aktualna_cena'])
        }]
        days_active = max(len(ad_rows_temp), 1)
        velocity = round(views / days_active, 1)
        elasticity = analyze_price_elasticity(ad_rows_temp, ad['aktualna_cena'])

        summary = build_automated_summary(ad, details, daily_gain, days_active, velocity, cal, weather, elasticity)
        summaries[ad_id] = summary
        ad_contexts[ad_id] = {"details": details, "cal": cal, "weather": weather}

        rows = [r for r in rows if not (r['id'] == ad_id and r['datum'] == today_str)]
        rows.append({
            'datum': today_str, 'krajina': loc['country'], 'lokalita': weather['location_label'],
            'den': cal['day_name'], 'typ_dna': cal['day_type'], 'pocasie': weather['summary'],
            'id': ad_id, 'kategoria': ad.get('kategoria', 'kocik'), 'nazov': ad['nazov'],
            'videnia': str(views), 'narast': str(daily_gain), 'cena': str(ad['aktualna_cena']),
            'sanca_predaja_pct': str(summary['sale_prob'])
        })

        if summary["status_type"] in ["danger", "warn"]:
            alerts.append(f"""
                <div style="margin-bottom:16px;padding:14px;border-left:4px solid #e11d48;background:#fff1f2;">
                    <h3 style="margin:0 0 6px 0;">{ad['nazov']} ({weather['location_label']}) &mdash; {summary['status_label']}</h3>
                    <p style="margin:0 0 6px 0;font-size:13px;">{summary['meaning']}</p>
                    <p style="margin:0 0 8px 0;font-size:13px;"><strong>Odporúčaný krok:</strong> {summary['rec']}</p>
                    <a href="{ad['url']}" style="color:#be123c;font-weight:bold;">Otvoriť inzerát na Bazoši →</a>
                </div>
            """)

    save_all_rows(rows)
    generate_html_dashboard(ads, rows, summaries, ad_contexts)

    if alerts:
        html_mail = f"""
        <html><body style="font-family:Arial,sans-serif;color:#1e293b;">
            <h2>🔔 Bazoš Predictive BI: Analytický sumár & Pravdepodobnosť predaja ({today_str})</h2>
            {''.join(alerts)}
        </body></html>
        """
        send_email(f"🔔 Bazoš BI: Predikcia a odporúčanie úpravy ({today_str})", html_mail)


if __name__ == "__main__":
    main()
