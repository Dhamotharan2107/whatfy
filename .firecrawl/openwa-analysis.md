[Skip to content](https://github.com/rmyndharis/OpenWA#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/rmyndharis/OpenWA) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/rmyndharis/OpenWA) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/rmyndharis/OpenWA) to refresh your session.Dismiss alert

{{ message }}

[rmyndharis](https://github.com/rmyndharis)/ **[OpenWA](https://github.com/rmyndharis/OpenWA)** Public

- [Notifications](https://github.com/login?return_to=%2Frmyndharis%2FOpenWA) You must be signed in to change notification settings
- [Fork\\
1.6k](https://github.com/login?return_to=%2Frmyndharis%2FOpenWA)
- [Star\\
7.8k](https://github.com/login?return_to=%2Frmyndharis%2FOpenWA)


main

[**11** Branches](https://github.com/rmyndharis/OpenWA/branches) [**7** Tags](https://github.com/rmyndharis/OpenWA/tags)

[Go to Branches page](https://github.com/rmyndharis/OpenWA/branches)[Go to Tags page](https://github.com/rmyndharis/OpenWA/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![rmyndharis](https://avatars.githubusercontent.com/u/2390382?v=4&size=40)](https://github.com/rmyndharis)[rmyndharis](https://github.com/rmyndharis/OpenWA/commits?author=rmyndharis)<br>[chore(deps): bump lucide-react from 0.575.0 to 1.16.0 in /dashboard (](https://github.com/rmyndharis/OpenWA/commit/0fbee7fbee9d746050a20c57544bf7bbb80e65d2) [#…](https://github.com/rmyndharis/OpenWA/pull/108)<br>Open commit detailssuccess<br>2 weeks agoMay 20, 2026<br>[0fbee7f](https://github.com/rmyndharis/OpenWA/commit/0fbee7fbee9d746050a20c57544bf7bbb80e65d2) · 2 weeks agoMay 20, 2026<br>## History<br>[104 Commits](https://github.com/rmyndharis/OpenWA/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/rmyndharis/OpenWA/commits/main/) 104 Commits |
| [.github](https://github.com/rmyndharis/OpenWA/tree/main/.github ".github") | [.github](https://github.com/rmyndharis/OpenWA/tree/main/.github ".github") | [chore(ci): group major dependabot updates to reduce PR noise](https://github.com/rmyndharis/OpenWA/commit/216c33909b3dfa13e5a19dde6405db998bc6756d "chore(ci): group major dependabot updates to reduce PR noise  - Group major version bumps into single PR per directory - Reduce open PR limits (root: 10→5, dashboard: 5→3) - Add labels for easier filtering (dependencies, dashboard, ci)") | 2 weeks agoMay 20, 2026 |
| [dashboard](https://github.com/rmyndharis/OpenWA/tree/main/dashboard "dashboard") | [dashboard](https://github.com/rmyndharis/OpenWA/tree/main/dashboard "dashboard") | [chore(deps): bump lucide-react from 0.575.0 to 1.16.0 in /dashboard (](https://github.com/rmyndharis/OpenWA/commit/0fbee7fbee9d746050a20c57544bf7bbb80e65d2 "chore(deps): bump lucide-react from 0.575.0 to 1.16.0 in /dashboard (#108)  Replaces the Github brand icon (removed in lucide v1) with an inline-SVG GithubIcon component, and adds an aria-label to the footer link. Supersedes #73.") [#…](https://github.com/rmyndharis/OpenWA/pull/108) | 2 weeks agoMay 20, 2026 |
| [docs](https://github.com/rmyndharis/OpenWA/tree/main/docs "docs") | [docs](https://github.com/rmyndharis/OpenWA/tree/main/docs "docs") | [fix: PostgreSQL migration compatibility (](https://github.com/rmyndharis/OpenWA/commit/b5920ce470f9635f5136529d5d73d8189f739511 "fix: PostgreSQL migration compatibility (#59)  - Make migration database-aware with conditional branching - SQLite path kept byte-for-byte identical (zero regression) - PostgreSQL path uses timestamp/NOW()/DEFAULT true instead of   SQLite-specific datetime/datetime('now')/DEFAULT (1) - Simplified PostgreSQL webhooks creation with inline FK constraint - Bump version to 0.1.6 - Sync version badges across README, docs, and Swagger  Fixes #59") [#59](https://github.com/rmyndharis/OpenWA/issues/59) [)](https://github.com/rmyndharis/OpenWA/commit/b5920ce470f9635f5136529d5d73d8189f739511 "fix: PostgreSQL migration compatibility (#59)  - Make migration database-aware with conditional branching - SQLite path kept byte-for-byte identical (zero regression) - PostgreSQL path uses timestamp/NOW()/DEFAULT true instead of   SQLite-specific datetime/datetime('now')/DEFAULT (1) - Simplified PostgreSQL webhooks creation with inline FK constraint - Bump version to 0.1.6 - Sync version badges across README, docs, and Swagger  Fixes #59") | 3 weeks agoMay 17, 2026 |
| [scripts](https://github.com/rmyndharis/OpenWA/tree/main/scripts "scripts") | [scripts](https://github.com/rmyndharis/OpenWA/tree/main/scripts "scripts") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [sdk](https://github.com/rmyndharis/OpenWA/tree/main/sdk "sdk") | [sdk](https://github.com/rmyndharis/OpenWA/tree/main/sdk "sdk") | [feat: add unit tests, release workflow, and SDK scaffolds](https://github.com/rmyndharis/OpenWA/commit/32a0205c69e68d64bbba1eff5fc576d80f97f441 "feat: add unit tests, release workflow, and SDK scaffolds  - Add 94 unit tests across 5 spec files (auth, guard, session, message, webhook) - Add release.yml GitHub Actions workflow (tag-triggered, test gate, Docker) - Add JavaScript/TypeScript and Python SDK scaffolds in sdk/ - Overall test coverage: ~5% → ~17%") | 4 months agoFeb 17, 2026 |
| [src](https://github.com/rmyndharis/OpenWA/tree/main/src "src") | [src](https://github.com/rmyndharis/OpenWA/tree/main/src "src") | [fix(database): add UUID DEFAULT to id columns on Postgres](https://github.com/rmyndharis/OpenWA/commit/e3b29d6b8ae358fed472a5624e4446c68fea1cb8 "fix(database): add UUID DEFAULT to id columns on Postgres  Creating a session (or any other entity with a UUID primary key) on PostgreSQL fails with HTTP 500:    QueryFailedError: null value in column \"id\" of relation \"sessions\"   violates not-null constraint  Root cause: the initial schema migration (1770108659848-AddMessageStatus) created id columns as `varchar PRIMARY KEY NOT NULL` with no DEFAULT. The TypeORM Postgres driver emits `INSERT ... VALUES (DEFAULT, ...)` for columns mapped to @PrimaryGeneratedColumn('uuid') and expects the database to supply the value, so the INSERT fails immediately.  This affects all 6 tables created by that migration: sessions, webhooks, messages, api_keys, audit_logs, message_batches — meaning a fresh PostgreSQL install cannot create any session, API key, or audit log.  Fix: add a migration that runs `ALTER COLUMN id SET DEFAULT gen_random_uuid()::varchar` on every affected table. `gen_random_uuid()` is built into PostgreSQL 13+, no extension required. The migration is a no-op on SQLite (TypeORM generates the UUID in the driver layer there). Both up and down are idempotent: they skip tables that don't exist.  Tested: - Patched the running Postgres DB with the same SQL; POST /api/sessions   now returns 201 with a valid UUID, GET /api/sessions lists it,   DELETE returns 204. - SQLite path verified to no-op via the driver-type guard.") | 3 weeks agoMay 17, 2026 |
| [test](https://github.com/rmyndharis/OpenWA/tree/main/test "test") | [test](https://github.com/rmyndharis/OpenWA/tree/main/test "test") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [traefik](https://github.com/rmyndharis/OpenWA/tree/main/traefik "traefik") | [traefik](https://github.com/rmyndharis/OpenWA/tree/main/traefik "traefik") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [.dockerignore](https://github.com/rmyndharis/OpenWA/blob/main/.dockerignore ".dockerignore") | [.dockerignore](https://github.com/rmyndharis/OpenWA/blob/main/.dockerignore ".dockerignore") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [.env.example](https://github.com/rmyndharis/OpenWA/blob/main/.env.example ".env.example") | [.env.example](https://github.com/rmyndharis/OpenWA/blob/main/.env.example ".env.example") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [.env.minimal](https://github.com/rmyndharis/OpenWA/blob/main/.env.minimal ".env.minimal") | [.env.minimal](https://github.com/rmyndharis/OpenWA/blob/main/.env.minimal ".env.minimal") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [.gitignore](https://github.com/rmyndharis/OpenWA/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/rmyndharis/OpenWA/blob/main/.gitignore ".gitignore") | [chore: add docs/plans/ to gitignore](https://github.com/rmyndharis/OpenWA/commit/85c20035d134247e1e359fa50b2332203a01ac6c "chore: add docs/plans/ to gitignore") | 4 months agoFeb 17, 2026 |
| [.prettierrc](https://github.com/rmyndharis/OpenWA/blob/main/.prettierrc ".prettierrc") | [.prettierrc](https://github.com/rmyndharis/OpenWA/blob/main/.prettierrc ".prettierrc") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [CHANGELOG.md](https://github.com/rmyndharis/OpenWA/blob/main/CHANGELOG.md "CHANGELOG.md") | [CHANGELOG.md](https://github.com/rmyndharis/OpenWA/blob/main/CHANGELOG.md "CHANGELOG.md") | [docs: update CHANGELOG.md for v0.1.6](https://github.com/rmyndharis/OpenWA/commit/8d356256855b4e2408ee02fd03e303b2bd928fe1 "docs: update CHANGELOG.md for v0.1.6") | 3 weeks agoMay 17, 2026 |
| [Dockerfile](https://github.com/rmyndharis/OpenWA/blob/main/Dockerfile "Dockerfile") | [Dockerfile](https://github.com/rmyndharis/OpenWA/blob/main/Dockerfile "Dockerfile") | [fix: upgrade to Node 22 LTS to fix lockfile compatibility](https://github.com/rmyndharis/OpenWA/commit/f6ffa943260604c424d81a5ec63f6a70bb706c64 "fix: upgrade to Node 22 LTS to fix lockfile compatibility  The lockfile was generated with npm 11 (Node 22) which is incompatible with npm 10 (Node 20) used in CI. Upgrading CI, release workflow, and Dockerfile to Node 22 (current LTS).") | 4 months agoFeb 17, 2026 |
| [LICENSE](https://github.com/rmyndharis/OpenWA/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/rmyndharis/OpenWA/blob/main/LICENSE "LICENSE") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [README.md](https://github.com/rmyndharis/OpenWA/blob/main/README.md "README.md") | [README.md](https://github.com/rmyndharis/OpenWA/blob/main/README.md "README.md") | [fix: PostgreSQL migration compatibility (](https://github.com/rmyndharis/OpenWA/commit/b5920ce470f9635f5136529d5d73d8189f739511 "fix: PostgreSQL migration compatibility (#59)  - Make migration database-aware with conditional branching - SQLite path kept byte-for-byte identical (zero regression) - PostgreSQL path uses timestamp/NOW()/DEFAULT true instead of   SQLite-specific datetime/datetime('now')/DEFAULT (1) - Simplified PostgreSQL webhooks creation with inline FK constraint - Bump version to 0.1.6 - Sync version badges across README, docs, and Swagger  Fixes #59") [#59](https://github.com/rmyndharis/OpenWA/issues/59) [)](https://github.com/rmyndharis/OpenWA/commit/b5920ce470f9635f5136529d5d73d8189f739511 "fix: PostgreSQL migration compatibility (#59)  - Make migration database-aware with conditional branching - SQLite path kept byte-for-byte identical (zero regression) - PostgreSQL path uses timestamp/NOW()/DEFAULT true instead of   SQLite-specific datetime/datetime('now')/DEFAULT (1) - Simplified PostgreSQL webhooks creation with inline FK constraint - Bump version to 0.1.6 - Sync version badges across README, docs, and Swagger  Fixes #59") | 3 weeks agoMay 17, 2026 |
| [docker-compose.dev.yml](https://github.com/rmyndharis/OpenWA/blob/main/docker-compose.dev.yml "docker-compose.dev.yml") | [docker-compose.dev.yml](https://github.com/rmyndharis/OpenWA/blob/main/docker-compose.dev.yml "docker-compose.dev.yml") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [docker-compose.yml](https://github.com/rmyndharis/OpenWA/blob/main/docker-compose.yml "docker-compose.yml") | [docker-compose.yml](https://github.com/rmyndharis/OpenWA/blob/main/docker-compose.yml "docker-compose.yml") | [fix: default DATABASE\_SYNCHRONIZE to false to prevent auto-schema cha…](https://github.com/rmyndharis/OpenWA/commit/d25fd12b26392cd9397768a31074d1a7f6ab169d "fix: default DATABASE_SYNCHRONIZE to false to prevent auto-schema changes in production") | 4 months agoFeb 17, 2026 |
| [eslint.config.mjs](https://github.com/rmyndharis/OpenWA/blob/main/eslint.config.mjs "eslint.config.mjs") | [eslint.config.mjs](https://github.com/rmyndharis/OpenWA/blob/main/eslint.config.mjs "eslint.config.mjs") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [nest-cli.json](https://github.com/rmyndharis/OpenWA/blob/main/nest-cli.json "nest-cli.json") | [nest-cli.json](https://github.com/rmyndharis/OpenWA/blob/main/nest-cli.json "nest-cli.json") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [package-lock.json](https://github.com/rmyndharis/OpenWA/blob/main/package-lock.json "package-lock.json") | [package-lock.json](https://github.com/rmyndharis/OpenWA/blob/main/package-lock.json "package-lock.json") | [chore(deps): bump @bull-board packages from 6.x to 7.1.5 (](https://github.com/rmyndharis/OpenWA/commit/7b3bbaf85d798e5cf396c780d68656ccc903f926 "chore(deps): bump @bull-board packages from 6.x to 7.1.5 (#107)  Combines #81, #82, #84 — @bull-board api/express/nestjs share peer deps and must be upgraded together.") [#107](https://github.com/rmyndharis/OpenWA/pull/107) [)](https://github.com/rmyndharis/OpenWA/commit/7b3bbaf85d798e5cf396c780d68656ccc903f926 "chore(deps): bump @bull-board packages from 6.x to 7.1.5 (#107)  Combines #81, #82, #84 — @bull-board api/express/nestjs share peer deps and must be upgraded together.") | 2 weeks agoMay 20, 2026 |
| [package.json](https://github.com/rmyndharis/OpenWA/blob/main/package.json "package.json") | [package.json](https://github.com/rmyndharis/OpenWA/blob/main/package.json "package.json") | [chore(deps): bump @bull-board packages from 6.x to 7.1.5 (](https://github.com/rmyndharis/OpenWA/commit/7b3bbaf85d798e5cf396c780d68656ccc903f926 "chore(deps): bump @bull-board packages from 6.x to 7.1.5 (#107)  Combines #81, #82, #84 — @bull-board api/express/nestjs share peer deps and must be upgraded together.") [#107](https://github.com/rmyndharis/OpenWA/pull/107) [)](https://github.com/rmyndharis/OpenWA/commit/7b3bbaf85d798e5cf396c780d68656ccc903f926 "chore(deps): bump @bull-board packages from 6.x to 7.1.5 (#107)  Combines #81, #82, #84 — @bull-board api/express/nestjs share peer deps and must be upgraded together.") | 2 weeks agoMay 20, 2026 |
| [tsconfig.build.json](https://github.com/rmyndharis/OpenWA/blob/main/tsconfig.build.json "tsconfig.build.json") | [tsconfig.build.json](https://github.com/rmyndharis/OpenWA/blob/main/tsconfig.build.json "tsconfig.build.json") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| [tsconfig.json](https://github.com/rmyndharis/OpenWA/blob/main/tsconfig.json "tsconfig.json") | [tsconfig.json](https://github.com/rmyndharis/OpenWA/blob/main/tsconfig.json "tsconfig.json") | [Initial commit - OpenWA v0.1.0](https://github.com/rmyndharis/OpenWA/commit/c5bd4b5fecb31cd521f3bd435e84c27912d24510 "Initial commit - OpenWA v0.1.0  OpenWA: Open Source WhatsApp API Gateway  Features: - Multi-session WhatsApp management - RESTful API with full messaging support - Web Dashboard for session management - PostgreSQL/SQLite database support - Redis cache and Bull job queue - Webhook system with retry mechanism - Plugin architecture for extensibility - Docker-ready deployment - n8n community node integration  This is the initial public release (v0.1.0).") | 4 months agoFeb 5, 2026 |
| View all files |

## Repository files navigation

[![OpenWA Logo](https://github.com/rmyndharis/OpenWA/raw/main/docs/logo/openwa_logo.webp)](https://github.com/rmyndharis/OpenWA/blob/main/docs/logo/openwa_logo.webp)

# OpenWA

[Permalink: OpenWA](https://github.com/rmyndharis/OpenWA#openwa)

**Open Source WhatsApp API Gateway**

[Features](https://github.com/rmyndharis/OpenWA#-features) •
[Quick Start](https://github.com/rmyndharis/OpenWA#-quick-start) •
[Docs](https://github.com/rmyndharis/OpenWA#-documentation) •
[API](https://github.com/rmyndharis/OpenWA#-api-examples) •
[Contributing](https://github.com/rmyndharis/OpenWA#-contributing)

![Version](https://camo.githubusercontent.com/f1321df17287f50d021f9be7913729ba7edd11f0626b1e6b962ed327330d05fb/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f76657273696f6e2d302e312e362d626c75652e737667)![License](https://camo.githubusercontent.com/8bb50fd2278f18fc326bf71f6e88ca8f884f72f179d3e555e20ed30157190d0d/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c6963656e73652d4d49542d677265656e2e737667)![Node](https://camo.githubusercontent.com/2dd55de5fd6cda4f91dc0f43de7f4155249220d6249cea503d8dd04766d03842/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6e6f64652d32325f4c54532d627269676874677265656e2e737667)![NestJS](https://camo.githubusercontent.com/45899b5d8af8cbc208060454b23cc92e6e099606be9a703fa5c248db9581719b/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f4e6573744a532d31312e782d7265642e737667)![Docker](https://camo.githubusercontent.com/7aa3db3a76815f8fcf908306a6362b4d888fb1666e3ca528782576d6da67b986/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f636b65722d72656164792d626c75652e737667)![TypeScript](https://camo.githubusercontent.com/1b88e991bd5660f74fbb86fac9cdb5d08821ce58807593287f5144c58395d891/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f547970655363726970742d352e782d3331373843362e737667)

* * *

## ✨ Why OpenWA?

[Permalink: ✨ Why OpenWA?](https://github.com/rmyndharis/OpenWA#-why-openwa)

**OpenWA** is a free, open-source WhatsApp API Gateway designed for developers who need full control over their messaging infrastructure—without vendor lock-in or hidden paywalls.

Built on a **pluggable architecture**, OpenWA lets you swap database engines (SQLite/PostgreSQL), storage backends (Local/S3), and cache layers (Memory/Redis) without changing a single line of application code.

|  |  |
| --- | --- |
| 🔓 **100% Open Source** | No licensing fees, no feature locks, full source code access |
| 🏗️ **Pluggable Architecture** | Swap adapters for database, storage, and cache via config |
| 🖥️ **Full Dashboard** | Modern React UI for session, webhook, and API key management |
| 🔹 **Multi-Session Ready** | Run multiple WhatsApp sessions concurrently on one instance |
| 🐳 **Docker Native** | Production-ready with zero configuration |
| 🔗 **n8n Integration** | Community nodes for workflow automation |

* * *

## 🎯 Features

[Permalink: 🎯 Features](https://github.com/rmyndharis/OpenWA#-features)

### Core Features

[Permalink: Core Features](https://github.com/rmyndharis/OpenWA#core-features)

| Feature | Status | Description |
| --- | --- | --- |
| REST API | ✅ | Full WhatsApp API via HTTP endpoints |
| Multi-Session | ✅ | Manage multiple WhatsApp accounts |
| Webhooks | ✅ | Real-time events with HMAC signature |
| Web Dashboard | ✅ | Visual management interface |
| API Key Auth | ✅ | Secure API authentication |
| Swagger Docs | ✅ | Interactive API documentation |

### Messaging

[Permalink: Messaging](https://github.com/rmyndharis/OpenWA#messaging)

| Feature | Status | Description |
| --- | --- | --- |
| Text Messages | ✅ | Send/receive text messages |
| Media Messages | ✅ | Images, videos, documents, audio |
| Message Reactions | ✅ | React to messages with emoji |
| Bulk Messaging | ✅ | Send to multiple recipients |
| Message Status | ✅ | Track delivery and read receipts |

### Advanced

[Permalink: Advanced](https://github.com/rmyndharis/OpenWA#advanced)

| Feature | Status | Description |
| --- | --- | --- |
| Groups API | ✅ | Create, manage, and message groups |
| Channels/Newsletter | ✅ | WhatsApp Channels support |
| Labels Management | ✅ | Organize chats with labels |
| Proxy Support | ✅ | Per-session proxy configuration |
| Rate Limiting | ✅ | Configurable request limits |
| CIDR Whitelisting | ✅ | IP-based access control |
| Audit Logging | ✅ | Track all API operations |

### Infrastructure

[Permalink: Infrastructure](https://github.com/rmyndharis/OpenWA#infrastructure)

| Feature | Status | Description |
| --- | --- | --- |
| SQLite | ✅ | Zero-config embedded database |
| PostgreSQL | ✅ | Production-grade database |
| Redis Cache | ✅ | Optional performance caching |
| S3/MinIO Storage | ✅ | Scalable media storage |
| Docker | ✅ | One-command deployment |
| Health Checks | ✅ | Kubernetes-ready probes |
| Data Migration | ✅ | Export/import between backends |

* * *

## 🚀 Quick Start

[Permalink: 🚀 Quick Start](https://github.com/rmyndharis/OpenWA#-quick-start)

### Option A: Docker (Recommended)

[Permalink: Option A: Docker (Recommended)](https://github.com/rmyndharis/OpenWA#option-a-docker-recommended)

```
# Clone and start
git clone https://github.com/rmyndharis/OpenWA.git
cd OpenWA
docker compose -f docker-compose.dev.yml up -d

# Access
# Dashboard: http://localhost:2886
# API: http://localhost:2785/api
# Swagger: http://localhost:2785/api/docs
```

### Option B: Local Development

[Permalink: Option B: Local Development](https://github.com/rmyndharis/OpenWA#option-b-local-development)

```
# Clone repository
git clone https://github.com/rmyndharis/OpenWA.git
cd OpenWA

# Install dependencies (includes dashboard)
npm install

# Start API + Dashboard (config is auto-generated on first run)
npm run dev

# Access
# Dashboard: http://localhost:2886
# API: http://localhost:2785/api
# Swagger: http://localhost:2785/api/docs
```

* * *

## 🏭 Production Deployment

[Permalink: 🏭 Production Deployment](https://github.com/rmyndharis/OpenWA#-production-deployment)

For production, use the main `docker-compose.yml` with optional services:

```
# Basic production (SQLite, local storage)
docker compose up -d

# With PostgreSQL database
docker compose --profile postgres up -d

# Full stack (PostgreSQL, Redis, Dashboard, Traefik)
docker compose --profile full up -d
```

| Profile | Services |
| --- | --- |
| `postgres` | PostgreSQL database |
| `redis` | Redis cache |
| `minio` | S3-compatible storage |
| `with-dashboard` | Web dashboard |
| `with-proxy` | Traefik reverse proxy |
| `full` | All services above |

> **Development vs Production**
>
> - Development (`docker-compose.dev.yml`): SQLite, local storage, both API & Dashboard included
> - Production (`docker-compose.yml`): Configurable database, profiles for optional services

## 🔌 Ports

[Permalink: 🔌 Ports](https://github.com/rmyndharis/OpenWA#-ports)

| Service | Port | Description |
| --- | --- | --- |
| API | `2785` | REST API endpoints |
| Dashboard | `2886` | Web management interface |
| Swagger | `2785/api/docs` | Interactive API docs |

* * *

## 📡 API Examples

[Permalink: 📡 API Examples](https://github.com/rmyndharis/OpenWA#-api-examples)

### Create a Session

[Permalink: Create a Session](https://github.com/rmyndharis/OpenWA#create-a-session)

```
curl -X POST http://localhost:2785/api/sessions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"name": "my-bot"}'
```

### Start Session & Get QR Code

[Permalink: Start Session & Get QR Code](https://github.com/rmyndharis/OpenWA#start-session--get-qr-code)

```
# Start the session
curl -X POST http://localhost:2785/api/sessions/{sessionId}/start \
  -H "X-API-Key: YOUR_API_KEY"

# Get QR code (scan with WhatsApp)
curl http://localhost:2785/api/sessions/{sessionId}/qr \
  -H "X-API-Key: YOUR_API_KEY"
```

### Send a Message

[Permalink: Send a Message](https://github.com/rmyndharis/OpenWA#send-a-message)

```
curl -X POST http://localhost:2785/api/sessions/{sessionId}/messages/send-text \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "chatId": "628123456789@c.us",
    "text": "Hello from OpenWA!"
  }'
```

### Setup Webhook

[Permalink: Setup Webhook](https://github.com/rmyndharis/OpenWA#setup-webhook)

```
curl -X POST http://localhost:2785/api/sessions/{sessionId}/webhooks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["message.received", "session.status"],
    "secret": "your-hmac-secret"
  }'
```

* * *

## 🛠 Tech Stack

[Permalink: 🛠 Tech Stack](https://github.com/rmyndharis/OpenWA#-tech-stack)

| Layer | Technology |
| --- | --- |
| **Runtime** | Node.js 22 LTS |
| **Framework** | NestJS 11.x |
| **Language** | TypeScript 5.x |
| **WA Engine** | whatsapp-web.js |
| **Database** | SQLite / PostgreSQL |
| **Cache** | Redis (optional) |
| **Storage** | Local / S3 / MinIO |
| **ORM** | TypeORM |
| **Container** | Docker + Docker Compose |

* * *

## 📁 Project Structure

[Permalink: 📁 Project Structure](https://github.com/rmyndharis/OpenWA#-project-structure)

```
openwa/
├── src/
│   ├── main.ts                 # Application entry point
│   ├── app.module.ts           # Root module
│   ├── config/                 # Configuration
│   ├── common/                 # Shared utilities
│   │   ├── cache/              # Redis caching
│   │   └── storage/            # File storage (Local/S3)
│   ├── core/                   # Core systems
│   │   ├── hooks/              # Plugin hooks
│   │   └── plugins/            # Plugin system
│   ├── engine/                 # WhatsApp engine abstraction
│   └── modules/
│       ├── session/            # Session management
│       ├── message/            # Message handling
│       ├── webhook/            # Webhook management
│       ├── group/              # Groups API
│       ├── contact/            # Contacts API
│       ├── auth/               # API key authentication
│       ├── infra/              # Infrastructure management
│       └── health/             # Health checks
├── dashboard/                  # React web dashboard
├── docs/                      # Documentation
├── docker-compose.yml
├── Dockerfile
└── package.json
```

* * *

## 📚 Documentation

[Permalink: 📚 Documentation](https://github.com/rmyndharis/OpenWA#-documentation)

Comprehensive documentation is available in the `docs/` folder:

| Document | Description |
| --- | --- |
| [Project Overview](https://github.com/rmyndharis/OpenWA/blob/main/docs/01-project-overview.md) | Introduction and goals |
| [Requirements](https://github.com/rmyndharis/OpenWA/blob/main/docs/02-requirements-specification.md) | Feature specifications |
| [Architecture](https://github.com/rmyndharis/OpenWA/blob/main/docs/03-system-architecture.md) | System design |
| [Security](https://github.com/rmyndharis/OpenWA/blob/main/docs/04-security-design.md) | Security implementation |
| [Database](https://github.com/rmyndharis/OpenWA/blob/main/docs/05-database-design.md) | Data models and migrations |
| [API Spec](https://github.com/rmyndharis/OpenWA/blob/main/docs/06-api-specification.md) | Complete API reference |
| [Development](https://github.com/rmyndharis/OpenWA/blob/main/docs/08-development-guidelines.md) | Coding standards |
| [Migration Guide](https://github.com/rmyndharis/OpenWA/blob/main/docs/14-migration-guide.md) | Database & storage migration |

* * *

## 🤝 Contributing

[Permalink: 🤝 Contributing](https://github.com/rmyndharis/OpenWA#-contributing)

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

Please read our [Development Guidelines](https://github.com/rmyndharis/OpenWA/blob/main/docs/08-development-guidelines.md) for coding standards and best practices.

* * *

## 📄 License

[Permalink: 📄 License](https://github.com/rmyndharis/OpenWA#-license)

This project is licensed under the **MIT License** – free for personal and commercial use.

See [LICENSE](https://github.com/rmyndharis/OpenWA/blob/main/LICENSE) for details.

* * *

**OpenWA** – Free, Open Source WhatsApp API Gateway

[📖 Documentation](https://github.com/rmyndharis/OpenWA/blob/main/docs/README.md) · [🔌 API Docs](http://localhost:2785/api/docs) · [🐛 Report Bug](https://github.com/rmyndharis/OpenWA/issues) · [💡 Request Feature](https://github.com/rmyndharis/OpenWA/issues)

Made with ❤️ by [Yudhi Armyndharis](https://github.com/rmyndharis) and the OpenWA Community

## About

Free, Open Source, Self-Hosted WhatsApp API Gateway


[www.open-wa.org](https://www.open-wa.org/ "https://www.open-wa.org")

### Topics

[api](https://github.com/topics/api "Topic: api") [gateway](https://github.com/topics/gateway "Topic: gateway") [whatsapp](https://github.com/topics/whatsapp "Topic: whatsapp")

### Resources

[Readme](https://github.com/rmyndharis/OpenWA#readme-ov-file)

### License

[MIT license](https://github.com/rmyndharis/OpenWA#MIT-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/rmyndharis/OpenWA).

[Activity](https://github.com/rmyndharis/OpenWA/activity)

### Stars

[**7.8k**\\
stars](https://github.com/rmyndharis/OpenWA/stargazers)

### Watchers

[**53**\\
watching](https://github.com/rmyndharis/OpenWA/watchers)

### Forks

[**1.6k**\\
forks](https://github.com/rmyndharis/OpenWA/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Frmyndharis%2FOpenWA&report=rmyndharis+%28user%29)

## [Releases\  5](https://github.com/rmyndharis/OpenWA/releases)

[v0.1.6\\
Latest\\
\\
3 weeks agoMay 17, 2026](https://github.com/rmyndharis/OpenWA/releases/tag/v0.1.6)

[\+ 4 releases](https://github.com/rmyndharis/OpenWA/releases)

## [Packages\  1](https://github.com/users/rmyndharis/packages?repo_name=OpenWA)

- [openwa](https://github.com/users/rmyndharis/packages/container/package/openwa)

## [Contributors\  3](https://github.com/rmyndharis/OpenWA/graphs/contributors)

- [![@rmyndharis](https://avatars.githubusercontent.com/u/2390382?s=64&v=4)](https://github.com/rmyndharis)[**rmyndharis** Yudhi Armyndharis](https://github.com/rmyndharis)
- [![@dependabot[bot]](https://avatars.githubusercontent.com/in/29110?s=64&v=4)](https://github.com/apps/dependabot)[**dependabot\[bot\]**](https://github.com/apps/dependabot)
- [![@amstrong-bil](https://avatars.githubusercontent.com/u/201595245?s=64&v=4)](https://github.com/amstrong-bil)[**amstrong-bil**](https://github.com/amstrong-bil)

## Languages

- [TypeScript86.4%](https://github.com/rmyndharis/OpenWA/search?l=typescript)
- [CSS11.8%](https://github.com/rmyndharis/OpenWA/search?l=css)
- [Shell0.8%](https://github.com/rmyndharis/OpenWA/search?l=shell)
- [Python0.5%](https://github.com/rmyndharis/OpenWA/search?l=python)
- [Dockerfile0.3%](https://github.com/rmyndharis/OpenWA/search?l=dockerfile)
- [JavaScript0.2%](https://github.com/rmyndharis/OpenWA/search?l=javascript)

You can’t perform that action at this time.