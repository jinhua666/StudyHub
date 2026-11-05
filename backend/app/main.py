from contextlib import asynccontextmanager, closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import io, re, shutil, sqlite3, tempfile, uuid, zipfile
import sys
import yaml
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session
from .database import Base, engine, get_db, DATA_DIR
from .models import Category, Note, Tag, Attachment, note_tags
from .seed import seed
from .services import categories, descendants, category_dict, note_dict, path_for, set_tags

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    from .database import SessionLocal
    with SessionLocal() as db: seed(db)
    yield
app = FastAPI(title='StudyHub API', version='1.0', lifespan=lifespan)

class CategoryInput(BaseModel):
    name: str = Field(min_length=1,max_length=150)
    parent_id: Optional[int] = None
    sort_order: int = 0
class NoteInput(BaseModel):
    title: str = Field(min_length=1,max_length=300)
    summary: str = ''
    content_md: str = ''
    category_id: int
    status: str = 'not_started'
    difficulty: str = 'beginner'
    is_favorite: bool = False
    source_url: str = ''
    tags: list[str] = []

def need(db, model, id):
    obj=db.get(model,id)
    if not obj: raise HTTPException(404,'记录不存在')
    return obj
def validate_note(db, data):
    need(db,Category,data.category_id)
    if not data.title.strip(): raise HTTPException(400,'标题不能为空')
    if data.status not in ('not_started','learning','mastered') or data.difficulty not in ('beginner','intermediate','advanced'): raise HTTPException(400,'状态或难度无效')
def save_note(db, data, n=None, commit=True):
    validate_note(db,data)
    if n is None: n=Note(); db.add(n)
    for key,value in data.model_dump(exclude={'tags'}).items(): setattr(n,key,value)
    n.updated_at=datetime.now(timezone.utc); db.flush(); set_tags(db,n,data.tags)
    if commit: db.commit()
    return note_dict(db,n)

class CategoryMove(BaseModel):
    target_id: int
    position: str = 'inside'

@app.post('/api/categories/{id}/move')
def move_category(id:int, data:CategoryMove, db:Session=Depends(get_db)):
    item=need(db,Category,id); target=need(db,Category,data.target_id)
    if data.position not in ('before','after','inside'): raise HTTPException(400,'无效的移动位置')
    if id==target.id: return {'ok':True}
    parent=target.id if data.position=='inside' else target.parent_id
    if item.is_system and parent is not None: raise HTTPException(400,'系统板块不能移动到其他分类')
    if not item.is_system and parent is None: raise HTTPException(400,'分类必须属于一个板块')
    if parent in descendants(db,id): raise HTTPException(400,'不能移动到自身或子分类')
    siblings=db.query(Category).filter(Category.parent_id==parent,Category.id!=id).order_by(Category.sort_order,Category.id).all()
    index=len(siblings) if data.position=='inside' else next(i for i,c in enumerate(siblings) if c.id==target.id)+(data.position=='after')
    siblings.insert(index,item); item.parent_id=parent
    for i,c in enumerate(siblings): c.sort_order=i
    db.commit(); return {'ok':True}

@app.get('/api/categories')
def list_categories(db: Session=Depends(get_db)):
    items=categories(db); mapping={c.id:c for c in items}
    counts=dict(db.query(Note.category_id,func.count(Note.id)).group_by(Note.category_id).all())
    return [category_dict(c,mapping,counts) for c in items]
@app.post('/api/categories')
def create_category(data: CategoryInput, db: Session=Depends(get_db)):
    if data.parent_id is None: raise HTTPException(400,'请在现有板块下创建分类')
    need(db,Category,data.parent_id)
    if not data.name.strip(): raise HTTPException(400,'名称不能为空')
    c=Category(**data.model_dump()); c.name=c.name.strip(); db.add(c); db.commit(); return {'id':c.id}
@app.put('/api/categories/{id}')
def update_category(id:int,data:CategoryInput,db:Session=Depends(get_db)):
    c=need(db,Category,id)
    if c.is_system and data.parent_id is not None: raise HTTPException(400,'系统板块不能移动')
    if not c.is_system and data.parent_id is None: raise HTTPException(400,'分类必须属于一个板块')
    if data.parent_id in descendants(db,id): raise HTTPException(400,'不能移动到自身或子分类')
    if data.parent_id is not None: need(db,Category,data.parent_id)
    if not data.name.strip(): raise HTTPException(400,'名称不能为空')
    c.name=data.name.strip(); c.parent_id=data.parent_id; c.sort_order=data.sort_order; db.commit(); return {'ok':True}
@app.delete('/api/categories/{id}')
def delete_category(id:int,confirm:bool=False,migrate_to:Optional[int]=None,db:Session=Depends(get_db)):
    c=need(db,Category,id)
    if c.is_system: raise HTTPException(400,'默认板块不能删除')
    ids=descendants(db,id)
    if migrate_to is not None:
        need(db,Category,migrate_to)
        if migrate_to in ids: raise HTTPException(400,'不能迁移到自身或子分类')
        db.query(Note).filter_by(category_id=id).update({'category_id':migrate_to})
        db.query(Category).filter_by(parent_id=id).update({'parent_id':migrate_to})
        db.delete(c); db.commit(); return {'ok':True}
    if not confirm and (len(ids)>1 or db.query(Note).filter(Note.category_id.in_(ids)).count()): raise HTTPException(409,'分类不为空，确认删除其全部子分类和文档？')
    # SQLite cascades documents and their attachment records; remove attachment files too.
    attachments=db.query(Attachment).join(Note).filter(Note.category_id.in_(ids)).all()
    files=[DATA_DIR/'attachments'/a.stored_name for a in attachments]
    db.delete(c); db.commit()
    for f in files: f.unlink(missing_ok=True)
    return {'ok':True}

@app.get('/api/notes')
def list_notes(q:str='',category_id:Optional[int]=None,recursive:bool=False,status:str='',favorite:bool=False,recent:bool=False,tag:str='',db:Session=Depends(get_db)):
    query=db.query(Note)
    if category_id: query=query.filter(Note.category_id.in_(descendants(db,category_id) if recursive else [category_id]))
    if status: query=query.filter(Note.status==status)
    if favorite: query=query.filter(Note.is_favorite.is_(True))
    if recent: query=query.filter(Note.last_viewed_at.is_not(None))
    if tag: query=query.filter(Note.id.in_(select(note_tags.c.note_id).join(Tag).where(Tag.name==tag)))
    if q:
        term='%'+q.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%'
        all_cats={c.id:c for c in categories(db)}
        matching_cats=[c.id for c in all_cats.values() if q.casefold() in path_for(c,all_cats).casefold()]
        query=query.filter(or_(Note.title.ilike(term,escape='\\'),Note.summary.ilike(term,escape='\\'),Note.content_md.ilike(term,escape='\\'),Note.category_id.in_(matching_cats),Note.id.in_(select(note_tags.c.note_id).join(Tag).where(Tag.name.ilike(term,escape='\\')))))
    query=query.order_by(Note.last_viewed_at.desc() if recent else Note.updated_at.desc())
    cats={c.id:c for c in categories(db)}
    return [note_dict(db,n,cats) for n in query.all()]
@app.post('/api/notes')
def create_note(data:NoteInput,db:Session=Depends(get_db)): return save_note(db,data)
@app.get('/api/notes/{id}')
def get_note(id:int,view:bool=False,db:Session=Depends(get_db)):
    n=need(db,Note,id)
    if view:
        db.execute(update(Note).where(Note.id==id).values(last_viewed_at=datetime.now(timezone.utc),updated_at=Note.updated_at))
        db.commit(); db.refresh(n)
    return note_dict(db,n)
@app.put('/api/notes/{id}')
def update_note(id:int,data:NoteInput,db:Session=Depends(get_db)): return save_note(db,data,need(db,Note,id))
@app.delete('/api/notes/{id}')
def delete_note(id:int,db:Session=Depends(get_db)):
    n=need(db,Note,id); files=[DATA_DIR/'attachments'/a.stored_name for a in db.query(Attachment).filter_by(note_id=id)]
    db.delete(n); db.commit()
    for f in files: f.unlink(missing_ok=True)
    return {'ok':True}
@app.get('/api/tags')
def tags(db:Session=Depends(get_db)): return list(db.scalars(select(Tag.name).join(note_tags).distinct().order_by(Tag.name)))

def markdown(n,db):
    d=note_dict(db,n); meta={k:d[k] for k in ('id','title','summary','tags','status','difficulty','source_url')}; meta['category']=d['category_path']
    return '---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---\n\n'+n.content_md
@app.get('/api/export')
def export_notes(category_id:Optional[int]=None,note_id:Optional[int]=None,db:Session=Depends(get_db)):
    query=db.query(Note)
    if note_id: query=query.filter(Note.id==note_id)
    if category_id: query=query.filter(Note.category_id.in_(descendants(db,category_id)))
    notes=query.all()
    if note_id:
        if not notes: raise HTTPException(404,'文档不存在')
        return StreamingResponse(iter([markdown(notes[0],db).encode('utf-8')]),media_type='text/markdown',headers={'Content-Disposition':f'attachment; filename="note-{note_id}.md"'})
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n in notes:
            d=note_dict(db,n); safe=lambda s: re.sub(r'[\\/:*?"<>|]+','_',s).strip('. ') or 'untitled'
            folder='/'.join(safe(x) for x in d['category_path'].split('/')); z.writestr(f'{folder}/{safe(n.title)}-{n.id}.md',markdown(n,db))
            for a in db.query(Attachment).filter_by(note_id=n.id):
                f=DATA_DIR/'attachments'/a.stored_name
                if f.is_file(): z.write(f,f'attachments/{a.stored_name}')
    out.seek(0); return StreamingResponse(out,media_type='application/zip',headers={'Content-Disposition':'attachment; filename="studyhub-export.zip"'})

class ImportItem(BaseModel):
    filename:str
    text:str
class ImportRequest(BaseModel):
    items:list[ImportItem]
    create_categories:bool=False
    duplicate:str='skip'
    default_category_id:Optional[int]=None
def parse_import(item):
    text=item.text.lstrip('\ufeff'); meta={}
    if text.startswith('---\n') or text.startswith('---\r\n'):
        parts=re.split(r'^---\s*$',text,maxsplit=2,flags=re.M)
        if len(parts)>=3:
            try: meta=yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError: raise HTTPException(400,f'{item.filename}: YAML 格式错误')
            text=parts[2].lstrip('\r\n')
    if not isinstance(meta,dict): raise HTTPException(400,f'{item.filename}: Front Matter 必须是映射')
    return meta,text
@app.post('/api/import/preview')
def preview_import(data:ImportRequest,db:Session=Depends(get_db)):
    result=[]; cats={c.id:c for c in categories(db)}; paths={path_for(c,cats):c.id for c in cats.values()}
    for item in data.items:
        meta,body=parse_import(item); title=str(meta.get('title') or Path(item.filename).stem); path=str(meta.get('category') or '')
        existing=db.get(Note,meta.get('id')) if isinstance(meta.get('id'),int) else None
        result.append({'filename':item.filename,'title':title,'category':path,'category_exists':path in paths or (not path and bool(data.default_category_id)),'existing_id':existing.id if existing else None})
    return result
@app.post('/api/import')
def import_notes(data:ImportRequest,db:Session=Depends(get_db)):
    if data.duplicate not in ('skip','update'): raise HTTPException(400,'重复处理方式无效')
    imported=skipped=0
    for item in data.items:
        meta,body=parse_import(item); path=str(meta.get('category') or ''); parent=None
        if path:
            # Prefer an exact full path, including categories whose names contain '/'.
            all_cats={c.id:c for c in categories(db)}
            exact=next((c for c in all_cats.values() if path_for(c,all_cats)==path),None)
            for part in ([] if exact else path.split('/')):
                c=db.query(Category).filter_by(parent_id=parent,name=part).first()
                if not c:
                    if not data.create_categories or parent is None: raise HTTPException(400,f'分类不存在：{path}')
                    c=Category(name=part,parent_id=parent,sort_order=9999); db.add(c); db.flush()
                parent=c.id
            if exact: parent=exact.id
        else: parent=data.default_category_id
        existing=db.get(Note,meta.get('id')) if isinstance(meta.get('id'),int) else None
        if existing and data.duplicate=='skip': skipped+=1; continue
        tags=meta.get('tags') or []
        if not isinstance(tags,list): raise HTTPException(400,f'{item.filename}: tags 必须为数组')
        if parent is None: raise HTTPException(400,f'{item.filename}: 请选择分类')
        try: obj=NoteInput(title=str(meta.get('title') or Path(item.filename).stem),summary=str(meta.get('summary') or ''),content_md=body,category_id=parent,status=meta.get('status','not_started'),difficulty=meta.get('difficulty','beginner'),source_url=str(meta.get('source_url') or ''),tags=tags)
        except ValueError: raise HTTPException(400,f'{item.filename}: 文档字段无效')
        save_note(db,obj,existing,commit=False); imported+=1
    db.commit()
    return {'imported':imported,'skipped':skipped}

ALLOWED={'.pdf','.png','.jpg','.jpeg','.webp','.txt','.csv','.py','.ipynb'}
@app.get('/api/notes/{id}/attachments')
def list_attachments(id:int,db:Session=Depends(get_db)):
    need(db,Note,id)
    return [{'id':a.id,'name':a.original_name,'size':a.file_size,'mime_type':a.mime_type} for a in db.query(Attachment).filter_by(note_id=id)]
@app.post('/api/notes/{id}/attachments')
async def upload_attachment(id:int,file:UploadFile=File(...),db:Session=Depends(get_db)):
    need(db,Note,id); name=Path(file.filename or '').name; ext=Path(name).suffix.lower()
    if not name or ext not in ALLOWED or len(name)>200: raise HTTPException(400,'不支持的文件名或类型')
    content=await file.read(20*1024*1024+1)
    if len(content)>20*1024*1024: raise HTTPException(400,'附件不能超过 20 MB')
    import mimetypes
    stored=uuid.uuid4().hex+ext; (DATA_DIR/'attachments'/stored).write_bytes(content)
    a=Attachment(note_id=id,original_name=name,stored_name=stored,mime_type=mimetypes.guess_type(name)[0] or 'application/octet-stream',file_size=len(content),file_path=stored)
    db.add(a); db.commit(); return {'id':a.id,'name':name}
@app.get('/api/attachments/{id}')
def get_attachment(id:int,db:Session=Depends(get_db)):
    a=need(db,Attachment,id); file=DATA_DIR/'attachments'/a.stored_name
    if not file.is_file(): raise HTTPException(404,'附件文件不存在')
    return FileResponse(file,media_type=a.mime_type,filename=a.original_name,content_disposition_type='inline' if a.mime_type.startswith('image/') or a.mime_type=='application/pdf' else 'attachment',headers={'X-Content-Type-Options':'nosniff'})
@app.delete('/api/attachments/{id}')
def delete_attachment(id:int,db:Session=Depends(get_db)):
    a=need(db,Attachment,id); file=DATA_DIR/'attachments'/a.stored_name; db.delete(a); db.commit(); file.unlink(missing_ok=True); return {'ok':True}
@app.get('/api/backup')
def backup():
    out=io.BytesIO()
    with tempfile.TemporaryDirectory(dir=DATA_DIR) as tmp:
        snapshot=Path(tmp)/'studyhub.db'
        with closing(sqlite3.connect(DATA_DIR/'studyhub.db')) as src, closing(sqlite3.connect(snapshot)) as dest: src.backup(dest)
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            z.write(snapshot,'studyhub.db')
            for f in (DATA_DIR/'attachments').iterdir():
                if f.is_file(): z.write(f,'attachments/'+f.name)
    out.seek(0); return StreamingResponse(out,media_type='application/zip',headers={'Content-Disposition':'attachment; filename="studyhub-backup.zip"'})
@app.post('/api/restore')
async def restore(file:UploadFile=File(...),confirm:bool=False):
    if not confirm: raise HTTPException(400,'必须确认覆盖当前数据')
    data=await file.read(200*1024*1024+1)
    if len(data)>200*1024*1024: raise HTTPException(400,'备份过大')
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names=z.namelist()
            if 'studyhub.db' not in names or any(not (n=='studyhub.db' or (n.startswith('attachments/') and len(Path(n).parts)==2)) for n in names): raise ValueError()
            if sum(i.file_size for i in z.infolist())>500*1024*1024: raise ValueError()
            with tempfile.TemporaryDirectory(dir=DATA_DIR) as tmp:
                candidate=Path(tmp)/'studyhub.db'; candidate.write_bytes(z.read('studyhub.db'))
                with closing(sqlite3.connect(candidate)) as conn:
                    if conn.execute('PRAGMA integrity_check').fetchone()[0]!='ok': raise ValueError()
                    tables={r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                    if not {'categories','notes','tags','note_tags','attachments'} <= tables: raise ValueError()
                # Preserve a safety copy before replacing current data.
                stamp=datetime.now().strftime('%Y%m%d-%H%M%S'); safety=DATA_DIR/'backups'/('before-restore-'+stamp+'.zip')
                with zipfile.ZipFile(safety,'w',zipfile.ZIP_DEFLATED) as old:
                    with closing(sqlite3.connect(DATA_DIR/'studyhub.db')) as src, closing(sqlite3.connect(Path(tmp)/'old.db')) as dst: src.backup(dst)
                    old.write(Path(tmp)/'old.db','studyhub.db')
                    for f in (DATA_DIR/'attachments').iterdir():
                        if f.is_file(): old.write(f,'attachments/'+f.name)
                engine.dispose(); shutil.copy2(candidate,DATA_DIR/'studyhub.db')
                for f in (DATA_DIR/'attachments').iterdir():
                    if f.is_file(): f.unlink()
                for name in names:
                    if name.startswith('attachments/') and not name.endswith('/'):
                        (DATA_DIR/'attachments'/Path(name).name).write_bytes(z.read(name))
    except (zipfile.BadZipFile,ValueError,sqlite3.DatabaseError,KeyError): raise HTTPException(400,'备份文件无效')
    return {'ok':True,'safety_backup':safety.name}

dist=(Path(sys._MEIPASS) if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[2])/'frontend'/'dist'
if dist.exists():
    app.mount('/assets',StaticFiles(directory=dist/'assets'),name='assets')
    @app.get('/{path:path}',include_in_schema=False)
    def frontend(path:str):
        candidate=(dist/path).resolve()
        if candidate.is_file() and dist.resolve() in candidate.parents: return FileResponse(candidate)
        return FileResponse(dist/'index.html')
