"""Integration checks. Set STUDYHUB_DATA_DIR to a disposable directory before running."""
import asyncio
import io
from fastapi import HTTPException, UploadFile
from app.database import Base, engine, SessionLocal
from app.models import Category, Note
from app.seed import seed
from app.main import (CategoryInput, CategoryMove, NoteInput, ImportItem, ImportRequest,
                      backup, create_category, create_note, delete_category, import_notes,
                      list_notes, move_category, restore, get_note)

Base.metadata.create_all(engine)
with SessionLocal() as db:
    seed(db)
    root=db.query(Category).filter_by(parent_id=None).first()
    a=create_category(CategoryInput(name='测试 A',parent_id=root.id),db)['id']
    b=create_category(CategoryInput(name='测试 B',parent_id=root.id),db)['id']
    child=create_category(CategoryInput(name='子分类',parent_id=a),db)['id']
    note=create_note(NoteInput(title='迁移测试',category_id=a,content_md='中文检索关键词'),db)
    old_update=note['updated_at']
    viewed=get_note(note['id'],view=True,db=db)
    assert viewed['updated_at'].replace(tzinfo=None)==old_update.replace(tzinfo=None) and viewed['last_viewed_at']
    assert any(n['id']==note['id'] for n in list_notes(q='中文检索',db=db))
    try:
        move_category(a,CategoryMove(target_id=child,position='inside'),db)
        raise AssertionError('cycle accepted')
    except HTTPException as exc: assert exc.status_code==400
    move_category(b,CategoryMove(target_id=a,position='before'),db)
    assert db.get(Category,b).sort_order < db.get(Category,a).sort_order
    delete_category(a,migrate_to=b,db=db)
    db.expire_all()
    assert db.get(Note,note['id']).category_id==b and db.get(Category,child).parent_id==b
    before=db.query(Note).count()
    items=[ImportItem(filename='ok.md',text=f'---\ntitle: 事务测试\ncategory: {root.name}\n---\n内容'), ImportItem(filename='bad.md',text='---\ntitle: 错误\ncategory: 不存在\n---\n内容')]
    try:
        import_notes(ImportRequest(items=items),db)
        raise AssertionError('invalid import accepted')
    except HTTPException: db.rollback()
    assert db.query(Note).count()==before

async def verify_backup():
    response=backup()
    chunks=[]
    async for chunk in response.body_iterator: chunks.append(chunk)
    result=await restore(UploadFile(filename='backup.zip',file=io.BytesIO(b''.join(chunks))),confirm=True)
    assert result['ok']
asyncio.run(verify_backup())
print('OK: search, category cycle/sort/migration, atomic import, backup/restore')
