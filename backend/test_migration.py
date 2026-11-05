"""Run only with STUDYHUB_DATA_DIR set to a disposable test directory."""
import asyncio, io, os, zipfile
from pathlib import Path
from contextlib import closing
from fastapi import UploadFile
from app.database import Base, engine, DATA_DIR, SessionLocal
from app.models import Attachment, Category
from app.seed import seed
from app.main import NoteInput, create_note, backup, restore

assert os.environ.get('STUDYHUB_DATA_DIR'), 'Use a disposable data directory'
Base.metadata.create_all(engine)
with SessionLocal() as db:
    seed(db)
    category=db.query(Category).first()
    note=create_note(NoteInput(title='迁移测试', category_id=category.id,content_md='公式 $x^2$'),db)
    name='migration-test.png'
    (DATA_DIR/'attachments'/name).write_bytes(b'test image content')
    db.add(Attachment(note_id=note['id'],original_name='test.png',stored_name=name,mime_type='image/png',file_size=18,file_path=name)); db.commit()

async def test():
    response=backup(); data=b''.join([chunk async for chunk in response.body_iterator])
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        assert archive.read('attachments/migration-test.png')==b'test image content'
        assert 'studyhub.db' in archive.namelist()
    (DATA_DIR/'attachments'/'migration-test.png').write_bytes(b'changed')
    result=await restore(UploadFile(filename='test.zip',file=io.BytesIO(data)),confirm=True)
    assert result['ok'] and (DATA_DIR/'attachments'/'migration-test.png').read_bytes()==b'test image content'
    with SessionLocal() as db:
        from app.models import Note
        assert db.query(Note).filter_by(title='迁移测试').one().content_md=='公式 $x^2$'
    print('OK: backup and restore preserve note, formula and attachment')
asyncio.run(test())
