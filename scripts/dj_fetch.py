#!/usr/bin/env python3
"""Djibouti: fetch laws, organic laws, finance laws and ordinances from the electronic Official
Journal (Journal Officiel de la République de Djibouti, eJO, journalofficiel.dj — WordPress REST API,
post type "texte-juridique") and the Constitution (presidence.dj), and write Markdown (fr/ and ar/).

Usage: python3 dj_fetch.py [--no-download]"""
import hashlib
import html
import json
import os
import re
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dj_text as T  # noqa

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(os.path.dirname(REPO), "_raw", "dj")
RETRIEVED = os.environ.get("LC_RETRIEVED", "2026-10-13")
API = "https://www.journalofficiel.dj/wp-json/wp/v2/"
NATURES = {247: ("lois", "law"), 259: ("lois-organiques", "organic_law"), 260: ("lois-de-finances", "finance_law"),
           263: ("ordonnances", "ordinance")}
CONST_URL = {"fr": "https://www.presidence.dj/page/constitution", "ar": "https://www.presidence.dj/page/constitution"}
S = requests.Session()
S.headers["User-Agent"] = T.UA


def fetch_nature(nid):
    p = os.path.join(RAW, "nature-%d.json" % nid)
    if os.path.exists(p) and "--no-download" in sys.argv:
        return json.load(open(p))
    out, page = [], 1
    while True:
        for i in range(5):
            try:
                r = S.get(API + "texte-juridique", params={"nature-dun-texte": nid, "per_page": 100, "page": page,
                                                          "_fields": "id,date,link,title,content,acf"}, timeout=180)
                r.raise_for_status()
                break
            except Exception as e:  # noqa
                print("  retry", e)
                time.sleep(15 * (i + 1))
        else:
            raise SystemExit("API failure")
        out += r.json()
        if page >= int(r.headers.get("X-WP-TotalPages", "1")):
            break
        page += 1
        time.sleep(2)
    json.dump(out, open(p, "w"), ensure_ascii=False)
    return out


def html_lines(h):
    if not h:
        return []
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|li|h\d|tr)>", "\n\n", h)
    h = re.sub(r"(?i)<(td|th)[^>]*>", " | ", h)
    t = html.unescape(re.sub(r"<[^>]+>", "", h))
    lines = []
    for x in t.replace("\r", "").split("\n"):
        x = re.sub(r"[ \t\xa0]+", " ", x).strip()
        lines.append(x)
    return lines


def year_of(ref, date, title=""):
    m = re.search(r"/AN/(\d{2})/", ref or "")
    if m:
        y = int(m.group(1))
        return str(2000 + y if y <= 40 else 1900 + y)
    m = re.search(r"\b(1[89]\d\d|20[0-4]\d)\b", (ref or "") + " " + (title or ""))
    if m:
        return m.group(1)
    m = re.match(r"^(\d{2})-\d+", (ref or "").strip())
    if m:
        y = int(m.group(1))
        return str(2000 + y if y <= 40 else 1900 + y)
    y = (date or "")[:4]
    return y if y.isdigit() and 1900 <= int(y) <= 2026 else None


AR_ART = re.compile(r"^(المادة|مادة)\s")


def ar_body(lines):
    out = []
    for x in lines:
        if not x:
            continue
        if AR_ART.match(x) and len(x) < 60:
            out += ["### " + x, ""]
        else:
            out += [x, ""]
    return out


def constitution():
    p = os.path.join(RAW, "constitution-fr.html")
    if "--no-download" not in sys.argv:
        T.fetch(CONST_URL["fr"], p, delay=10)
    t = open(p, encoding="utf-8").read()
    i = t.find("Pr&eacute;ambule")
    if i < 0:
        i = t.find("Préambule")
    j = t.find("INDEX ANALYTIQUE", i)
    seg = t[i: j if j > 0 else None]
    seg = re.split(r'<footer|class="footer', seg)[0]
    lines = html_lines(seg)
    body = T.structure(lines, "fr")
    meta = {"title": "Constitution de la République de Djibouti", "identifier": "Constitution du 15 septembre 1992",
            "type": "constitution", "jurisdiction": "dj", "language": "fr", "date": "1992-09-15", "status": "in_force",
            "source": CONST_URL["fr"], "retrieved": RETRIEVED,
            "note": "Texte publié par la Présidence de la République (version consolidée telle que publiée sur le site; les révisions constitutionnelles ultérieures à la mise à jour de la page peuvent ne pas y figurer)."}
    T.write_md(os.path.join(REPO, "fr", "constitution", "constitution-1992.md"), meta, meta["title"], body)


def main():
    os.makedirs(RAW, exist_ok=True)
    constitution()
    n = {"fr": 0, "ar": 0}
    seen = {}
    for nid, (dname, typ) in NATURES.items():
        rows = fetch_nature(nid)
        print(dname, len(rows))
        for x in rows:
            acf = x.get("acf") or {}
            title = re.sub(r"\s+", " ", html.unescape(x["title"]["rendered"])).strip()
            ref = (acf.get("reference") or "").strip()
            lines = html_lines(acf.get("visas") or "") + [""] + html_lines(x["content"]["rendered"]) + [""] + html_lines(acf.get("signature") or "")
            if sum(len(l) for l in lines) < 80:
                continue
            h = hashlib.md5((title + "\n".join(lines)).encode()).hexdigest()
            if h in seen:
                continue
            seen[h] = 1
            year = year_of(ref, x.get("date"), title)
            base = T.slug(dname[:-1] + "-" + ref if ref else title, 90)
            d = os.path.join(REPO, "fr", dname, year or "undated")
            path = os.path.join(d, base + ".md")
            if os.path.exists(path) and path in seen:
                path = os.path.join(d, base + "-%d.md" % x["id"])
            seen[path] = 1
            meta = {"title": title, "identifier": ref or None, "type": typ, "jurisdiction": "dj", "language": "fr",
                    "year": int(year) if year else None, "status": "unknown", "source": x["link"], "retrieved": RETRIEVED}
            T.write_md(path, meta, title, T.structure(lines, "fr"))
            n["fr"] += 1
            ar = html_lines(acf.get("visas_ar") or "") + [""] + html_lines(acf.get("contenu_ar") or "") + [""] + html_lines(acf.get("signature_ar") or "")
            if sum(len(l) for l in ar) > 200:
                tar = re.sub(r"\s+", " ", " ".join(html_lines(acf.get("titre_ar") or "")) + " " + " ".join(html_lines(acf.get("commentaire_ar") or ""))).strip() or title
                meta_ar = dict(meta, title=tar, language="ar")
                T.write_md(os.path.join(REPO, "ar", dname, year or "undated", os.path.basename(path)), meta_ar, tar, ar_body(ar))
                n["ar"] += 1
    print(n)


if __name__ == "__main__":
    main()
