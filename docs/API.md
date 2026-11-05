# 本地 API

服务默认绑定 `127.0.0.1:8000`，交互式 OpenAPI 文档见 <http://127.0.0.1:8000/docs>。API 没有登录认证，勿将服务绑定到公网。

- `GET/POST /api/categories`：获取扁平分类树、创建子分类。
- `PUT/DELETE /api/categories/{id}`：重命名、移动、排序或删除；删除非空分类需要 `confirm=true`，也可用 `migrate_to` 指定非子孙目标分类，迁移直属文档和子分类。
- `POST /api/categories/{id}/move`：按目标分类与 `inside`、`before`、`after` 位置移动及排序。
- `GET/POST /api/notes`：查询和创建。查询参数包括 `q`, `category_id`, `recursive`, `status`, `favorite`, `recent`, `tag`。
- `GET/PUT/DELETE /api/notes/{id}`：读取、更新和删除。读取时 `view=true` 更新最近阅读时间。
- `GET /api/tags`：使用中的标签。
- `POST /api/import/preview` 和 `POST /api/import`：请求体为 `items: [{filename, text}]`，可选 `default_category_id`, `create_categories`, `duplicate`（`skip` 或 `update`）。
- `GET /api/export`：无参数导出全部 ZIP；`category_id` 导出分类子树；`note_id` 导出单篇 Markdown。
- `GET/POST /api/notes/{id}/attachments`、`GET/DELETE /api/attachments/{id}`：附件管理。
- `GET /api/backup` 下载完整备份；`POST /api/restore?confirm=true` 上传 ZIP 恢复。恢复前自动在数据目录的 backups 中保存一份当前数据。

创建和更新文档的 JSON 字段包括 `title`, `summary`, `content_md`, `category_id`, `status`, `difficulty`, `is_favorite`, `source_url`, `tags`。字段详情和响应格式以 OpenAPI 为准。
