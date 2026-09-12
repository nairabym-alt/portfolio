# Muhammed Niraby — Architecture & Interiors

The complete bilingual portfolio: 25 projects across architecture, interiors,
animation and films, and technical drawings. This repository keeps the final
website's original-quality media. No extra image or video compression is applied.

## View locally

Install Python 3.10 or newer, then run from this folder:

```sh
python -m http.server 8765 --directory dist
```

Open `http://localhost:8765/`. Use a local web server; opening an HTML file directly
does not load the project data correctly.

## Edit the portfolio

| File | Purpose |
| --- | --- |
| `dist/content.json` | Arabic and English project text, categories, profile and media references |
| `dist/app.js` | Pages, navigation, gallery, zoom and film interactions |
| `dist/styles.css`, `brand.css`, `pages.css`, `gallery.css` | Layout, typography and colours |
| `dist/media/` | All website photos, full-size views, videos, drawings, documents and branding |
| `dist/fonts/` | Local fonts and their licences |
| `scripts/finalize_site.py` | Regenerate the 33 page entrypoints after changing titles/descriptions |

After editing content, run:

```sh
python scripts/finalize_site.py
```

The ready-to-serve `dist/` is self-contained. It includes the supplied logo,
updated portrait, the Jaramana film and the Blender juice-can and car projects.
The personal video and the cancelled extra Max-model previews are excluded.
Selected film clips and original-size zoom files match the final local website.
The raw CAD/Max/Blender working projects and unused footage are separate source
archives; they are not required to run this website.

## GitHub Pages

The Pages workflow builds `_site/` from `dist/`. It adjusts URL paths for this
repository, without recompressing any media. The original `dist/` is preserved.

In the repository's **Settings → Pages**, select **GitHub Actions** as the source.
Push to `main`, or run **Publish original-quality portfolio** from the Actions tab.
The deployment step reports the public address when publication succeeds.

To prepare the same build locally:

```sh
python scripts/build_github_pages.py --base-path /portfolio/
```

If this repository is renamed or moved, use its new Pages path. For a custom
domain at the web root, use `/` instead. Never replace original `dist/` media with
compressed publication experiments.

## حفظ النسخة وتعديلها

هذا المجلد يحتوي الموقع النهائي كاملاً بالعربية والإنكليزية، مع الصور والفيديوهات
بنفس جودة النسخة المحلية النهائية، دون ضغط إضافي. عدّل النصوص في
`dist/content.json`، ثم شغّل أمر تحديث الصفحات أعلاه. لتغيير الصور، أضفها داخل
`dist/media/` وعدّل مسارها في بيانات المشروع المناسب.

لتنزيل نسخة محفوظة لاحقاً من GitHub: **Code → Download ZIP**، ثم فكّ الملف كاملاً.
للتشغيل المحلي تحتاج Python 3 وتشغّل أمر المعاينة أعلاه. رفع التعديلات إلى `main`
يشغّل النشر بعد تفعيل GitHub Pages. لا تحتاج الصور والفيديوهات إلى ضغط جديد.

## Credits and rights

Portfolio content and branding: Muhammed Niraby. Project-specific roles and
collaboration credits are recorded in the project descriptions. Typeface licences
are included beside the font files. No general licence to reuse project media is
granted by this repository.
