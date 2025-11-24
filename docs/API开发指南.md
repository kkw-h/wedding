这份文档是按照 **RESTful 标准** 编写的 API 接口文档。它采用了 **OpenAPI (Swagger) 风格** 的描述方式，特别优化了**数据结构示例 (JSON Payload)** 和 **TypeScript 类型定义**，以便编程 AI（如 Copilot, Cursor）能够直接读取并生成 Controller 和 DTO 代码。

---

# 婚礼 SaaS 管理系统 API 开发文档 (v1.0)

**版本:** 1.0.0
**基础路径 (Base URL):** `https://api.wed-saas.com/v1`
**认证方式:** Bearer Token (JWT)

---

## 1. 全局规范 (Global Standards)

### 1.1 统一响应结构 (Response Wrapper)
所有接口（无论成功或失败）均返回以下 JSON 结构：

```json
{
  "code": 200,          // 业务状态码：200 成功, 非 200 失败
  "message": "success", // 提示信息
  "data": { ... },      // 业务数据 payload
  "timestamp": 1698723000
}
```

### 1.2 常用业务状态码 (Business Codes)
| Code | Description | Solution |
| :--- | :--- | :--- |
| `200` | 成功 | - |
| `401` | 未授权 | Token 过期或无效，请重新登录 |
| `403` | 权限不足 | 当前角色无权操作（如策划师尝试查看毛利） |
| `1001` | 撞单警告 | 该客户手机号已被其他策划师录入 |
| `1002` | 状态锁定 | 审批通过后，报价单不可修改 |

---

## 2. 核心接口模块 (Core Endpoints)

### 🔐 模块 A：认证与用户 (Auth & User)

#### A1. 用户登录
*   **POST** `/auth/login`
*   **Request Body:**
    ```json
    {
      "username": "planner_zhang",
      "password": "hashed_password_string"
    }
    ```
*   **Response:**
    ```json
    {
      "token": "eyJhbGciOiJIUzI1...",
      "user": {
        "id": "u_123",
        "name": "张策划",
        "role": "PLANNER", // 关键字段：前端据此判断是否隐藏成本
        "team_id": "t_001"
      }
    }
    ```

---

### 📢 模块 B：线索与公海 (CRM Leads)

#### B1. 获取线索列表 (含筛选)
*   **GET** `/leads`
*   **Query Params:**
    *   `page`: 1
    *   `size`: 20
    *   `status`: `NEW` | `CONTACTING` | `PUBLIC_POOL` (公海)
    *   `keyword`: "1380000" (搜索手机或姓名)
*   **Response:**
    ```json
    {
      "total": 45,
      "list": [
        {
          "id": "lead_999",
          "name": "王小姐",
          "phone": "138****1234", // 列表页默认脱敏
          "wedding_date": "2025-10-01",
          "status": "NEW",
          "owner_name": "张策划"
        }
      ]
    }
    ```

#### B2. 新建线索 (自动查重)
*   **POST** `/leads`
*   **Logic:** 后端需先检查 `phone` 是否存在。如果存在且 `owner_id` 不为空，返回 `Code 1001`。
*   **Request Body:**
    ```json
    {
      "name": "李先生",
      "phone": "13900001111",
      "source": "XIAOHONGSHU",
      "wedding_date": "2025-05-20"
    }
    ```

#### B3. 从公海池捞取线索
*   **PUT** `/leads/{id}/claim`
*   **Description:** 将线索的 `owner_id` 设为当前用户，状态改为 `CONTACTING`。

---

### 💒 模块 C：项目与详情 (Projects)

#### C1. 获取项目详情 (聚合数据)
*   **GET** `/projects/{id}`
*   **Response:**
    ```json
    {
      "id": "proj_888",
      "base_info": {
        "groom": "张伟",
        "bride": "王芳",
        "hotel": "希尔顿大宴会厅",
        "wedding_date": "2025-10-01"
      },
      "progress": {
        "current_stage": "DESIGNING",
        "percent": 45
      },
      "stats": {
        "total_price": 85000,
        "paid_amount": 30000
      }
    }
    ```

---

### 💰 模块 D：报价与方案 (Quotation & Budget)

> ⚠️ **特别注意：字段级权限控制 (Field-level Security)**
> *   若 `user.role === 'PLANNER'`，返回数据中 `cost_price` (成本) 和 `margin` (毛利) 必须为 `null` 或 `0`。
> *   若 `user.role === 'ADMIN'`，返回真实数据。

#### D1. 获取报价单明细
*   **GET** `/projects/{id}/budget`
*   **Response:**
    ```json
    {
      "project_id": "proj_888",
      "version": "v2.0",
      "categories": [
        {
          "name": "仪式区布置",
          "items": [
            {
              "id": "item_001",
              "name": "主舞台背景",
              "specs": "8m*4m",
              "quantity": 1,
              "unit_price": 5000, // 对客价
              "cost_price": 2000, // 成本价 (Admin可见)
              "image_url": "https://oss..."
            }
          ]
        }
      ]
    }
    ```

#### D2. 批量更新报价项 (自动保存)
*   **PUT** `/projects/{id}/budget/batch-update`
*   **Request Body:**
    ```json
    {
      "items": [
        { "id": "item_001", "quantity": 2, "unit_price": 4800 },
        { "id": "item_002", "is_deleted": true }
      ]
    }
    ```

---

### ✅ 模块 E：审批流 (Approvals)

#### E1. 发起折扣申请
*   **POST** `/approvals`
*   **Request Body:**
    ```json
    {
      "project_id": "proj_888",
      "type": "DISCOUNT",
      "content": {
        "original_price": 100000,
        "target_price": 95000,
        "reason": "老客户转介绍，申请95折"
      }
    }
    ```

#### E2. 审批决策
*   **PATCH** `/approvals/{id}/audit`
*   **Request Body:**
    ```json
    {
      "status": "APPROVED", // or REJECTED
      "comment": "同意，但下不为例"
    }
    ```

---

## 3. TypeScript 接口定义 (For Frontend/AI)

将此部分复制给 AI，它可以直接生成前端的 Type 文件。

```typescript
// 1. 用户角色枚举
export type UserRole = 'ADMIN' | 'MANAGER' | 'PLANNER' | 'VENDOR';

// 2. 线索状态
export type LeadStatus = 'NEW' | 'CONTACTING' | 'WON' | 'LOST' | 'PUBLIC_POOL';

// 3. 报价单项 (包含权限字段)
export interface BudgetItem {
  id: string;
  category: string;
  name: string;
  specs?: string;
  unit_price: number;      // 销售单价
  quantity: number;
  total_price: number;     // unit_price * quantity
  
  // 敏感字段 (可能为 null)
  cost_price?: number;     
  supplier_id?: string;
  
  // 附件
  image_url?: string;
  remark?: string;
}

// 4. 项目概览
export interface ProjectDetail {
  id: string;
  lead_id: string;
  couple_names: string; // "张伟 & 王芳"
  wedding_date: string; // ISO Date
  stage: 'PREPARING' | 'DESIGNING' | 'EXECUTING' | 'COMPLETED';
  budget_summary: {
    total_quoted: number;
    total_cost?: number; // Admin only
    gross_margin?: number; // Admin only
  };
}
```

---

## 4. 开发注意事项 (Developer Notes)

1.  **金额精度：** 数据库存储金额时请使用 `Decimal(10, 2)`，后端计算时注意浮点数精度问题（建议使用 `decimal.js` 或以“分”为单位存储整数）。
2.  **图片上传：** 涉及图片字段（如 `image_url`），请先调用通用上传接口 `/api/upload` 获取 OSS 地址后，再提交到业务接口。
3.  **演示模式 (Presentation Mode)：** 这是一个**纯前端状态**。API 返回的数据包含真实金额，前端根据 `isPresentationMode` 状态决定是否将金额渲染为 `******`。API 不需要为此设计专门的参数。
4.  **乐观锁 (Optimistic Locking)：** 在更新报价单时，建议带上 `version` 字段，防止多人同时操作导致覆盖。
5.  **权限控制：** 所有 API 都需要检查用户角色，确保只有授权角色才能访问。
6.  **错误处理：** 所有 API 都需要返回一致的错误格式，包含 `code`、`message` 和 `data`（可选）。
7.  **日志记录：** 所有 API 调用都需要记录到日志中，包含请求参数、响应数据、执行时间等。
8. **数据库迁移：** 数据库迁移脚本请使用 `Alembic` 或 `Flask-Migrate` 管理，确保在部署时能够自动应用。
9. **数据修改记录SQLAlchemy-Continuum**： 为了记录所有数据变更，建议使用 `SQLAlchemy-Continuum` 插件。
