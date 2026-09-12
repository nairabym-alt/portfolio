from pathlib import Path
import json, html, re
SITE=Path(__file__).resolve().parents[1]
DIST=SITE/'dist'
data=json.loads((DIST/'content.json').read_text(encoding='utf-8'))
template='''<!doctype html><html lang="en" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#16343b"><meta name="description" content="{description}"><title>{title} — Muhammed Niraby</title><link rel="icon" type="image/png" href="/media/brand/favicon.png"><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/brand.css"><link rel="stylesheet" href="/pages.css"><link rel="stylesheet" href="/gallery.css"><script defer src="/app.js"></script></head><body><main class="loading-screen"><img src="/media/brand/logo-transparent.png" width="48" height="64" alt="Muhammed Niraby"><p>Architecture &amp; Interiors</p><noscript><h1>Muhammed Niraby</h1><p>Architecture, interior design, visualization, and technical documentation.</p><p>Enable JavaScript to explore the interactive portfolio.</p><a href="mailto:nairabymhmd@gmail.com">nairabymhmd@gmail.com</a></noscript></main></body></html>'''
routes={'':'Architecture & Interiors','about':'About','contact':'Contact','cv':'Résumé'}
descriptions={}
for c in data['categories']:
 routes[c['id']]=c['title']['en'];descriptions[c['id']]=c['intro']['en']
for p in data['projects']:
 key=p['category']+'/'+p['id'];routes[key]=p['title']['en'];descriptions[key]=p['description']['en']
for route,title in routes.items():
 target=DIST/route/'index.html';target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(template.format(title=html.escape(title,quote=True),description=html.escape(descriptions.get(route,data['profile']['bio']['en']),quote=True)),encoding='utf-8')
(DIST/'404.html').write_text(template.format(title='Page not found',description='Muhammed Niraby architecture portfolio'),encoding='utf-8')
print(f'Generated {len(routes)} static routes')
