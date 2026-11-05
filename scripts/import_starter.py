"""Import bundled notes without overwriting any existing user documents."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.database import Base, engine, SessionLocal
from app.models import Note
from app.seed import seed
from app.main import ImportItem, ImportRequest, import_notes, parse_import
from app.services import categories, path_for

Base.metadata.create_all(engine)
with SessionLocal() as db:
    seed(db)
    cats = {c.id: c for c in categories(db)}
    existing = {(n.title, path_for(cats.get(n.category_id), cats)) for n in db.query(Note)}
    items = []
    for path in sorted((ROOT / 'materials').rglob('*.md')):
        item = ImportItem(filename=path.name, text=path.read_text(encoding='utf-8'))
        meta, _ = parse_import(item)
        if (meta.get('title'), meta.get('category')) not in existing:
            items.append(item)
    result = import_notes(ImportRequest(items=items), db)
    print(f"Imported {result['imported']} starter documents; skipped {len(list((ROOT / 'materials').rglob('*.md'))) - len(items)} already present.")
