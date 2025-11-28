## 目标与范围
- 搭建婚礼 SaaS 管理后台前端项目，支持登录、RBAC、CRM 线索、项目中心、报价/审批等核心模块的 MVP。
- 接口基于本机 FastAPI：OpenAPI `http://127.0.0.1:8000/openapi.json`，请求基址 `http://127.0.0.1:8000/api/v1/`（后端定义见 web/wedding-api/app/config.py:7 与 web/wedding-api/app/api/v1/api.py:5-12）。

## 技术栈
- 前端：Vue 3 + Vite + TypeScript
- UI：Ant Design Vue（遵循“Ant Design Pro”交互范式）
- 路由与状态：Vue Router + Pinia
- HTTP：Axios（统一响应封装与拦截器）
- OpenAPI 类型/客户端：openapi-typescript +（可选）orval 或 openapi-fetch 生成 API 客户端

## 项目结构
- `web/wedding-admin/`
  - `src/main.ts`（应用入口）
  - `src/router/`（动态路由与路由守卫，含 meta.roles）
  - `src/stores/`（Pinia：`auth`、`ui`、`app`）
  - `src/api/`（Axios 实例、OpenAPI 生成的 types/client、模块化接口）
  - `src/pages/`（Dashboard、CRM、Projects、Budget、Approvals、Resources、Finance、Settings）
  - `src/components/`（`SensitiveText`、`QuotationBuilder` 等）
  - `src/utils/`（权限工具、格式化、金额精度）
  - `env`：`VITE_API_BASE=http://127.0.0.1:8000/api/v1/`、`VITE_OPENAPI_URL=http://127.0.0.1:8000/openapi.json`

## 鉴权与 RBAC
- 登录：`POST /auth/login`（web/wedding-api/app/api/v1/api.py:5），保存 `token` 与 `user.role` 至 Pinia + `localStorage`。
- 请求拦截：在 Axios `Authorization: Bearer <token>`，401 自动跳转登录。
- 路由守卫：基于 `route.meta.roles` 与当前 `user.role` 控制访问与菜单显示。
- 字段级权限：前端在展示层根据角色隐藏敏感字段（成本、毛利），与后端控制一致（见 docs/API开发指南.md 与 docs/管理后台设计.md）。

## 全局响应封装
- 统一处理后端响应包装（`code`、`message`、`data`、`timestamp`），错误码映射（如 401、403、1001 撞单等）。
- 失败弹出通知与重试策略；接口失败统一上报。

## OpenAPI 集成
- 通过 `VITE_OPENAPI_URL` 生成 TS 类型：`openapi-typescript` 输出到 `src/api/types/openapi.d.ts`。
- （可选）使用 `orval` 或 `openapi-fetch` 生成强类型客户端，减少手写请求代码。
- 在 CI/本地提供 `yarn openapi:gen` 脚本，变更后可一键更新类型。

## 关键组件
- `SensitiveText`：接入 Pinia 全局 `ui.isPresentationMode`，在演示模式下用 `******` 遮罩金额等敏感字段。
- `QuotationBuilder`：拖拽表格，行排序、实时金额计算、自动保存 Hook（变更后 2s 防抖 或 30s 心跳）。

## 页面与功能
- Dashboard：根据角色展示 KPI/待办/漏斗与预警。
- CRM：
  - 列表与筛选：`GET /leads`（分页、状态、关键词）。
  - 新建线索：`POST /leads`（创建前撞单检测，返回 `code=1001` 提示）。
  - 公海捞取：`PUT /leads/{id}/claim`。
- Projects（核心作业区）：
  - 列表：按阶段筛选。
  - 详情：Tab（概览/方案/预算/任务/人员/文件）。
  - 预算：`GET /projects/{id}/budget`，批量更新 `PUT /projects/{id}/budget/batch-update`，前端遵守字段级权限。
- Approvals：
  - 发起：`POST /approvals`（折扣/付款等）。
  - 审批决策：`PATCH /approvals/{id}/audit`。
- Resources：人员/场地/物料库，遵循角色可见性与操作限制。
- Finance：收支流水、请款审批链；策划师只读，财务可操作。
- Settings：账号权限、业务配置、SOP 模板。

## 金额精度与上传
- 金额以“分”为单位或引入 `decimal.js` 保证计算精度。
- 图片上传走通用上传接口后回填 `image_url` 字段。

## 开发与验证
- 启动后端（FastAPI，已在 `web/wedding-api/app/main.py`，OpenAPI 默认 `/openapi.json`）。
- 启动前端：本地 `.env` 指向 `http://127.0.0.1:8000/api/v1/`。
- 验证流程：登录 → 路由守卫 → CRM 列表与创建 → 公海捞取 → 项目详情与预算编辑 → 审批发起/决策。
- 添加基本单元测试与 E2E 冒烟用例（登录与权限、预算遮罩、撞单提示）。

## 迭代节奏（MVP → 增强）
- MVP：Dashboard（简版）、CRM、Projects（概览/预算）、Approvals。
- v1.5：Resources/Finance/Settings 完整版、SOP 流程、移动端预览模态。

## 交付物
- 可运行的 `web/wedding-admin` 前端项目、OpenAPI 类型生成脚本、基础测试与使用说明（环境变量、启动命令）。
