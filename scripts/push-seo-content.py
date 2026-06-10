#!/usr/bin/env python3
"""
Push the local SEO content (seo-content/FINAL-*.md) into Shopify, in all 4
languages (EN/FR/DE/ES). PREPARED — do NOT run until the theme is validated live
and you give the GO.

What it does
------------
1. COLLECTIONS (7): custom.seo_intro (text), custom.seo_body (rich_text),
   custom.faq (json) — base value in the shop PRIMARY locale + translations for
   the other published locales (via translationsRegister).
2. PRODUCTS (17): SEO title_tag/description_tag, body_html (description),
   custom.short_description, custom.dimensions — base + translations.
   (Per-product STORY metaobjects + menu/announcement translations are handled
    by separate modules — see TODO at the bottom.)

Safety
------
- Idempotent: metafieldsSet/translationsRegister overwrite, they don't duplicate.
- --dry-run prints what would be sent without writing.
- --only collections|products   --limit N   to test on a subset first.
- Does NOT touch the theme, products' prices, inventory, or status.

Usage
-----
  export SHOPIFY_STORE="rack-and-ride.myshopify.com"
  export SHOPIFY_ADMIN_TOKEN="shpat_xxx"   # custom app, scopes: write_products,
                                           # write_translations, write_metaobjects
  python3 scripts/push-seo-content.py --dry-run --only collections --limit 1
  python3 scripts/push-seo-content.py --only collections
  python3 scripts/push-seo-content.py            # everything
"""
import os, re, json, sys, time, argparse, urllib.request, urllib.error

STORE = os.environ.get("SHOPIFY_STORE", "rack-and-ride.myshopify.com")
TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
API = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEO = os.path.join(HERE, "seo-content")

# File language marker -> Shopify locale prefix
LANGS = {"EN": "en", "FR": "fr", "DE": "de", "es": "es", "ES": "es"}
COLL_HANDLES = ["surfboard-wall-mount", "skateboard-wall-mounts", "snowboard-wall-mounts",
                "skis-wall-mounts", "bike-racks", "kitesurf-racks", "deco"]

# ---------------------------------------------------------------- API helper
def gql(query, variables=None):
    if not TOKEN:
        sys.exit("ERROR: set SHOPIFY_ADMIN_TOKEN (custom app Admin API token).")
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        f"https://{STORE}/admin/api/{API}/graphql.json", data=body,
        headers={"Content-Type": "application/json", "X-Shopify-Access-Token": TOKEN})
    for attempt in range(5):
        try:
            r = urllib.request.urlopen(req)
            data = json.loads(r.read())
            if data.get("errors"):
                raise RuntimeError(json.dumps(data["errors"]))
            return data["data"]
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503):
                time.sleep(2 * (attempt + 1)); continue
            raise
    raise RuntimeError("gql failed after retries")

# ---------------------------------------------------------------- markdown -> rich text
def _inline(s):
    nodes, pos = [], 0
    for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', s):
        if m.start() > pos: nodes.append({"type": "text", "value": s[pos:m.start()]})
        nodes.append({"type": "link", "url": m.group(2), "title": "",
                      "children": [{"type": "text", "value": m.group(1)}]})
        pos = m.end()
    if pos < len(s): nodes.append({"type": "text", "value": s[pos:]})
    return nodes or [{"type": "text", "value": s}]

def md_to_richtext(md):
    children = []
    for chunk in re.split(r'\n\s*\n', md.strip()):
        chunk = chunk.strip()
        if not chunk: continue
        lines = chunk.split('\n')
        if lines[0].startswith('## '):
            children.append({"type": "heading", "level": 2,
                             "children": [{"type": "text", "value": lines[0][3:].strip()}]})
            rest = ' '.join(l.strip() for l in lines[1:]).strip()
            if rest: children.append({"type": "paragraph", "children": _inline(rest)})
        else:
            children.append({"type": "paragraph",
                             "children": _inline(' '.join(l.strip() for l in lines))})
    return json.dumps({"type": "root", "children": children}, ensure_ascii=False)

def md_to_html(md):
    out = []
    for chunk in re.split(r'\n\s*\n', md.strip()):
        chunk = chunk.strip()
        if not chunk: continue
        lines = chunk.split('\n')
        def inl(t):
            return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
        if lines[0].startswith('## '):
            out.append(f"<h2>{inl(lines[0][3:].strip())}</h2>")
            rest = ' '.join(l.strip() for l in lines[1:]).strip()
            if rest: out.append(f"<p>{inl(rest)}</p>")
        elif lines[0].startswith('### '):
            out.append(f"<h3>{inl(lines[0][4:].strip())}</h3>")
            rest = ' '.join(l.strip() for l in lines[1:]).strip()
            if rest: out.append(f"<p>{inl(rest)}</p>")
        else:
            out.append(f"<p>{inl(' '.join(l.strip() for l in lines))}</p>")
    return ''.join(out)

# ---------------------------------------------------------------- parse collections (per lang)
def _faq_paragraphs(t):
    faq = []
    for p in re.split(r'\n\s*\n', t.strip()):
        m = re.match(r'^\*\*(.+?)\*\*\s*(.+)$', p.strip(), re.S)
        if m: faq.append({"question": m.group(1).strip(),
                          "answer": ' '.join(l.strip() for l in m.group(2).split('\n')).strip()})
    return faq

def _faq_lines(t):
    faq = []
    for line in t.split('\n'):
        m = re.match(r'^[-*\s]*\*\*(.+?)\*\*\s*(.+)$', line.strip())
        if m: faq.append({"question": m.group(1).strip(), "answer": m.group(2).strip()})
    return faq

def parse_collections():
    """Returns {handle: {lang: {seo_intro, seo_body(richtext json), faq(json)}}}"""
    text = ""
    for f in ("FINAL-collections-1.md", "FINAL-collections-2.md"):
        text += "\n" + open(os.path.join(SEO, f), encoding="utf-8").read()
    hdr = list(re.finditer(r'(?m)^## .+?`([a-z0-9-]+)`.*$', text))
    out = {}
    for i, m in enumerate(hdr):
        h = m.group(1)
        if h not in COLL_HANDLES: continue
        body = text[m.start():(hdr[i+1].start() if i+1 < len(hdr) else len(text))]
        out[h] = {}
        for L in ("EN", "FR", "DE", "ES"):
            def block(title):
                try: return body.split('### '+title)[1].split('**'+L+'**')[1].split('**FR**' if L=='EN' else '**')[0]
                except Exception: return ""
            # robust per-language slice
            chap = _lang_slice(body, 'Chapeau', L)
            corps = _lang_slice(body, 'Corps SEO', L)
            before, _, after = corps.partition('## FAQ')
            if after.strip():
                seo_body = md_to_richtext(before); faq = _faq_paragraphs(after)
            else:
                seo_body = md_to_richtext(corps)
                faq = _faq_lines(_lang_slice(body, 'FAQ', L)) if '### FAQ' in body else []
                il = _intlinks(body, L)
                if il:
                    rt = json.loads(seo_body); rt["children"].append({"type":"paragraph","children":_inline(il)})
                    seo_body = json.dumps(rt, ensure_ascii=False)
            out[h][L] = {
                "seo_intro": ' '.join(l.strip() for l in chap.split('\n')).strip(),
                "seo_body": seo_body,
                "faq": json.dumps(faq, ensure_ascii=False),
            }
    return out

def _lang_slice(body, section, L):
    seq = ["EN", "FR", "DE", "ES"]
    try:
        seg = body.split('### ' + section, 1)[1]
    except IndexError:
        return ""
    parts = seg.split('**' + L + '**', 1)
    if len(parts) < 2: return ""
    tail = parts[1]
    # cut at the next language marker
    nexts = [tail.find('**' + x + '**') for x in seq if x != L]
    nexts = [p for p in nexts if p != -1]
    cut = min(nexts) if nexts else None
    # also cut at next '### ' section
    sec = tail.find('\n### ')
    if sec != -1 and (cut is None or sec < cut): cut = sec
    return tail[:cut].strip() if cut is not None else tail.strip()

def _intlinks(body, L):
    if '### Internal links' not in body: return ""
    seg = body.split('### Internal links')[1]
    for line in seg.split('\n'):
        s = line.strip()
        if s.lower().startswith('- %s:' % L.lower()):
            return s.split(':', 1)[1].strip()
    return ""

# ---------------------------------------------------------------- push helpers
def resolve_collection_gids():
    q = "{" + " ".join(f'c{i}: collectionByHandle(handle:"{h}"){{id}}'
                        for i, h in enumerate(COLL_HANDLES)) + "}"
    d = gql(q)
    return {COLL_HANDLES[i]: d[f"c{i}"]["id"] for i in range(len(COLL_HANDLES)) if d.get(f"c{i}")}

def shop_locales():
    d = gql("{ shopLocales { locale primary published } }")
    locs = [x for x in d["shopLocales"] if x["published"]]
    primary = next((x["locale"] for x in locs if x["primary"]), "en")
    return primary, [x["locale"] for x in locs]

MF_SET = """mutation($mf:[MetafieldsSetInput!]!){metafieldsSet(metafields:$mf){
  metafields{id key} userErrors{field message}}}"""
TR_REG = """mutation($id:ID!,$tr:[TranslationInput!]!){translationsRegister(resourceId:$id,translations:$tr){
  userErrors{field message}}}"""
TR_RES = """query($id:ID!){translatableResource(resourceId:$id){translatableContent{key digest locale}}}"""

def push_metafield(owner_gid, key, mtype, values_by_lang, primary, locales, dry):
    """values_by_lang: {locale_prefix: value}. Sets base (primary) + translations."""
    base_val = values_by_lang.get(primary[:2]) or values_by_lang.get("en")
    if not base_val: return
    if dry:
        print(f"    [dry] {key} base={primary} ({len(base_val)} chars) + {len(locales)-1} translations")
        return
    d = gql(MF_SET, {"mf": [{"ownerId": owner_gid, "namespace": "custom",
                             "key": key, "type": mtype, "value": base_val}]})
    errs = d["metafieldsSet"]["userErrors"]
    if errs: print("    ! metafieldsSet", key, errs); return
    mf_gid = d["metafieldsSet"]["metafields"][0]["id"]
    # translations
    dig = {c["locale"]: c["digest"] for c in gql(TR_RES, {"id": mf_gid})["translatableResource"]["translatableContent"] if c["key"] == "value"}
    trs = []
    for loc in locales:
        if loc == primary: continue
        v = values_by_lang.get(loc[:2])
        if not v: continue
        digest = dig.get(primary) or (list(dig.values())[0] if dig else None)
        if not digest: continue
        trs.append({"locale": loc, "key": "value", "value": v, "translatableContentDigest": digest})
    if trs:
        e = gql(TR_REG, {"id": mf_gid, "tr": trs})["translationsRegister"]["userErrors"]
        if e: print("    ! translations", key, e)
    print(f"    ✓ {key} (+{len(trs)} translations)")

# ---------------------------------------------------------------- runners
def run_collections(limit, dry):
    primary, locales = shop_locales()
    print(f"Primary locale: {primary} | published: {locales}")
    gids = resolve_collection_gids()
    data = parse_collections()
    for n, h in enumerate(COLL_HANDLES):
        if limit and n >= limit: break
        if h not in gids or h not in data:
            print(f"  skip {h} (no gid/data)"); continue
        print(f"  Collection {h}")
        per = data[h]  # {EN:{...}, FR:{...}, ...}
        for key, mtype in (("seo_intro", "multi_line_text_field"),
                           ("seo_body", "rich_text_field"), ("faq", "json")):
            vals = {LANGS[L]: per[L][key] for L in ("EN", "FR", "DE", "ES") if L in per and per[L].get(key)}
            push_metafield(gids[h], key, mtype, vals, primary, locales, dry)

def run_products(limit, dry):
    print("PRODUCTS module — TODO: parse FINAL-produits-*.md (meta title_tag/description_tag,"
          " body_html, custom.short_description) + 02-optimise.md (custom.dimensions),"
          " push base + translations like collections. Implement after collections run clean.")

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", choices=["collections", "products"], default=None)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    if a.only in (None, "collections"):
        print("=== COLLECTIONS ==="); run_collections(a.limit, a.dry_run)
    if a.only in (None, "products"):
        print("=== PRODUCTS ==="); run_products(a.limit, a.dry_run)
    print("Done.")
