import json
from pathlib import Path
from pleiades_sidebar.pleiades import PleiadesDataset
from slugify import slugify

hits_file = Path("~/scratch/hits.txt").expanduser().resolve()

items = list()
pds = PleiadesDataset()

with hits_file.open() as f:
    for line in f:
        sidebar_json_path = Path(line.strip())
        pid = sidebar_json_path.stem
        puri = f"https://pleiades.stoa.org/places/{pid}"
        place = pds.get(puri)
        title = place["title"]
        items.append((slugify(title, separator=""), title, puri))
del f

# Sort by title
items.sort(key=lambda x: x[0].lower())

# Output as unordered HTML list
print("<ul>")
for slug, title, uri in items:
    print(f'  <li>{title}: <a href="{uri}">{uri}</a></li>')
print("</ul>")
