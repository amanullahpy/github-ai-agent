# Proposed Solutions: amanullahpy/nestjs-learning-lab

## Solution #1: Add Pull Request Template
- **Target File**: `.github/pull_request_template.md`
- **Risk**: LOW
- **Status**: PENDING
- **Proposed Change**:
```
## Description
<!-- Briefly describe the changes introduced in this pull request -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Documentation update
- [ ] Refactoring / code quality improvement

## Checklist
- [ ] Code follows the project's guidelines
- [ ] Self-review of changes performed
- [ ] Documentation updated where appropriate
- [ ] Changes tested locally

```

## Solution #2: Add Standard Bug Report Template
- **Target File**: `.github/ISSUE_TEMPLATE/bug_report.md`
- **Risk**: LOW
- **Status**: PENDING
- **Proposed Change**:
```
---
name: Bug report
about: Create a report to help improve this project
title: ''
labels: bug
assignees: ''
---

## Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Execute '....'
3. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Environment
- OS: [e.g. Windows, macOS, Linux]
- Runtime/Version: [e.g. Node 20, Python 3.12]

```

## Solution #3: Add standard MIT License
- **Target File**: `LICENSE`
- **Risk**: LOW
- **Status**: PENDING
- **Proposed Change**:
```
MIT License

Copyright (c) 2026 amanullahpy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```

## Solution #4: Add Usage section to README
- **Target File**: `README.md`
- **Risk**: LOW
- **Status**: PENDING
- **Proposed Change**:
```
# NestJS Learning Lab 🧪🚀

A clean, production-quality **NestJS Learning Lab** designed specifically to help experienced frontend developers (React / Next.js / TypeScript) master NestJS architecture through working TypeScript code, interactive Swagger endpoints, unit tests, and 15 structured educational markdown guides.

---

## 🎯 Purpose

This project is not a bloated production SaaS or an overly simplified "Hello World". It is built as an interactive learning laboratory demonstrating core NestJS framework concepts in a clean, modular TypeScript application:

- **Modular Architecture**: Feature separation (`UsersModule`, `ProductsModule`, `DemoModule`, `HealthModule`).
- **Dependency Injection**: Inversion of Control with `@Injectable()` providers.
- **DTOs & Validation**: Class validation (`class-validator`) and global `ValidationPipe`.
- **Request Lifecycle**: Middleware, Guards, Interceptors, Pipes, and Exception Filters.
- **OpenAPI Integration**: Live interactive Swagger UI documentation at `/api/docs`.
- **Environment Configuration**: Schema validation via `@nestjs/config`.
- **Unit Testing**: Isolated service and controller testing with Jest.

---

## 📋 Prerequisites

- **Node.js**: v20+ (v24 supported)
- **npm**: v10+

---

## 🚀 Quick Start

### 1. Installation

```bash
cd nestjs-learning-lab
npm install
```

### 2. Environment Setup

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default configuration (`.env`):

```env
NODE_ENV=development
PORT=3000
APP_NAME=NestJS Learning Lab
```

### 3. Start Development Server

```bash
npm run start:dev
```

- **Base API URL**: `http://localhost:3000/api`
- **Swagger Documentation UI**: [`http://localhost:3000/api/docs`](http://localhost:3000/api/docs)

---

## 🛠 Available Scripts

```bash
# Run application in development mode with hot reload
npm run start:dev

# Run application in production mode
npm run start:prod

# Compile TypeScript project to dist/
npm run build

# Run unit tests
npm run test

# Run ESLint check & auto-fix
npm run lint

# Format code with Prettier
npm run format
```

---

## 📂 Project Structure

```text
nestjs-learning-lab/
├── docs/                                  # 15 Educational Markdown Guides
│   ├── 01-nestjs-overview.md
│   ├── 02-project-structure.md
│   ├── 03-modules.md
│   ├── 04-controllers.md
│   ├── 05-providers-and-dependency-injection.md
│   ├── 06-dto-and-validation.md
│   ├── 07-pipes.md
│   ├── 08-guards.md
│   ├── 09-interceptors.md
│   ├── 10-exception-filters.md
│   ├── 11-middleware.md
│   ├── 12-configuration.md
│   ├── 13-swagger.md
│   ├── 14-testing.md
│   └── 15-request-lifecycle.md
│
├── src/
│   ├── main.ts                            # Bootstrap entry point
│   ├── app.module.ts                      # Root module
│   │
│   ├── config/                            # App configuration & validation
│   │   ├── configuration.ts
│   │   └── env.validation.ts
│   │
│   ├── common/                            # Shared utilities & lifecycle components
│   │   ├── filters/global-exception.filter.ts
│   │   ├── guards/demo-auth.guard.ts
│   │   ├── interceptors/logging.interceptor.ts
│   │   ├── middleware/request-id.middleware.ts
│   │   ├── pipes/parse-positive-int.pipe.ts
│   │   └── types/index.ts
│   │
│   ├── health/                            # Health check module
│   │   ├── health.controller.ts
│   │   └── health.module.ts
│   │
│   └── modules/
│       ├── users/                         # Users domain module (In-memory CRUD)
│       │   ├── dto/
│       │   │   ├── create-user.dto.ts
│       │   │   └── update-user.dto.ts
│       │   ├── users.controller.ts
│       │   ├── users.service.ts
│       │   ├── users.module.ts
│       │   ├── users.service.spec.ts
│       │   └── users.controller.spec.ts
│       │
│       ├── products/                      # Products domain module (In-memory CRUD)
│       │   ├── dto/
│       │   │   ├── create-product.dto.ts
│       │   │   └── update-product.dto.ts
│       │   ├── products.controller.ts
│       │   ├── products.service.ts
│       │   ├── products.module.ts
│       │   └── products.service.spec.ts
│       │
│       └── demo/                          # Interactive learning endpoints
│           ├── demo.controller.ts
│           ├── demo.service.ts
│           └── demo.module.ts
│
├── .env
├── .env.example
├── eslint.config.mjs
├── nest-cli.json
├── package.json
├── tsconfig.json
└── README.md
```

---

## 🗺 Endpoint Directory

### Health Tag
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Check service health status |

### Users Tag (In-Memory CRUD)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/users` | Retrieve all users |
| `GET` | `/api/users/:id` | Get specific user by ID |
| `POST` | `/api/users` | Create user (Validates name, email, age 18-100, role enum) |
| `PATCH` | `/api/users/:id` | Partial update user |
| `DELETE` | `/api/users/:id` | Delete user |

### Products Tag (In-Memory CRUD)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/products` | Retrieve all products |
| `GET` | `/api/products/:id` | Get product by ID |
| `POST` | `/api/products` | Create product (Validates price >= 0, inStock boolean) |
| `PATCH` | `/api/products/:id` | Partial update product |
| `DELETE` | `/api/products/:id` | Delete product |

### Demo Tag (Interactive Concept Endpoints)
| Method | Endpoint | Concept Demonstrated |
| :--- | :--- | :--- |
| `GET` | `/api/demo/pipes/:id` | Custom parameter validation (`ParsePositiveIntPipe`) |
| `GET` | `/api/demo/guards` | Concept explanation for NestJS Guards |
| `GET` | `/api/demo/protected` | Route authorization (`DemoAuthGuard` checks `x-demo-token: nest-learning`) |
| `GET` | `/api/demo/interceptors` | Request/Response wrapping & logging (`LoggingInterceptor`) |
| `GET` | `/api/demo/errors` | Centralized exception formatting (`GlobalExceptionFilter`) |
| `GET` | `/api/demo/request-context` | Middleware header injection (`RequestIdMiddleware`) |

---

## 🎓 Recommended Learning Order & Documentation Index

Follow this step-by-step sequence to master NestJS architecture:

1. [`docs/01-nestjs-overview.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/01-nestjs-overview.md) – NestJS core concepts vs Next.js/React
2. [`docs/02-project-structure.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/02-project-structure.md) – Directory organization best practices
3. [`docs/03-modules.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/03-modules.md) – Understanding `@Module()` boundaries, imports & exports
4. [`docs/04-controllers.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/src/modules/users/users.controller.ts) – HTTP routing and thin controllers
5. [`docs/05-providers-and-dependency-injection.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/05-providers-and-dependency-injection.md) – `@Injectable()`, IoC, and constructor injection
6. [`docs/06-dto-and-validation.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/06-dto-and-validation.md) – `class-validator`, DTOs, and global `ValidationPipe`
7. [`docs/07-pipes.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/07-pipes.md) – Parameter transformation and validation pipes
8. [`docs/08-guards.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/08-guards.md) – Request authorization with `CanActivate`
9. [`docs/09-interceptors.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/09-interceptors.md) – Aspect-Oriented programming with RxJS streams
10. [`docs/10-exception-filters.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/10-exception-filters.md) – Catching exceptions with `GlobalExceptionFilter`
11. [`docs/11-middleware.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/11-middleware.md) – HTTP request processing middleware
12. [`docs/12-configuration.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/12-configuration.md) – `@nestjs/config` & startup env schema validation
13. [`docs/13-swagger.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/13-swagger.md) – OpenAPI document generation
14. [`docs/14-testing.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/14-testing.md) – Unit testing services & controllers with Jest
15. [`docs/15-request-lifecycle.md`](file:///c:/Users/mobiGo/Desktop/nothing/nestjs-learning-lab/docs/15-request-lifecycle.md) – The complete NestJS execution sequence diagram


## 🚀 Usage & Quickstart

This section guides you through setting up and running the `nestjs-learning-lab` project locally, enabling you to explore its architecture and interactive examples.

### Prerequisites

Ensure you have the following installed on your system:

*   **Node.js**: Version 18.x or higher (LTS recommended).
*   **npm** or **Yarn**: Package manager (npm comes with Node.js, Yarn can be installed globally).
*   **Docker & Docker Compose**: Required for running the local database instance.

### 1. Clone the Repository

Start by cloning the project to your local machine:

```bash
git clone https://github.com/your-username/nestjs-learning-lab.git
cd nestjs-learning-lab
```

### 2. Install Dependencies

Install all necessary project dependencies using your preferred package manager:

```bash
# Using npm
npm install

# Or using Yarn
# yarn install
```

### 3. Environment Configuration

The project uses environment variables for configuration. A `.env.example` file is provided as a template.

1.  Create a `.env` file in the project root by copying the example:
    ```bash
    cp .env.example .env
    ```
2.  Review and update the variables in your newly created `.env` file as needed. Key variables typically include:
    *   `PORT`: The port the NestJS application will listen on (e.g., `3000`).
    *   `DATABASE_URL`: Connection string for your database.
    *   `JWT_SECRET`: Secret key for JWT authentication.
    *   `API_PREFIX`: Optional API route prefix (e.g., `api/v1`).

    **Example `.env` (for local development):**
    ```env
    # Application Port
    PORT=3000

    # Database Configuration (Post

```
