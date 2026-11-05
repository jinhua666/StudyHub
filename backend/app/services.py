from sqlalchemy import select, delete
from .models import Category, Note, Tag, note_tags

def categories(db): return db.query(Category).order_by(Category.sort_order, Category.id).all()
def descendants(db, category_id):
    children = {}
    for c in categories(db): children.setdefault(c.parent_id, []).append(c.id)
    result, stack = [], [category_id]
    while stack:
        item = stack.pop()
        if item in result: continue
        result.append(item); stack.extend(children.get(item, []))
    return result
def path_for(c, all_categories):
    names, seen = [], set()
    while c and c.id not in seen:
        seen.add(c.id); names.append(c.name); c = all_categories.get(c.parent_id)
    return '/'.join(reversed(names))
def category_dict(c, cats, counts):
    return {'id':c.id,'name':c.name,'parent_id':c.parent_id,'sort_order':c.sort_order,'is_system':c.is_system,'path':path_for(c,cats),'note_count':counts.get(c.id,0)}
def note_dict(db,n, cats=None):
    cats = cats or {c.id:c for c in categories(db)}
    tags = list(db.scalars(select(Tag.name).join(note_tags,Tag.id==note_tags.c.tag_id).where(note_tags.c.note_id==n.id)))
    result = {k:getattr(n,k) for k in ('id','title','summary','content_md','category_id','status','difficulty','is_favorite','source_url','created_at','updated_at','last_viewed_at')}
    result.update(tags=tags, category_path=path_for(cats.get(n.category_id),cats)); return result
def set_tags(db,n,names):
    db.execute(delete(note_tags).where(note_tags.c.note_id==n.id))
    for name in dict.fromkeys(x.strip() for x in names if x.strip()):
        tag = db.query(Tag).filter_by(name=name).first()
        if not tag: tag=Tag(name=name); db.add(tag); db.flush()
        db.execute(note_tags.insert().values(note_id=n.id,tag_id=tag.id))
