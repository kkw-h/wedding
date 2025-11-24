# 💍 Wedding SaaS Project Context (GEMINI.md)

## 1. Project Overview
This project is a comprehensive SaaS solution for the wedding industry, designed to manage the entire lifecycle of wedding planning from lead acquisition to execution. It consists of three interconnected applications serving different user roles.

### The Ecosystem
1.  **`web-admin` (PC Dashboard):** The "Central Kitchen" for internal management.
    *   **Users:** Admin (Boss), Manager, Planner, Finance.
    *   **Focus:** CRM, Project Management, Resource Scheduling, Financial Auditing, Business Intelligence.
2.  **`mini-app` (Mobile Mini Program):** The "Exquisite Plating" for end customers.
    *   **Users:** Bride & Groom (C-side), Planners (On-site execution).
    *   **Focus:** Visualization, Task Management (Gamified), Payments, Guest Tools (Invitations/Seating).
3.  **`wedding-api` (Backend Service):** The core logic and data hub.
    *   **Focus:** RESTful API, Authentication, RBAC, Data Consistency, Cron Jobs.

---

## 2. Technical Stack & Architecture

### 🖥️ Frontend: Admin Panel (`web-admin`)
*   **Framework:** Vue 3
*   **UI Library:** Ant Design Pro
*   **State Management:** Pinia
*   **Key Features:**
    *   **Presentation Mode:** Global state to mask sensitive data (costs/margins) when showing screens to clients.
    *   **RBAC:** Dynamic menu and route guards based on user roles.

### 📱 Frontend: Mini Program (`mini-app`)
*   **Framework:** Uni-app or Taro (Cross-platform for WeChat/Douyin)
*   **UI Library:** Vant Weapp or TDesign
*   **Key Features:**
    *   **Emotional UI:** High-quality visuals, micro-interactions (confetti, smooth transitions).
    *   **Dual-Role View:** Different tabs for Customers vs. Planners (Work/Execution view).

### ⚙️ Backend: API Service (`wedding-api`)
*   **Language:** Python
*   **Framework:** FastAPI
*   **Database:** PostgreSQL (SQLAlchemy ORM)
*   **Migrations:** Alembic
*   **Auth:** JWT + RBAC Middleware
*   **Key Features:**
    *   **Data Masking Middleware:** Automatically nullifies sensitive fields (cost_price) for non-Admin roles.
    *   **Scheduler:** Cron jobs for Lead Recycling (Public Pool logic).

---

## 3. Key Business Logic

### 🔐 Role-Based Access Control (RBAC)
| Role | Scope & Permissions |
| :--- | :--- |
| **ADMIN** | Full access. Sees all costs, profits, and global stats. |
| **MANAGER** | Team management. Approves discounts/refunds. Access to team leads. |
| **PLANNER** | Operational access. Only sees own leads/projects. **Cost data is masked.** |
| **FINANCE** | Financial records only. Can process payments/refunds. |

### 🔄 Lead Management (CRM)
*   **Conflict Check:** On lead creation, check phone number uniqueness. If exists & has owner -> Conflict Warning.
*   **Public Pool (Recycling):** 
    *   Job runs daily at 02:00.
    *   If a private lead has `last_contact_at > 15 days` -> Reset `owner_id` to NULL (Public Pool).

### 💰 Quoting & Finance
*   **Data Masking:** Planners see `unit_price` (Sales Price) but NOT `cost_price` (Internal Cost).
*   **Approvals:** Discounts below floor price require Manager approval (triggered via API).
*   **Presentation Mode:** Frontend toggle to mask all money fields with `******` for client meetings.

---

## 4. Development Guidelines

### 📂 Directory Structure (Target)
```text
/
├── docs/                 # Design & Spec documentation
├── web/
│   ├── web-admin/        # Vue 3 Admin Panel
│   ├── mini-app/         # C-side Mini Program
│   └── wedding-api/      # FastAPI Backend
└── GEMINI.md             # Project Context (This file)
```

### 📝 API Conventions
*   **Style:** RESTful, OpenAPI (Swagger).
*   **Response Format:**
    ```json
    {
      "code": 200,
      "message": "success",
      "data": { ... },
      "timestamp": 1698723000
    }
    ```
*   **Money Handling:** Store as `Decimal(10, 2)` in DB. Use rigorous precision handling in backend.

### 🚀 Initialization Steps (TODO)
1.  **Backend:** Initialize FastAPI project in `web/wedding-api`. Setup PostgreSQL connection and Alembic.
2.  **Admin:** Scaffold Vue 3 project in `web/web-admin` using Ant Design Pro.
3.  **Mini-App:** Initialize Uni-app project in `web/mini-app`.

---

## 5. Documentation Reference
*   `docs/编程开发指南.md`: Technical specs, database schema, API endpoints.
*   `docs/API开发指南.md`: Detailed API contracts, request/response examples.
*   `docs/管理后台设计.md`: Admin panel UI/UX, permission matrix, page logic.
*   `docs/C端小程序设计.md`: Mobile app UI/UX, gamification, customer journey.
