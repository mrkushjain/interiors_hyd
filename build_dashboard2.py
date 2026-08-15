"""
Build rich HTML dashboard from company_data.json with all comments, photos, videos, links.
"""
import json, re, os
from pathlib import Path

with open("company_data.json") as f:
    company_data = json.load(f)

MEDIA_DIR = Path("media")

# Static extra info per company
COMPANY_META = {
    "SpaceV Interior Designs":  {"location": "Nallagandla", "contact": "Vasu", "website": ""},
    "HomeLane":                  {"location": "Banjara Hills", "contact": "", "website": "https://homelane.com"},
    "SLV Interiors":             {"location": "Hyderabad", "contact": "", "website": ""},
    "Interazzo":                 {"location": "Hyderabad", "contact": "", "website": "https://interazzo.com"},
    "Trendy Space Interior":     {"location": "", "contact": "Kiran Potu", "website": ""},
    "Mohan (Independent)":       {"location": "", "contact": "Mohan", "website": ""},
    "Mega Interiors":            {"location": "Hyderabad", "contact": "", "website": ""},
    "Casa Interiors And Decor":  {"location": "", "contact": "Maneesha", "website": ""},
    "Iris Design Studio":        {"location": "Hyderabad", "contact": "Harsha", "website": ""},
    "5 Tattva Design Studio":    {"location": "", "contact": "", "website": ""},
    "My Space Design Studio":    {"location": "", "contact": "Amarender Reddy", "website": ""},
    "Houspace":                  {"location": "", "contact": "", "website": ""},
    "Luxus Design Studio":       {"location": "Hyderabad", "contact": "Anoosha", "website": ""},
    "Painter Manish":            {"location": "", "contact": "Manish", "website": ""},
    "Carpenter Gautam":          {"location": "", "contact": "Gautam", "website": ""},
}

def clean_phone(p):
    return re.sub(r"[\s\-]", "", p).lstrip("+")

def phone_link(p):
    c = clean_phone(p)
    if not c.startswith("91"):
        c = "91" + c
    return f'<a href="tel:+{c}" class="phone-btn">📞 {p}</a>'

def render_url(u):
    u = u.rstrip(".,)")
    if "instagram.com" in u:
        return f'<a href="{u}" target="_blank" class="link-btn ig-btn">📸 Instagram</a>'
    if "youtube.com" in u or "youtu.be" in u:
        return f'<a href="{u}" target="_blank" class="link-btn yt-btn">▶️ YouTube</a>'
    if "facebook.com" in u:
        return f'<a href="{u}" target="_blank" class="link-btn fb-btn">👍 Facebook</a>'
    domain = re.sub(r"https?://(www\.)?", "", u).split("/")[0]
    return f'<a href="{u}" target="_blank" class="link-btn web-btn">🔗 {domain}</a>'

def render_media(files):
    if not files:
        return ""
    items = []
    for fname in files:
        fpath = MEDIA_DIR / fname
        if not fpath.exists():
            continue
        ext = fname.rsplit(".", 1)[-1].lower()
        rel = f"media/{fname}"
        if ext in ("jpg", "jpeg", "png", "webp", "gif"):
            items.append(f'<div class="media-item"><img src="{rel}" loading="lazy" onclick="openLightbox(this.src)"></div>')
        elif ext in ("mp4", "mov", "avi", "mkv"):
            items.append(f'<div class="media-item"><video controls preload="none"><source src="{rel}"></video></div>')
    if not items:
        return ""
    return '<div class="media-grid">' + "".join(items) + '</div>'

# Sort companies by number of mentions descending
sorted_companies = sorted(company_data.items(), key=lambda x: -len(x[1]["messages"]))

# Build sidebar items
sidebar_html = ""
for name, data in sorted_companies:
    cid = re.sub(r"[^a-z0-9]", "_", name.lower())
    count = len(data["messages"])
    media_count = sum(len(e["media"]) for e in data["messages"])
    sidebar_html += f"""
    <div class="sidebar-item" onclick="showCompany('{cid}')" id="si_{cid}">
      <div class="si-name">{name}</div>
      <div class="si-meta">{count} mentions{f' · {media_count} 📷' if media_count else ''}</div>
    </div>"""

# Build company panels
panels_html = ""
for name, data in sorted_companies:
    cid = re.sub(r"[^a-z0-9]", "_", name.lower())
    meta = COMPANY_META.get(name, {})

    # Collect all unique phones and URLs across all messages
    all_phones = list(dict.fromkeys(data["phones"]))
    all_urls = list(dict.fromkeys([u.rstrip(".,)") for u in data["urls"]]))

    # Add website from meta if present
    if meta.get("website") and meta["website"] not in all_urls:
        all_urls.insert(0, meta["website"])

    phones_html = "".join(phone_link(p) for p in all_phones) if all_phones else '<span class="no-info">No phone found</span>'
    urls_html = "".join(render_url(u) for u in all_urls) if all_urls else '<span class="no-info">No links found</span>'

    contact_html = f'<div class="info-row"><span class="info-label">Contact:</span> {meta["contact"]}</div>' if meta.get("contact") else ""
    location_html = f'<div class="info-row"><span class="info-label">Location:</span> 📍 {meta["location"]}</div>' if meta.get("location") else ""

    # All comments
    comments_html = ""
    for msg in data["messages"]:
        if not msg["text"] and not msg["media"]:
            continue
        media_html = render_media(msg["media"])
        text_html = f'<div class="comment-text">{msg["text"]}</div>' if msg["text"] else ""
        msg_phones = "".join(phone_link(p) for p in msg["phones"])
        msg_urls = "".join(render_url(u) for u in msg["urls"])
        inline_links = f'<div class="inline-links">{msg_phones}{msg_urls}</div>' if msg["phones"] or msg["urls"] else ""
        comments_html += f"""
        <div class="comment-card">
          <div class="comment-header">
            <span class="comment-sender">👤 {msg['sender']}</span>
            <span class="comment-date">{msg['date']}</span>
          </div>
          {text_html}
          {inline_links}
          {media_html}
        </div>"""

    panels_html += f"""
    <div class="company-panel" id="panel_{cid}" style="display:none;">
      <div class="company-header">
        <h2>{name}</h2>
        <div class="mention-count">{len(data['messages'])} mentions in group</div>
      </div>
      {contact_html}
      {location_html}
      <div class="section-title">📞 Phone Numbers</div>
      <div class="links-row">{phones_html}</div>
      <div class="section-title">🔗 Links & Portfolio</div>
      <div class="links-row">{urls_html}</div>
      <div class="section-title">💬 All Group Comments ({len(data['messages'])})</div>
      <div class="comments-list">{comments_html}</div>
    </div>"""

first_id = re.sub(r"[^a-z0-9]", "_", sorted_companies[0][0].lower()) if sorted_companies else ""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sayuk Interiors — Full Dashboard</title>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; background:#f1f5f9; color:#1e293b; height:100vh; display:flex; flex-direction:column; }}

/* ── Top Bar ── */
.topbar {{ background:linear-gradient(135deg,#1e40af,#3b82f6); color:white; padding:14px 24px; display:flex; align-items:center; gap:16px; flex-shrink:0; }}
.topbar h1 {{ font-size:1.2rem; font-weight:700; }}
.topbar p {{ font-size:0.8rem; opacity:.8; }}
#search-top {{ margin-left:auto; padding:8px 14px; border-radius:20px; border:none; font-size:0.9rem; width:260px; outline:none; }}

/* ── Layout ── */
.layout {{ display:flex; flex:1; overflow:hidden; }}

/* ── Sidebar ── */
.sidebar {{ width:280px; background:white; border-right:1px solid #e2e8f0; overflow-y:auto; flex-shrink:0; }}
.sidebar-item {{ padding:14px 18px; cursor:pointer; border-bottom:1px solid #f1f5f9; transition:background .15s; }}
.sidebar-item:hover {{ background:#f8fafc; }}
.sidebar-item.active {{ background:#eff6ff; border-left:3px solid #3b82f6; }}
.si-name {{ font-weight:600; font-size:0.92rem; color:#0f172a; }}
.si-meta {{ font-size:0.75rem; color:#94a3b8; margin-top:3px; }}

/* ── Main ── */
.main {{ flex:1; overflow-y:auto; padding:28px 32px; }}

/* ── Company Panel ── */
.company-header {{ margin-bottom:20px; }}
.company-header h2 {{ font-size:1.6rem; font-weight:700; color:#0f172a; }}
.mention-count {{ font-size:0.85rem; color:#64748b; margin-top:4px; }}

.info-row {{ font-size:0.9rem; color:#374151; margin-bottom:8px; }}
.info-label {{ font-weight:600; color:#1e40af; }}

.section-title {{ font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em;
                  color:#64748b; margin:22px 0 10px; padding-bottom:6px; border-bottom:1px solid #e2e8f0; }}

.links-row {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:4px; }}
.phone-btn {{ display:inline-block; padding:8px 16px; background:#f0fdf4; color:#166534;
              border:1px solid #bbf7d0; border-radius:8px; font-size:0.85rem; font-weight:600;
              text-decoration:none; }}
.phone-btn:hover {{ background:#dcfce7; }}
.link-btn {{ display:inline-block; padding:8px 16px; border-radius:8px; font-size:0.85rem;
             font-weight:600; text-decoration:none; }}
.ig-btn {{ background:#fce7f3; color:#9d174d; border:1px solid #fbcfe8; }}
.yt-btn {{ background:#fef2f2; color:#991b1b; border:1px solid #fecaca; }}
.fb-btn {{ background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe; }}
.web-btn {{ background:#f8fafc; color:#334155; border:1px solid #e2e8f0; }}
.link-btn:hover {{ opacity:.85; }}
.no-info {{ font-size:0.85rem; color:#94a3b8; font-style:italic; }}

/* ── Comments ── */
.comments-list {{ display:flex; flex-direction:column; gap:14px; }}
.comment-card {{ background:white; border-radius:12px; padding:16px; box-shadow:0 1px 3px rgba(0,0,0,.07); }}
.comment-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }}
.comment-sender {{ font-weight:600; font-size:0.88rem; color:#1e40af; }}
.comment-date {{ font-size:0.78rem; color:#94a3b8; }}
.comment-text {{ font-size:0.88rem; line-height:1.6; color:#374151; white-space:pre-wrap; word-break:break-word; }}
.inline-links {{ display:flex; gap:6px; flex-wrap:wrap; margin-top:8px; }}
.inline-links .phone-btn, .inline-links .link-btn {{ font-size:0.78rem; padding:5px 10px; }}

/* ── Media Grid ── */
.media-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:8px; margin-top:12px; }}
.media-item img, .media-item video {{ width:100%; border-radius:8px; cursor:pointer; max-height:200px; object-fit:cover; }}

/* ── Lightbox ── */
#lightbox {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,.9); z-index:1000;
             align-items:center; justify-content:center; cursor:pointer; }}
#lightbox.open {{ display:flex; }}
#lightbox img {{ max-width:90vw; max-height:90vh; border-radius:8px; }}

/* ── Empty state ── */
.empty-state {{ text-align:center; padding:80px 20px; color:#94a3b8; }}
.empty-state div {{ font-size:3rem; margin-bottom:12px; }}

@media(max-width:640px) {{
  .sidebar {{ width:100%; height:auto; max-height:35vh; }}
  .layout {{ flex-direction:column; }}
  .main {{ padding:16px; }}
  #search-top {{ width:160px; }}
}}
</style>
</head>
<body>

<div class="topbar">
  <div>
    <h1>🏠 Sayuk Interiors Dashboard</h1>
    <p>My Home Sayuk, Tellapur · {len(company_data)} companies · sourced from resident group</p>
  </div>
  <input type="text" id="search-top" placeholder="Search companies…" oninput="filterSidebar(this.value)">
</div>

<div class="layout">
  <div class="sidebar" id="sidebar">{sidebar_html}</div>
  <div class="main" id="main">
    <div class="empty-state" id="empty-state">
      <div>👈</div>
      <p>Select a company from the sidebar to see all mentions, photos, and contact details.</p>
    </div>
    {panels_html}
  </div>
</div>

<div id="lightbox" onclick="closeLightbox()">
  <img id="lb-img" src="">
</div>

<script>
const firstId = "{first_id}";

function showCompany(cid) {{
  document.querySelectorAll('.company-panel').forEach(p => p.style.display='none');
  document.querySelectorAll('.sidebar-item').forEach(s => s.classList.remove('active'));
  document.getElementById('empty-state').style.display='none';
  const panel = document.getElementById('panel_'+cid);
  const si = document.getElementById('si_'+cid);
  if(panel) panel.style.display='block';
  if(si) si.classList.add('active');
  document.getElementById('main').scrollTop = 0;
}}

function filterSidebar(q) {{
  const ql = q.toLowerCase();
  document.querySelectorAll('.sidebar-item').forEach(item => {{
    const text = item.innerText.toLowerCase();
    item.style.display = text.includes(ql) ? '' : 'none';
  }});
}}

function openLightbox(src) {{
  document.getElementById('lb-img').src = src;
  document.getElementById('lightbox').classList.add('open');
}}
function closeLightbox() {{
  document.getElementById('lightbox').classList.remove('open');
}}

// Auto-select first company
if(firstId) showCompany(firstId);
</script>
</body>
</html>
"""

out = Path("dashboard2.html")
out.write_text(html, encoding="utf-8")
print(f"Dashboard written to {out}")
print(f"Companies: {len(company_data)}")
total_media = sum(sum(len(e['media']) for e in d['messages']) for d in company_data.values())
print(f"Total media files referenced: {total_media}")
