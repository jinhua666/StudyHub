"""Run with STUDYHUB_DATA_DIR pointing at a disposable directory."""
from fastapi import HTTPException
from app.database import Base, engine, SessionLocal
from app.main import CategoryInput, NoteInput, list_categories, create_category, update_category, create_note, list_notes, backup
from app.seed import seed
Base.metadata.create_all(engine)
with SessionLocal() as db:
    seed(db)
    cats = list_categories(db)
    root = next(c for c in cats if c['parent_id'] is None)
    category = create_category(CategoryInput(name='测试分类', parent_id=root['id']), db)
    note = create_note(NoteInput(title='注意力机制', category_id=category['id'], content_md='中文关键词', tags=['测试标签']), db)
    assert any(n['id'] == note['id'] for n in list_notes(q='中文关键词', db=db))
    assert any(n['id'] == note['id'] for n in list_notes(tag='测试标签', db=db))
    try:
        update_category(category['id'], CategoryInput(name='测试分类', parent_id=category['id']), db)
        raise AssertionError('cycle was accepted')
    except HTTPException as exc:
        assert exc.status_code == 400
    assert backup().status_code == 200
    print('OK: seed, category, note, Chinese search, tags, cycle prevention, backup')
