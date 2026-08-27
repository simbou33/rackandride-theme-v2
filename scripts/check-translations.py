#!/usr/bin/env python3
"""Flag machine-sounding product copy in fr / de / es.

The copy on this shop was written in English first. Where a translation stayed
close to the English word order, the result is grammatical but not idiomatic —
"décolle votre planche du parquet" for "lifts your board off the ground". This
scores each translated body against markers of that failure so the worst ones
can be rewritten first, instead of re-reading the whole catalogue by hand.

Every marker below was found in this catalogue's own copy, not invented: add to
the lists as new ones turn up. A high score is a reason to read the text, never
a verdict on its own.

Usage:
    python3 scripts/check-translations.py <shopify-graphql-dump.json> [locale ...]

The dump is the result of a `products { handle title descriptionHtml
fr/de/es: translations(locale:) { key value } }` query.
"""
import json, re, sys
from collections import defaultdict

# Structures that only exist in these texts because English had them there.
CALQUES = {
    'fr': [
        (r"\bQue vous \w+iez\b", "« Que vous …iez » — calque de *whether you*"),
        (r"\btrouve déjà sa réponse\b", "« trouve déjà sa réponse » — calque de *is already answered*"),
        (r"\bs'expose fièrement\b|\brepose fier\b", "« repose fier » — calque de *sits proud*"),
        (r"\bsi bien que\b", "« si bien que » — calque de *so that*, lourd à l'oral"),
        (r"\bqui fait toute la valeur\b", "calque de *that makes it worth*"),
        (r"\bun cran en dessous\b", "calque de *a step down*"),
        (r"\bde collection retraité\b|\bretraité\b", "« retraité » pour *retired* — ne se dit pas d'un objet"),
        (r"\bdécolle votre \w+ du \w+\b", "« décolle … du parquet » — calque de *lifts off the ground*"),
        (r"\breste à l'écart de\b", "calque de *stays away from*"),
        (r"\bsortir une \w+ du sol\b", "calque de *get it off the floor*"),
        (r"\bPoussez votre\b", "« Poussez » pour *push* — le geste n'est pas celui-là"),
        (r"\ble choix premium\b", "anglicisme non traduit dans une phrase française"),
    ],
    'de': [
        (r"\bOb du \w+ oder\b", "« Ob du … oder » — calque de *whether you*"),
        (r"\bist bereits beantwortet\b", "calque de *is already answered*"),
        (r"\bstolz und geschützt\b", "calque de *proud and protected*"),
        (r"\bso dass die eigentliche Frage\b", "calque de *so the real question*"),
        (r"\beine Stufe unter\b", "calque de *a step down*"),
        (r"\bvom Boden zu heben\b", "calque de *to lift off the floor*"),
    ],
    'es': [
        (r"\bTanto si \w+ como\b", "calque de *whether you … or*"),
        (r"\bya está respondida\b", "calque de *is already answered*"),
        (r"\borgulloso y protegido\b", "calque de *proud and protected*"),
        (r"\bun escalón por debajo\b", "calque de *a step down*"),
        (r"\blevantar una tabla del suelo\b", "calque de *get a board off the floor*"),
    ],
}

# English leans on possessives far more than these languages do. A translation
# that keeps every one of them reads as translated even when each sentence is
# fine on its own.
POSSESSIVE = {
    'fr': r"\b(votre|vos)\b",
    'de': r"\b(dein|deine|deinen|deinem|deiner|Ihr|Ihre|Ihren|Ihrem)\b",
    'es': r"\b(tu|tus|su|sus)\b",
}

def plain(html):
    txt = re.sub(r'<[^>]+>', ' ', html or '')
    return re.sub(r'\s+', ' ', txt).strip()

def score(text, loc):
    words = len(text.split()) or 1
    hits = []
    for pattern, why in CALQUES.get(loc, []):
        n = len(re.findall(pattern, text, re.I))
        if n:
            hits.append((n, why))
    poss = len(re.findall(POSSESSIVE.get(loc, r'(?!)'), text, re.I))
    poss_rate = poss * 100.0 / words
    # Em dashes are an English punctuation habit; kept sparingly they are fine,
    # so this only counts once the density is clearly imported.
    dash_rate = text.count('—') * 100.0 / words
    total = sum(n for n, _ in hits) * 3 + max(0, poss_rate - 2.5) * 2 + max(0, dash_rate - 0.6) * 3
    return total, hits, poss_rate, dash_rate, words

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    data = json.load(open(sys.argv[1]))['data']['products']['nodes']
    locales = sys.argv[2:] or ['fr', 'de', 'es']

    for loc in locales:
        rows = []
        for p in data:
            body = next((t['value'] for t in p.get(loc, []) if t['key'] == 'body_html'), None)
            if not body:
                rows.append((None, p['handle'], 0, [], 0, 0, 0))
                continue
            rows.append((True,) + (p['handle'],) + score(plain(body), loc))
        rows.sort(key=lambda r: -r[2])

        print('\n' + '═' * 78)
        print(' %s — %d fiches' % (loc.upper(), len(rows)))
        print('═' * 78)
        for ok, handle, total, hits, poss, dash, words in rows:
            if ok is None:
                print('  %-46s  —  pas de traduction' % handle[:46])
                continue
            flag = '⚑' if total >= 6 else ('·' if total >= 3 else ' ')
            print('%s %-44s %5.1f   poss %.1f%%  tirets %.1f%%  %d mots'
                  % (flag, handle[:44], total, poss, dash, words))
            for n, why in hits:
                print('      %d× %s' % (n, why))

if __name__ == '__main__':
    main()
