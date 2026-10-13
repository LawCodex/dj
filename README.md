# Djibouti (DJ) — legislation as Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

Legislation of the Republic of Djibouti in **French** (`fr/`) and, where the source provides it, **Arabic** (`ar/`)
— the two official languages — from official sources:

* the **Constitution** of 15 September 1992, as published by the Presidency of the Republic (presidence.dj);
* all **laws** (*lois*, including constitutional laws), **organic laws**, **finance laws** and **ordinances**
  published on the electronic Official Journal of the Republic of Djibouti (**eJO**, journalofficiel.dj, run by
  the Secrétariat général du Gouvernement), whose texts are available as HTML.

Retrieved 2026-10-13.

<!-- COUNTS -->
| Directory | Files |
|---|---|
| `ar/lois-organiques/` | 1 |
| `ar/lois/` | 62 |
| `fr/constitution/` | 1 |
| `fr/lois-de-finances/` | 56 |
| `fr/lois-organiques/` | 15 |
| `fr/lois/` | 2433 |
| `fr/ordonnances/` | 213 |
| **Total** | **2781** |
<!-- /COUNTS -->

## Structure

```
fr/constitution/constitution-1992.md
fr/lois/<year>/<slug>.md               lois (incl. lois constitutionnelles)
fr/lois-organiques/<year>/<slug>.md
fr/lois-de-finances/<year>/<slug>.md
fr/ordonnances/<year>/<slug>.md
ar/<same>/...                          Arabic text, where the eJO record has one (same file name as the French)
```

File names are slugs of the official reference (e.g. `loi-100-an-15-7eme-l.md` for *Loi n°100/AN/15/7ème L*). The
year directory is derived from the reference (`/AN/15/` = 2015) or, failing that, from the title or the
publication date. Front matter: `identifier` is the official reference; `status` is `unknown` (the eJO does not
flag repealed texts). The body reproduces the *visas* (preamble), the articles (`Article N` headings, with
`TITRE`/`CHAPITRE`/`SECTION` headings above them) and the signature block.

## Sources

| Source | URL | Used for |
|---|---|---|
| Journal Officiel électronique de la République de Djibouti (eJO) | https://www.journalofficiel.dj/ (REST: `/wp-json/wp/v2/texte-juridique?nature-dun-texte=<id>`) | laws, organic laws, finance laws, ordinances |
| Présidence de la République — Constitution | https://www.presidence.dj/page/constitution | Constitution (French) |

## Not covered / known gaps

* **Decrees, arrêtés, decisions, circulars** etc. published in the eJO (about 50,000 texts, most of them individual
  measures such as appointments) are not included. Only the legislative texts are.
* The eJO's PDF editions of the Official Journal are not used (their download is announced as a paid feature); the
  HTML texts are freely displayed on the site and are used as is. Some older texts carry only a title and a short
  body, as entered in the eJO.
* Arabic texts are published only for a small number of recent laws (`ar/`). The Arabic version of the
  Constitution was not included.
* Constitution: the text as displayed by the Presidency website; constitutional laws revising it (2010, 2025, …)
  are in `fr/lois/`, and the Presidency page may not reflect the most recent revision.
* No consolidation: laws are as published; amending laws are separate files.

## Copyright

Official texts of the Republic of Djibouti (laws and regulations published in the Official Journal) are public
legal texts; the eJO and Presidency sites state "tous droits réservés" for the site itself but publish the texts
for public information. The Markdown conversion is provided as is, for information; the authoritative text is the
Journal Officiel de la République de Djibouti.

## Regenerate

```
python3 -m pip install -r scripts/requirements.txt
python3 scripts/dj_fetch.py         # API responses cached in ../_raw/dj; --no-download to rebuild from cache
python3 scripts/dj_readme.py        # refresh the counts table
```
