---
title: HTTP 请求与响应基础
summary: 理解 HTTP 消息结构、常用方法、状态码与无状态性。
category: 前后端/计算机网络/HTTP/HTTPS
tags: [HTTP, 网络, API]
status: not_started
difficulty: beginner
---

# HTTP 请求与响应基础

## 请求与响应

HTTP 是应用层协议。客户端发送请求，服务端返回响应。请求通常包含方法、目标路径、请求头和可选请求体；响应包含状态码、响应头和可选响应体。

```http
GET /api/notes/42 HTTP/1.1
Host: localhost:8000
Accept: application/json
```

常用方法：GET 读取资源；POST 常用于创建或触发处理；PUT 通常用于替换目标资源的表示；PATCH 用于部分修改；DELETE 请求删除资源。具体语义仍以接口契约为准。

## 状态码

- `2xx`：请求成功，例如 200 和 201。
- `3xx`：重定向或缓存协商，例如 304。
- `4xx`：客户端请求存在问题，例如 400、401、403、404。
- `5xx`：服务端处理失败，例如 500 和 503。

HTTP 本身是无状态协议，服务端不会仅凭协议自动记住之前的请求；应用可以通过 Cookie、会话或令牌维护所需状态。HTTPS 在 HTTP 与传输层之间使用 TLS，提供加密和服务器身份验证等能力。

## 练习

使用浏览器开发者工具查看一次请求的方法、状态码、Content-Type 和响应时间。比较 401 与 403 的含义，并想一想 GET 请求为什么应避免产生业务上的副作用。
