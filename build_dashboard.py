"""
Build an HTML dashboard from interior_leads.json
"""
import json, re

with open("interior_leads.json") as f:
    leads = json.load(f)

# ── Manually curated company entries extracted from the messages ──────────────
COMPANIES = [
    {
        "name": "SpaceV Interior Designs",
        "contact": "Vasu",
        "phone": "8500010069",
        "location": "Nallagandla",
        "review": "Checked 20+ interiors — from big brands like Livspace, Homelane, Arista to local carpenters. Finally went ahead with SpaceV and it turned out way better than expected.",
        "reviewer": "Ram Neelam",
        "flat": "2.5 BHK",
        "facing": "WF",
        "tower": "Tridasa",
        "date": "2025-06-11",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "HomeLane",
        "contact": "",
        "phone": "+91 8179456656",
        "location": "Banjara Hills",
        "review": "Listed as a good interior company by multiple residents.",
        "reviewer": "Gurava Maruri / Haritha Reddy / R H",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "SLV Interiors",
        "contact": "",
        "phone": "+91 9666886132",
        "location": "",
        "review": "Recommended by multiple group members as a good interior company.",
        "reviewer": "Gurava Maruri / Haritha Reddy",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Interazzo",
        "contact": "",
        "phone": "",
        "location": "",
        "review": "Quality wise liked Interazzo the best but yes it is slightly on the expensive side.",
        "reviewer": "Asmita",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2025-07-18",
        "sentiment": "positive",
        "urls": ["https://interazzo.com/"],
    },
    {
        "name": "Trendy Space Interior",
        "contact": "Kiran Potu",
        "phone": "9948591230",
        "location": "",
        "review": "Recommended by group members.",
        "reviewer": "Gurava Maruri",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Mohan (Independent)",
        "contact": "Mohan",
        "phone": "+918099192769",
        "location": "",
        "review": "After burning my fingers and finally got my interior done by this guy. In my present community he did for 5-6 flats. Also does for NRIs.",
        "reviewer": "Ravi",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-20",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Mega Interiors",
        "contact": "",
        "phone": "9247611111",
        "location": "",
        "review": "Hassle free and affordable. Cost around 13L.",
        "reviewer": "Sasank",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-08-24",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Casa Interiors And Decor",
        "contact": "Maneesha",
        "phone": "+91 85999 47444",
        "location": "",
        "review": "We Design Your Dream Home. Instagram and YouTube portfolio available.",
        "reviewer": "Amarsrinivas Eli",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2025-02-06",
        "sentiment": "neutral",
        "urls": [
            "https://www.instagram.com/casa_interiors_decor/",
            "https://youtube.com/@casainteriorsanddecors",
        ],
    },
    {
        "name": "Iris Design Studio",
        "contact": "Harsha",
        "phone": "+91 99495 12847",
        "location": "Hyderabad",
        "review": "Work done by friend's interior firm. Recommended for quotations.",
        "reviewer": "Bhargav BV",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2025-03-14",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "5 Tattva Design Studio",
        "contact": "",
        "phone": "9913957537",
        "location": "",
        "review": "Committed to creating homes that reflect your personality and style.",
        "reviewer": "Sudipta",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2025-03-30",
        "sentiment": "neutral",
        "urls": [],
    },
    {
        "name": "My Space Design Studio Interiors",
        "contact": "Amarender Reddy",
        "phone": "+91 9515133080 / +91 8125920636",
        "location": "",
        "review": "Highly recommend. Did interior work for 2500 sqft flat at Lotus Grand, Kokapet. Designs are exceptional, execution and final output truly commendable.",
        "reviewer": "Sanju / Pallavi Kodali",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2025-08-29",
        "sentiment": "positive",
        "urls": ["https://youtu.be/N7lfDscy4rE"],
    },
    {
        "name": "Houspace",
        "contact": "",
        "phone": "90000 83426",
        "location": "",
        "review": "Interior designing expertise. Reached out to the group for enquiries.",
        "reviewer": "Vijay Mohan Bangaru",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-12-13",
        "sentiment": "neutral",
        "urls": [],
    },
    {
        "name": "Luxus Design Studio",
        "contact": "Anoosha (Architect)",
        "phone": "9049713333",
        "location": "Hyderabad",
        "review": "Interior design studio with creative designers. Own modular factory. 97797 72579 also listed. Active in the group since 2022.",
        "reviewer": "Asmita",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2025-07-18",
        "sentiment": "positive",
        "urls": ["https://www.instagram.com/luxusdesignstudio.in/"],
    },
    {
        "name": "Woodz & Nails Interiors",
        "contact": "",
        "phone": "",
        "location": "",
        "review": "Recommended by multiple group members.",
        "reviewer": "Gurava Maruri / Haritha Reddy",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Care Interiors",
        "contact": "",
        "phone": "",
        "location": "Nallagandla",
        "review": "Recommended by group members.",
        "reviewer": "Gurava Maruri",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Painter Manish (Independent)",
        "contact": "Manish",
        "phone": "9515552622",
        "location": "",
        "review": "Has done good work. Economical rates for painting work.",
        "reviewer": "Jayant Kumar Singh (JKS)",
        "flat": "",
        "facing": "",
        "tower": "MyHome Tridasa",
        "date": "2024-02-17",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Carpenter Gautam (Independent)",
        "contact": "Gautam",
        "phone": "9651202712",
        "location": "",
        "review": "Has done good work. Economical rates for carpentry work.",
        "reviewer": "Jayant Kumar Singh (JKS)",
        "flat": "",
        "facing": "",
        "tower": "MyHome Tridasa",
        "date": "2024-02-29",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Nilesh Gaydhani (Independent Designer)",
        "contact": "Nilesh Gaydhani",
        "phone": "9881472773",
        "location": "Maharashtra / Hyderabad",
        "review": "20 years experience. 350 turn-key projects. Residential, commercial, supervision, renovation. All under one roof.",
        "reviewer": "Sanchita",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-07-26",
        "sentiment": "neutral",
        "urls": [],
    },
    {
        "name": "Icons Interiors",
        "contact": "",
        "phone": "",
        "location": "",
        "review": "Recommended by group members.",
        "reviewer": "Gurava Maruri",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Axiis Interiors",
        "contact": "",
        "phone": "",
        "location": "",
        "review": "Recommended by group members.",
        "reviewer": "Gurava Maruri",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Dzine Studio",
        "contact": "",
        "phone": "",
        "location": "",
        "review": "Recommended by group members.",
        "reviewer": "Gurava Maruri",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "YesYou Interiors",
        "contact": "",
        "phone": "78912 42360",
        "location": "",
        "review": "Recommended by group members.",
        "reviewer": "Gurava Maruri",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Salt Interiors",
        "contact": "",
        "phone": "9573285458",
        "location": "",
        "review": "Recommended by group members.",
        "reviewer": "Gurava Maruri",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Wurfel Interiors",
        "contact": "",
        "phone": "+91 8769836054",
        "location": "",
        "review": "Recommended by group members.",
        "reviewer": "Gurava Maruri",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
    {
        "name": "Nifty Interio",
        "contact": "",
        "phone": "+91 99666 60069",
        "location": "",
        "review": "Recommended by group members.",
        "reviewer": "Gurava Maruri",
        "flat": "",
        "facing": "",
        "tower": "",
        "date": "2024-06-12",
        "sentiment": "positive",
        "urls": [],
    },
]

# ── Build HTML ────────────────────────────────────────────────────────────────
def sentiment_badge(s):
    colors = {"positive": "#22c55e", "negative": "#ef4444", "neutral": "#f59e0b"}
    labels = {"positive": "✅ Recommended", "negative": "⚠️ Avoid", "neutral": "ℹ️ Info"}
    bg = colors.get(s, "#888")
    label = labels.get(s, "")
    return f'<span class="badge" style="background:{bg};">{label}</span>'

def phone_link(p):
    if not p: return ""
    # Handle multiple phones
    parts = [x.strip() for x in p.replace("/", ",").split(",")]
    links = []
    for part in parts:
        clean = re.sub(r"[\s\-\+]", "", part)
        if clean.startswith("91") and len(clean) == 12:
            clean = clean[2:]
        links.append(f'<a href="tel:+91{clean}" class="phone-link">📞 {part}</a>')
    return " ".join(links)

def url_links(urls):
    if not urls: return ""
    out = []
    for u in urls:
        if "instagram" in u:
            out.append(f'<a href="{u}" target="_blank" class="url-link">📸 Instagram</a>')
        elif "youtube" in u or "youtu.be" in u:
            out.append(f'<a href="{u}" target="_blank" class="url-link">▶️ YouTube</a>')
        else:
            domain = re.sub(r'https?://(www\.)?', '', u).split('/')[0]
            out.append(f'<a href="{u}" target="_blank" class="url-link">🔗 {domain}</a>')
    return " ".join(out)

cards_html = ""
for c in COMPANIES:
    flat_badge = f'<span class="tag">{c["flat"]}</span>' if c["flat"] else ""
    facing_badge = f'<span class="tag tag-facing">{c["facing"]}</span>' if c["facing"] else ""
    tower_badge = f'<span class="tag tag-tower">{c["tower"]}</span>' if c["tower"] else ""
    location_text = f'<div class="meta">📍 {c["location"]}</div>' if c["location"] else ""
    contact_text = f'<div class="meta">👤 {c["contact"]}</div>' if c["contact"] else ""
    phone_text = f'<div class="phone-row">{phone_link(c["phone"])}</div>' if c["phone"] else ""
    url_text = f'<div class="url-row">{url_links(c["urls"])}</div>' if c["urls"] else ""

    cards_html += f"""
    <div class="card"
         data-sentiment="{c['sentiment']}"
         data-flat="{c['flat'].lower()}"
         data-facing="{c['facing'].lower()}"
         data-tower="{c['tower'].lower()}">
      <div class="card-header">
        <div class="company-name">{c['name']}</div>
        {sentiment_badge(c['sentiment'])}
      </div>
      <div class="tags-row">{flat_badge}{facing_badge}{tower_badge}</div>
      {contact_text}
      {location_text}
      {phone_text}
      {url_text}
      <div class="review">"{c['review']}"</div>
      <div class="reviewer">— {c['reviewer']} &nbsp;·&nbsp; {c['date']}</div>
    </div>
    """

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sayuk Interiors Dashboard</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f1f5f9; color: #1e293b; }}

  header {{ background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 28px 32px; }}
  header h1 {{ font-size: 1.8rem; font-weight: 700; }}
  header p {{ margin-top: 6px; opacity: 0.85; font-size: 0.95rem; }}

  .stats {{ display: flex; gap: 16px; margin: 24px 32px 0; flex-wrap: wrap; }}
  .stat {{ background: white; border-radius: 12px; padding: 16px 24px; flex: 1; min-width: 140px;
           box-shadow: 0 1px 3px rgba(0,0,0,.08); }}
  .stat-num {{ font-size: 2rem; font-weight: 700; color: #1e40af; }}
  .stat-label {{ font-size: 0.8rem; color: #64748b; margin-top: 2px; }}

  .filters {{ margin: 20px 32px; display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}
  .filters label {{ font-size: 0.85rem; font-weight: 600; color: #475569; }}
  .filters input, .filters select {{
    padding: 8px 14px; border: 1px solid #cbd5e1; border-radius: 8px;
    font-size: 0.9rem; background: white; outline: none;
  }}
  .filters input:focus, .filters select:focus {{ border-color: #3b82f6; }}
  .filter-btn {{
    padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer;
    font-size: 0.85rem; font-weight: 600; background: #e2e8f0; color: #475569;
    transition: all .15s;
  }}
  .filter-btn.active, .filter-btn:hover {{ background: #3b82f6; color: white; }}

  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
           gap: 20px; padding: 20px 32px 40px; }}

  .card {{ background: white; border-radius: 14px; padding: 20px;
           box-shadow: 0 1px 3px rgba(0,0,0,.08); transition: box-shadow .2s; }}
  .card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,.12); }}
  .card[style*="display:none"] {{ display: none !important; }}

  .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 10px; }}
  .company-name {{ font-size: 1.05rem; font-weight: 700; color: #0f172a; flex: 1; }}
  .badge {{ font-size: 0.72rem; font-weight: 600; color: white; padding: 3px 9px;
            border-radius: 20px; white-space: nowrap; }}

  .tags-row {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }}
  .tag {{ font-size: 0.75rem; padding: 3px 10px; border-radius: 20px;
          background: #dbeafe; color: #1e40af; font-weight: 600; }}
  .tag-facing {{ background: #fce7f3; color: #9d174d; }}
  .tag-tower {{ background: #dcfce7; color: #166534; }}

  .meta {{ font-size: 0.83rem; color: #64748b; margin-bottom: 5px; }}
  .phone-row {{ margin: 10px 0 6px; display: flex; gap: 8px; flex-wrap: wrap; }}
  .phone-link {{ display: inline-block; background: #f0fdf4; color: #166534;
                 padding: 5px 12px; border-radius: 8px; font-size: 0.82rem;
                 text-decoration: none; font-weight: 600; border: 1px solid #bbf7d0; }}
  .phone-link:hover {{ background: #dcfce7; }}

  .url-row {{ margin: 6px 0; display: flex; gap: 8px; flex-wrap: wrap; }}
  .url-link {{ display: inline-block; background: #eff6ff; color: #1e40af;
               padding: 5px 12px; border-radius: 8px; font-size: 0.82rem;
               text-decoration: none; font-weight: 600; border: 1px solid #bfdbfe; }}
  .url-link:hover {{ background: #dbeafe; }}

  .review {{ font-size: 0.85rem; color: #374151; margin-top: 12px; line-height: 1.5;
             font-style: italic; border-left: 3px solid #e2e8f0; padding-left: 10px; }}
  .reviewer {{ font-size: 0.78rem; color: #94a3b8; margin-top: 8px; text-align: right; }}

  #no-results {{ display: none; text-align: center; padding: 60px; color: #94a3b8; font-size: 1.1rem; grid-column: 1/-1; }}

  @media(max-width:600px) {{
    .grid {{ padding: 16px; gap: 14px; }}
    .stats, .filters {{ margin: 16px; }}
    header {{ padding: 20px 16px; }}
  }}
</style>
</head>
<body>

<header>
  <h1>🏠 Sayuk Interior Companies Dashboard</h1>
  <p>My Home Sayuk, Tellapur, Hyderabad — sourced from resident Telegram group</p>
</header>

<div class="stats">
  <div class="stat"><div class="stat-num">{len(COMPANIES)}</div><div class="stat-label">Companies Listed</div></div>
  <div class="stat"><div class="stat-num">{sum(1 for c in COMPANIES if c['sentiment']=='positive')}</div><div class="stat-label">Recommended</div></div>
  <div class="stat"><div class="stat-num">{sum(1 for c in COMPANIES if c['phone'])}</div><div class="stat-label">With Phone Numbers</div></div>
  <div class="stat"><div class="stat-num">{sum(1 for c in COMPANIES if c['urls'])}</div><div class="stat-label">With Portfolio Links</div></div>
</div>

<div class="filters">
  <label>Filter:</label>
  <input type="text" id="search" placeholder="Search company, contact, review..." oninput="applyFilters()">
  <select id="flat-filter" onchange="applyFilters()">
    <option value="">All Flat Types</option>
    <option value="2bhk">2 BHK</option>
    <option value="2.5 bhk">2.5 BHK</option>
    <option value="3bhk">3 BHK</option>
  </select>
  <select id="facing-filter" onchange="applyFilters()">
    <option value="">All Facing</option>
    <option value="ef">East Facing</option>
    <option value="wf">West Facing</option>
  </select>
  <button class="filter-btn active" onclick="filterSentiment('', this)">All</button>
  <button class="filter-btn" onclick="filterSentiment('positive', this)">✅ Recommended</button>
  <button class="filter-btn" onclick="filterSentiment('neutral', this)">ℹ️ Info only</button>
</div>

<div class="grid" id="grid">
  {cards_html}
  <div id="no-results">No companies match your filters.</div>
</div>

<script>
let activeSentiment = '';

function filterSentiment(s, btn) {{
  activeSentiment = s;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}}

function applyFilters() {{
  const q = document.getElementById('search').value.toLowerCase();
  const flat = document.getElementById('flat-filter').value.toLowerCase();
  const facing = document.getElementById('facing-filter').value.toLowerCase();
  let visible = 0;

  document.querySelectorAll('.card').forEach(card => {{
    const text = card.innerText.toLowerCase();
    const cardFlat = card.dataset.flat;
    const cardFacing = card.dataset.facing;
    const cardSentiment = card.dataset.sentiment;

    const matchQ = !q || text.includes(q);
    const matchFlat = !flat || cardFlat.includes(flat);
    const matchFacing = !facing || cardFacing === facing;
    const matchSentiment = !activeSentiment || cardSentiment === activeSentiment;

    if (matchQ && matchFlat && matchFacing && matchSentiment) {{
      card.style.display = '';
      visible++;
    }} else {{
      card.style.display = 'none';
    }}
  }});

  document.getElementById('no-results').style.display = visible === 0 ? 'block' : 'none';
}}
</script>

</body>
</html>
"""

with open("dashboard.html", "w") as f:
    f.write(html)

print("Dashboard written to dashboard.html")
print(f"Total companies: {len(COMPANIES)}")
