[Skip to content](https://github.com/Forgemind-git/ForgeChat#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/Forgemind-git/ForgeChat) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/Forgemind-git/ForgeChat) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/Forgemind-git/ForgeChat) to refresh your session.Dismiss alert

{{ message }}

[Forgemind-git](https://github.com/Forgemind-git)/ **[ForgeChat](https://github.com/Forgemind-git/ForgeChat)** Public

- [Notifications](https://github.com/login?return_to=%2FForgemind-git%2FForgeChat) You must be signed in to change notification settings
- [Fork\\
11](https://github.com/login?return_to=%2FForgemind-git%2FForgeChat)
- [Star\\
31](https://github.com/login?return_to=%2FForgemind-git%2FForgeChat)


main

[**8** Branches](https://github.com/Forgemind-git/ForgeChat/branches) [**4** Tags](https://github.com/Forgemind-git/ForgeChat/tags)

[Go to Branches page](https://github.com/Forgemind-git/ForgeChat/branches)[Go to Tags page](https://github.com/Forgemind-git/ForgeChat/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>![sathyaprakash000](https://avatars.githubusercontent.com/u/55381501?v=4&size=40)![sthirumalairajan2212](https://avatars.githubusercontent.com/u/92260025?v=4&size=40)<br>[sathyaprakash000](https://github.com/Forgemind-git/ForgeChat/commits?author=sathyaprakash000)<br>and<br>[sthirumalairajan2212](https://github.com/Forgemind-git/ForgeChat/commits?author=sthirumalairajan2212)<br>[chore(release): v1.2.1 (](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17) [#70](https://github.com/Forgemind-git/ForgeChat/pull/70) [)](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17)<br>Open commit detailssuccess<br>last weekJun 17, 2026<br>[58b81fb](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17) · last weekJun 17, 2026<br>## History<br>[62 Commits](https://github.com/Forgemind-git/ForgeChat/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/Forgemind-git/ForgeChat/commits/main/) 62 Commits |
| [.github](https://github.com/Forgemind-git/ForgeChat/tree/main/.github ".github") | [.github](https://github.com/Forgemind-git/ForgeChat/tree/main/.github ".github") | [fix(ci): build backend image from repo root so db/migrations is in co…](https://github.com/Forgemind-git/ForgeChat/commit/93effc1510a3e0a19138a1c36d1735c97c931a0c "fix(ci): build backend image from repo root so db/migrations is in context (#57)  The backend Dockerfile COPYs backend/ and db/migrations/ (for the boot-time migration runner) and builds from the repo root, matching docker-compose.yml. docker-publish.yml still used context: ./backend, so the v1.1.0 release build failed with \"/db/migrations: not found\". Build backend with context \".\" and an explicit per-image Dockerfile path; frontend stays self-contained.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | 3 weeks agoJun 4, 2026 |
| [backend](https://github.com/Forgemind-git/ForgeChat/tree/main/backend "backend") | [backend](https://github.com/Forgemind-git/ForgeChat/tree/main/backend "backend") | [chore(release): v1.2.1 (](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17 "chore(release): v1.2.1 (#70)  Patch release: media-template broadcasts now send with their header image (resolved from the template's own saved media, like Send Test), fixing the Pending → Failed broadcast failure. Bumps backend/frontend/mcp-server to 1.2.1 and adds the CHANGELOG entry.  Signed-off-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com> Co-authored-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com>") [#70](https://github.com/Forgemind-git/ForgeChat/pull/70) [)](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17 "chore(release): v1.2.1 (#70)  Patch release: media-template broadcasts now send with their header image (resolved from the template's own saved media, like Send Test), fixing the Pending → Failed broadcast failure. Bumps backend/frontend/mcp-server to 1.2.1 and adds the CHANGELOG entry.  Signed-off-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com> Co-authored-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com>") | last weekJun 17, 2026 |
| [db/migrations](https://github.com/Forgemind-git/ForgeChat/tree/main/db/migrations "This path skips through empty directories") | [db/migrations](https://github.com/Forgemind-git/ForgeChat/tree/main/db/migrations "This path skips through empty directories") | [Sync working-copy code: AI agent suite + MCP server (v1.2.0) (](https://github.com/Forgemind-git/ForgeChat/commit/448091550d3167c0d0a51ea59cadafdcfe0b0477 "Sync working-copy code: AI agent suite + MCP server (v1.2.0) (#63)  * feat: sync working-copy code — AI agent suite + MCP server (v1.2.0)  Brings the latest /root/Forge-Chat working code into ForgeChat: - Sheets `upsert` op, CRM write-back tools, human handoff (escalate + keywords +   round-robin + pause/resume + chat take-over), auto-summary on close,   \"new conversations only\" trigger mode - MCP agent-builder server (stdio + HTTP): read_sheet_values, upsert, discovery - Version bump to 1.2.0  ForgeChat's curated docs/CI (README, CONTRIBUTING, CHANGELOG, DEPLOY*, .github) are intentionally left untouched.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * docs(readme): add \"Build agents from Claude (MCP server)\" setup section  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * fix(ci): sync backend lock, guard agentConversation call; docs(skill): Phase 4 latest  - backend/package-lock.json regenerated to match package.json (MCP deps) so   `npm ci` passes - ChatWindow: guard api.agentConversation?.status?.() so the header never breaks   when the endpoint/api shape is absent (fixes ChatWindow.header unit tests) - SKILL.md Phase 4: drop \"(optional)\", add read_sheet_values + the Sheets   `upsert` op (recommended for logging)  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  ---------  Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>") [#63](https://github.com/Forgemind-git/ForgeChat/pull/63) [)](https://github.com/Forgemind-git/ForgeChat/commit/448091550d3167c0d0a51ea59cadafdcfe0b0477 "Sync working-copy code: AI agent suite + MCP server (v1.2.0) (#63)  * feat: sync working-copy code — AI agent suite + MCP server (v1.2.0)  Brings the latest /root/Forge-Chat working code into ForgeChat: - Sheets `upsert` op, CRM write-back tools, human handoff (escalate + keywords +   round-robin + pause/resume + chat take-over), auto-summary on close,   \"new conversations only\" trigger mode - MCP agent-builder server (stdio + HTTP): read_sheet_values, upsert, discovery - Version bump to 1.2.0  ForgeChat's curated docs/CI (README, CONTRIBUTING, CHANGELOG, DEPLOY*, .github) are intentionally left untouched.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * docs(readme): add \"Build agents from Claude (MCP server)\" setup section  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * fix(ci): sync backend lock, guard agentConversation call; docs(skill): Phase 4 latest  - backend/package-lock.json regenerated to match package.json (MCP deps) so   `npm ci` passes - ChatWindow: guard api.agentConversation?.status?.() so the header never breaks   when the endpoint/api shape is absent (fixes ChatWindow.header unit tests) - SKILL.md Phase 4: drop \"(optional)\", add read_sheet_values + the Sheets   `upsert` op (recommended for logging)  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  ---------  Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>") | 2 weeks agoJun 10, 2026 |
| [docs](https://github.com/Forgemind-git/ForgeChat/tree/main/docs "docs") | [docs](https://github.com/Forgemind-git/ForgeChat/tree/main/docs "docs") | [feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, te…](https://github.com/Forgemind-git/ForgeChat/commit/bb8a60d12069c05be13d67ed4d398c57e596afa1 "feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, template rendering (#55)  Sync the full application into the public repo for the official v1.1.0 release.  Added - AI agents that reply automatically: engine, builder UI, live preview, run   history, keyword/any-message/new-contact triggers, and media-send. - AI model connectors (OpenAI, Anthropic) with a Settings → AI Models tab. - Google integration (Sheets lookup + Drive). Client ID/Secret/redirect are   entered in Settings → Integrations and stored encrypted in the DB — no env files. - Voice-note understanding: incoming audio is transcribed and answered as text. - WhatsApp-style template rendering in chat & broadcast previews, including   {{1}} variable substitution and image headers. - Custom-text variables in bulk broadcasts. - Bundled docker-compose.yml (+ docker-compose.prod.yml overlay) so a fresh   clone runs with a single `docker compose up -d`, plus clearer macOS notes. - Server-sent events for live UI updates; boot-time migration runner.  Changed - Brand-language pass for Meta / WhatsApp guidelines (README, login splash,   TRADEMARK.md, affiliation disclaimer). - license-check CI: allow url-template@2.0.8 (BSD-3-Clause googleapis dep). - Versions bumped to 1.1.0; CHANGELOG updated.  Notes - README video preview kept unchanged (GIF tour + YouTube link). - All documentation/clone URLs point at the public ForgeChat repo.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | 3 weeks agoJun 4, 2026 |
| [frontend](https://github.com/Forgemind-git/ForgeChat/tree/main/frontend "frontend") | [frontend](https://github.com/Forgemind-git/ForgeChat/tree/main/frontend "frontend") | [chore(release): v1.2.1 (](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17 "chore(release): v1.2.1 (#70)  Patch release: media-template broadcasts now send with their header image (resolved from the template's own saved media, like Send Test), fixing the Pending → Failed broadcast failure. Bumps backend/frontend/mcp-server to 1.2.1 and adds the CHANGELOG entry.  Signed-off-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com> Co-authored-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com>") [#70](https://github.com/Forgemind-git/ForgeChat/pull/70) [)](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17 "chore(release): v1.2.1 (#70)  Patch release: media-template broadcasts now send with their header image (resolved from the template's own saved media, like Send Test), fixing the Pending → Failed broadcast failure. Bumps backend/frontend/mcp-server to 1.2.1 and adds the CHANGELOG entry.  Signed-off-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com> Co-authored-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com>") | last weekJun 17, 2026 |
| [mcp-server](https://github.com/Forgemind-git/ForgeChat/tree/main/mcp-server "mcp-server") | [mcp-server](https://github.com/Forgemind-git/ForgeChat/tree/main/mcp-server "mcp-server") | [chore(release): v1.2.1 (](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17 "chore(release): v1.2.1 (#70)  Patch release: media-template broadcasts now send with their header image (resolved from the template's own saved media, like Send Test), fixing the Pending → Failed broadcast failure. Bumps backend/frontend/mcp-server to 1.2.1 and adds the CHANGELOG entry.  Signed-off-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com> Co-authored-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com>") [#70](https://github.com/Forgemind-git/ForgeChat/pull/70) [)](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17 "chore(release): v1.2.1 (#70)  Patch release: media-template broadcasts now send with their header image (resolved from the template's own saved media, like Send Test), fixing the Pending → Failed broadcast failure. Bumps backend/frontend/mcp-server to 1.2.1 and adds the CHANGELOG entry.  Signed-off-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com> Co-authored-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com>") | last weekJun 17, 2026 |
| [.dockerignore](https://github.com/Forgemind-git/ForgeChat/blob/main/.dockerignore ".dockerignore") | [.dockerignore](https://github.com/Forgemind-git/ForgeChat/blob/main/.dockerignore ".dockerignore") | [feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, te…](https://github.com/Forgemind-git/ForgeChat/commit/bb8a60d12069c05be13d67ed4d398c57e596afa1 "feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, template rendering (#55)  Sync the full application into the public repo for the official v1.1.0 release.  Added - AI agents that reply automatically: engine, builder UI, live preview, run   history, keyword/any-message/new-contact triggers, and media-send. - AI model connectors (OpenAI, Anthropic) with a Settings → AI Models tab. - Google integration (Sheets lookup + Drive). Client ID/Secret/redirect are   entered in Settings → Integrations and stored encrypted in the DB — no env files. - Voice-note understanding: incoming audio is transcribed and answered as text. - WhatsApp-style template rendering in chat & broadcast previews, including   {{1}} variable substitution and image headers. - Custom-text variables in bulk broadcasts. - Bundled docker-compose.yml (+ docker-compose.prod.yml overlay) so a fresh   clone runs with a single `docker compose up -d`, plus clearer macOS notes. - Server-sent events for live UI updates; boot-time migration runner.  Changed - Brand-language pass for Meta / WhatsApp guidelines (README, login splash,   TRADEMARK.md, affiliation disclaimer). - license-check CI: allow url-template@2.0.8 (BSD-3-Clause googleapis dep). - Versions bumped to 1.1.0; CHANGELOG updated.  Notes - README video preview kept unchanged (GIF tour + YouTube link). - All documentation/clone URLs point at the public ForgeChat repo.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | 3 weeks agoJun 4, 2026 |
| [.gitignore](https://github.com/Forgemind-git/ForgeChat/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/Forgemind-git/ForgeChat/blob/main/.gitignore ".gitignore") | [Sync working-copy code: AI agent suite + MCP server (v1.2.0) (](https://github.com/Forgemind-git/ForgeChat/commit/448091550d3167c0d0a51ea59cadafdcfe0b0477 "Sync working-copy code: AI agent suite + MCP server (v1.2.0) (#63)  * feat: sync working-copy code — AI agent suite + MCP server (v1.2.0)  Brings the latest /root/Forge-Chat working code into ForgeChat: - Sheets `upsert` op, CRM write-back tools, human handoff (escalate + keywords +   round-robin + pause/resume + chat take-over), auto-summary on close,   \"new conversations only\" trigger mode - MCP agent-builder server (stdio + HTTP): read_sheet_values, upsert, discovery - Version bump to 1.2.0  ForgeChat's curated docs/CI (README, CONTRIBUTING, CHANGELOG, DEPLOY*, .github) are intentionally left untouched.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * docs(readme): add \"Build agents from Claude (MCP server)\" setup section  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * fix(ci): sync backend lock, guard agentConversation call; docs(skill): Phase 4 latest  - backend/package-lock.json regenerated to match package.json (MCP deps) so   `npm ci` passes - ChatWindow: guard api.agentConversation?.status?.() so the header never breaks   when the endpoint/api shape is absent (fixes ChatWindow.header unit tests) - SKILL.md Phase 4: drop \"(optional)\", add read_sheet_values + the Sheets   `upsert` op (recommended for logging)  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  ---------  Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>") [#63](https://github.com/Forgemind-git/ForgeChat/pull/63) [)](https://github.com/Forgemind-git/ForgeChat/commit/448091550d3167c0d0a51ea59cadafdcfe0b0477 "Sync working-copy code: AI agent suite + MCP server (v1.2.0) (#63)  * feat: sync working-copy code — AI agent suite + MCP server (v1.2.0)  Brings the latest /root/Forge-Chat working code into ForgeChat: - Sheets `upsert` op, CRM write-back tools, human handoff (escalate + keywords +   round-robin + pause/resume + chat take-over), auto-summary on close,   \"new conversations only\" trigger mode - MCP agent-builder server (stdio + HTTP): read_sheet_values, upsert, discovery - Version bump to 1.2.0  ForgeChat's curated docs/CI (README, CONTRIBUTING, CHANGELOG, DEPLOY*, .github) are intentionally left untouched.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * docs(readme): add \"Build agents from Claude (MCP server)\" setup section  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * fix(ci): sync backend lock, guard agentConversation call; docs(skill): Phase 4 latest  - backend/package-lock.json regenerated to match package.json (MCP deps) so   `npm ci` passes - ChatWindow: guard api.agentConversation?.status?.() so the header never breaks   when the endpoint/api shape is absent (fixes ChatWindow.header unit tests) - SKILL.md Phase 4: drop \"(optional)\", add read_sheet_values + the Sheets   `upsert` op (recommended for logging)  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  ---------  Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>") | 2 weeks agoJun 10, 2026 |
| [AUTHORS.md](https://github.com/Forgemind-git/ForgeChat/blob/main/AUTHORS.md "AUTHORS.md") | [AUTHORS.md](https://github.com/Forgemind-git/ForgeChat/blob/main/AUTHORS.md "AUTHORS.md") | [ForgeChat — initial public release](https://github.com/Forgemind-git/ForgeChat/commit/1b3af0df4eaab72cbdce1d6b443bb02dda934175 "ForgeChat — initial public release  Public, source-available release of ForgeChat, a full-stack WhatsApp CRM on the Meta WhatsApp Cloud API. Published with a fresh history; see CHANGELOG.md for the 1.0.1 feature set and the Sustainable Use License in LICENSE.md.  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com> Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | last monthMay 24, 2026 |
| [CHANGELOG.md](https://github.com/Forgemind-git/ForgeChat/blob/main/CHANGELOG.md "CHANGELOG.md") | [CHANGELOG.md](https://github.com/Forgemind-git/ForgeChat/blob/main/CHANGELOG.md "CHANGELOG.md") | [chore(release): v1.2.1 (](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17 "chore(release): v1.2.1 (#70)  Patch release: media-template broadcasts now send with their header image (resolved from the template's own saved media, like Send Test), fixing the Pending → Failed broadcast failure. Bumps backend/frontend/mcp-server to 1.2.1 and adds the CHANGELOG entry.  Signed-off-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com> Co-authored-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com>") [#70](https://github.com/Forgemind-git/ForgeChat/pull/70) [)](https://github.com/Forgemind-git/ForgeChat/commit/58b81fb89e503e78f27404f947a44a38590dbb17 "chore(release): v1.2.1 (#70)  Patch release: media-template broadcasts now send with their header image (resolved from the template's own saved media, like Send Test), fixing the Pending → Failed broadcast failure. Bumps backend/frontend/mcp-server to 1.2.1 and adds the CHANGELOG entry.  Signed-off-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com> Co-authored-by: sthirumalairajan2212 <92260025+sthirumalairajan2212@users.noreply.github.com>") | last weekJun 17, 2026 |
| [CODE\_OF\_CONDUCT.md](https://github.com/Forgemind-git/ForgeChat/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md") | [CODE\_OF\_CONDUCT.md](https://github.com/Forgemind-git/ForgeChat/blob/main/CODE_OF_CONDUCT.md "CODE_OF_CONDUCT.md") | [ForgeChat — initial public release](https://github.com/Forgemind-git/ForgeChat/commit/1b3af0df4eaab72cbdce1d6b443bb02dda934175 "ForgeChat — initial public release  Public, source-available release of ForgeChat, a full-stack WhatsApp CRM on the Meta WhatsApp Cloud API. Published with a fresh history; see CHANGELOG.md for the 1.0.1 feature set and the Sustainable Use License in LICENSE.md.  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com> Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | last monthMay 24, 2026 |
| [CONTRIBUTING.md](https://github.com/Forgemind-git/ForgeChat/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [CONTRIBUTING.md](https://github.com/Forgemind-git/ForgeChat/blob/main/CONTRIBUTING.md "CONTRIBUTING.md") | [feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, te…](https://github.com/Forgemind-git/ForgeChat/commit/bb8a60d12069c05be13d67ed4d398c57e596afa1 "feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, template rendering (#55)  Sync the full application into the public repo for the official v1.1.0 release.  Added - AI agents that reply automatically: engine, builder UI, live preview, run   history, keyword/any-message/new-contact triggers, and media-send. - AI model connectors (OpenAI, Anthropic) with a Settings → AI Models tab. - Google integration (Sheets lookup + Drive). Client ID/Secret/redirect are   entered in Settings → Integrations and stored encrypted in the DB — no env files. - Voice-note understanding: incoming audio is transcribed and answered as text. - WhatsApp-style template rendering in chat & broadcast previews, including   {{1}} variable substitution and image headers. - Custom-text variables in bulk broadcasts. - Bundled docker-compose.yml (+ docker-compose.prod.yml overlay) so a fresh   clone runs with a single `docker compose up -d`, plus clearer macOS notes. - Server-sent events for live UI updates; boot-time migration runner.  Changed - Brand-language pass for Meta / WhatsApp guidelines (README, login splash,   TRADEMARK.md, affiliation disclaimer). - license-check CI: allow url-template@2.0.8 (BSD-3-Clause googleapis dep). - Versions bumped to 1.1.0; CHANGELOG updated.  Notes - README video preview kept unchanged (GIF tour + YouTube link). - All documentation/clone URLs point at the public ForgeChat repo.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | 3 weeks agoJun 4, 2026 |
| [Caddyfile](https://github.com/Forgemind-git/ForgeChat/blob/main/Caddyfile "Caddyfile") | [Caddyfile](https://github.com/Forgemind-git/ForgeChat/blob/main/Caddyfile "Caddyfile") | [feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, te…](https://github.com/Forgemind-git/ForgeChat/commit/bb8a60d12069c05be13d67ed4d398c57e596afa1 "feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, template rendering (#55)  Sync the full application into the public repo for the official v1.1.0 release.  Added - AI agents that reply automatically: engine, builder UI, live preview, run   history, keyword/any-message/new-contact triggers, and media-send. - AI model connectors (OpenAI, Anthropic) with a Settings → AI Models tab. - Google integration (Sheets lookup + Drive). Client ID/Secret/redirect are   entered in Settings → Integrations and stored encrypted in the DB — no env files. - Voice-note understanding: incoming audio is transcribed and answered as text. - WhatsApp-style template rendering in chat & broadcast previews, including   {{1}} variable substitution and image headers. - Custom-text variables in bulk broadcasts. - Bundled docker-compose.yml (+ docker-compose.prod.yml overlay) so a fresh   clone runs with a single `docker compose up -d`, plus clearer macOS notes. - Server-sent events for live UI updates; boot-time migration runner.  Changed - Brand-language pass for Meta / WhatsApp guidelines (README, login splash,   TRADEMARK.md, affiliation disclaimer). - license-check CI: allow url-template@2.0.8 (BSD-3-Clause googleapis dep). - Versions bumped to 1.1.0; CHANGELOG updated.  Notes - README video preview kept unchanged (GIF tour + YouTube link). - All documentation/clone URLs point at the public ForgeChat repo.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | 3 weeks agoJun 4, 2026 |
| [DEPLOY-DIGITALOCEAN.md](https://github.com/Forgemind-git/ForgeChat/blob/main/DEPLOY-DIGITALOCEAN.md "DEPLOY-DIGITALOCEAN.md") | [DEPLOY-DIGITALOCEAN.md](https://github.com/Forgemind-git/ForgeChat/blob/main/DEPLOY-DIGITALOCEAN.md "DEPLOY-DIGITALOCEAN.md") | [feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, te…](https://github.com/Forgemind-git/ForgeChat/commit/bb8a60d12069c05be13d67ed4d398c57e596afa1 "feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, template rendering (#55)  Sync the full application into the public repo for the official v1.1.0 release.  Added - AI agents that reply automatically: engine, builder UI, live preview, run   history, keyword/any-message/new-contact triggers, and media-send. - AI model connectors (OpenAI, Anthropic) with a Settings → AI Models tab. - Google integration (Sheets lookup + Drive). Client ID/Secret/redirect are   entered in Settings → Integrations and stored encrypted in the DB — no env files. - Voice-note understanding: incoming audio is transcribed and answered as text. - WhatsApp-style template rendering in chat & broadcast previews, including   {{1}} variable substitution and image headers. - Custom-text variables in bulk broadcasts. - Bundled docker-compose.yml (+ docker-compose.prod.yml overlay) so a fresh   clone runs with a single `docker compose up -d`, plus clearer macOS notes. - Server-sent events for live UI updates; boot-time migration runner.  Changed - Brand-language pass for Meta / WhatsApp guidelines (README, login splash,   TRADEMARK.md, affiliation disclaimer). - license-check CI: allow url-template@2.0.8 (BSD-3-Clause googleapis dep). - Versions bumped to 1.1.0; CHANGELOG updated.  Notes - README video preview kept unchanged (GIF tour + YouTube link). - All documentation/clone URLs point at the public ForgeChat repo.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | 3 weeks agoJun 4, 2026 |
| [DEPLOY.md](https://github.com/Forgemind-git/ForgeChat/blob/main/DEPLOY.md "DEPLOY.md") | [DEPLOY.md](https://github.com/Forgemind-git/ForgeChat/blob/main/DEPLOY.md "DEPLOY.md") | [feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, te…](https://github.com/Forgemind-git/ForgeChat/commit/bb8a60d12069c05be13d67ed4d398c57e596afa1 "feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, template rendering (#55)  Sync the full application into the public repo for the official v1.1.0 release.  Added - AI agents that reply automatically: engine, builder UI, live preview, run   history, keyword/any-message/new-contact triggers, and media-send. - AI model connectors (OpenAI, Anthropic) with a Settings → AI Models tab. - Google integration (Sheets lookup + Drive). Client ID/Secret/redirect are   entered in Settings → Integrations and stored encrypted in the DB — no env files. - Voice-note understanding: incoming audio is transcribed and answered as text. - WhatsApp-style template rendering in chat & broadcast previews, including   {{1}} variable substitution and image headers. - Custom-text variables in bulk broadcasts. - Bundled docker-compose.yml (+ docker-compose.prod.yml overlay) so a fresh   clone runs with a single `docker compose up -d`, plus clearer macOS notes. - Server-sent events for live UI updates; boot-time migration runner.  Changed - Brand-language pass for Meta / WhatsApp guidelines (README, login splash,   TRADEMARK.md, affiliation disclaimer). - license-check CI: allow url-template@2.0.8 (BSD-3-Clause googleapis dep). - Versions bumped to 1.1.0; CHANGELOG updated.  Notes - README video preview kept unchanged (GIF tour + YouTube link). - All documentation/clone URLs point at the public ForgeChat repo.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | 3 weeks agoJun 4, 2026 |
| [LICENSE.md](https://github.com/Forgemind-git/ForgeChat/blob/main/LICENSE.md "LICENSE.md") | [LICENSE.md](https://github.com/Forgemind-git/ForgeChat/blob/main/LICENSE.md "LICENSE.md") | [ForgeChat — initial public release](https://github.com/Forgemind-git/ForgeChat/commit/1b3af0df4eaab72cbdce1d6b443bb02dda934175 "ForgeChat — initial public release  Public, source-available release of ForgeChat, a full-stack WhatsApp CRM on the Meta WhatsApp Cloud API. Published with a fresh history; see CHANGELOG.md for the 1.0.1 feature set and the Sustainable Use License in LICENSE.md.  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com> Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | last monthMay 24, 2026 |
| [README.md](https://github.com/Forgemind-git/ForgeChat/blob/main/README.md "README.md") | [README.md](https://github.com/Forgemind-git/ForgeChat/blob/main/README.md "README.md") | [Sync working-copy code: AI agent suite + MCP server (v1.2.0) (](https://github.com/Forgemind-git/ForgeChat/commit/448091550d3167c0d0a51ea59cadafdcfe0b0477 "Sync working-copy code: AI agent suite + MCP server (v1.2.0) (#63)  * feat: sync working-copy code — AI agent suite + MCP server (v1.2.0)  Brings the latest /root/Forge-Chat working code into ForgeChat: - Sheets `upsert` op, CRM write-back tools, human handoff (escalate + keywords +   round-robin + pause/resume + chat take-over), auto-summary on close,   \"new conversations only\" trigger mode - MCP agent-builder server (stdio + HTTP): read_sheet_values, upsert, discovery - Version bump to 1.2.0  ForgeChat's curated docs/CI (README, CONTRIBUTING, CHANGELOG, DEPLOY*, .github) are intentionally left untouched.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * docs(readme): add \"Build agents from Claude (MCP server)\" setup section  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * fix(ci): sync backend lock, guard agentConversation call; docs(skill): Phase 4 latest  - backend/package-lock.json regenerated to match package.json (MCP deps) so   `npm ci` passes - ChatWindow: guard api.agentConversation?.status?.() so the header never breaks   when the endpoint/api shape is absent (fixes ChatWindow.header unit tests) - SKILL.md Phase 4: drop \"(optional)\", add read_sheet_values + the Sheets   `upsert` op (recommended for logging)  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  ---------  Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>") [#63](https://github.com/Forgemind-git/ForgeChat/pull/63) [)](https://github.com/Forgemind-git/ForgeChat/commit/448091550d3167c0d0a51ea59cadafdcfe0b0477 "Sync working-copy code: AI agent suite + MCP server (v1.2.0) (#63)  * feat: sync working-copy code — AI agent suite + MCP server (v1.2.0)  Brings the latest /root/Forge-Chat working code into ForgeChat: - Sheets `upsert` op, CRM write-back tools, human handoff (escalate + keywords +   round-robin + pause/resume + chat take-over), auto-summary on close,   \"new conversations only\" trigger mode - MCP agent-builder server (stdio + HTTP): read_sheet_values, upsert, discovery - Version bump to 1.2.0  ForgeChat's curated docs/CI (README, CONTRIBUTING, CHANGELOG, DEPLOY*, .github) are intentionally left untouched.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * docs(readme): add \"Build agents from Claude (MCP server)\" setup section  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * fix(ci): sync backend lock, guard agentConversation call; docs(skill): Phase 4 latest  - backend/package-lock.json regenerated to match package.json (MCP deps) so   `npm ci` passes - ChatWindow: guard api.agentConversation?.status?.() so the header never breaks   when the endpoint/api shape is absent (fixes ChatWindow.header unit tests) - SKILL.md Phase 4: drop \"(optional)\", add read_sheet_values + the Sheets   `upsert` op (recommended for logging)  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  ---------  Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>") | 2 weeks agoJun 10, 2026 |
| [SECURITY.md](https://github.com/Forgemind-git/ForgeChat/blob/main/SECURITY.md "SECURITY.md") | [SECURITY.md](https://github.com/Forgemind-git/ForgeChat/blob/main/SECURITY.md "SECURITY.md") | [ForgeChat — initial public release](https://github.com/Forgemind-git/ForgeChat/commit/1b3af0df4eaab72cbdce1d6b443bb02dda934175 "ForgeChat — initial public release  Public, source-available release of ForgeChat, a full-stack WhatsApp CRM on the Meta WhatsApp Cloud API. Published with a fresh history; see CHANGELOG.md for the 1.0.1 feature set and the Sustainable Use License in LICENSE.md.  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com> Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | last monthMay 24, 2026 |
| [SESSION-HANDOFF.md](https://github.com/Forgemind-git/ForgeChat/blob/main/SESSION-HANDOFF.md "SESSION-HANDOFF.md") | [SESSION-HANDOFF.md](https://github.com/Forgemind-git/ForgeChat/blob/main/SESSION-HANDOFF.md "SESSION-HANDOFF.md") | [ForgeChat — initial public release](https://github.com/Forgemind-git/ForgeChat/commit/1b3af0df4eaab72cbdce1d6b443bb02dda934175 "ForgeChat — initial public release  Public, source-available release of ForgeChat, a full-stack WhatsApp CRM on the Meta WhatsApp Cloud API. Published with a fresh history; see CHANGELOG.md for the 1.0.1 feature set and the Sustainable Use License in LICENSE.md.  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com> Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | last monthMay 24, 2026 |
| [SKILL.md](https://github.com/Forgemind-git/ForgeChat/blob/main/SKILL.md "SKILL.md") | [SKILL.md](https://github.com/Forgemind-git/ForgeChat/blob/main/SKILL.md "SKILL.md") | [Sync working-copy code: AI agent suite + MCP server (v1.2.0) (](https://github.com/Forgemind-git/ForgeChat/commit/448091550d3167c0d0a51ea59cadafdcfe0b0477 "Sync working-copy code: AI agent suite + MCP server (v1.2.0) (#63)  * feat: sync working-copy code — AI agent suite + MCP server (v1.2.0)  Brings the latest /root/Forge-Chat working code into ForgeChat: - Sheets `upsert` op, CRM write-back tools, human handoff (escalate + keywords +   round-robin + pause/resume + chat take-over), auto-summary on close,   \"new conversations only\" trigger mode - MCP agent-builder server (stdio + HTTP): read_sheet_values, upsert, discovery - Version bump to 1.2.0  ForgeChat's curated docs/CI (README, CONTRIBUTING, CHANGELOG, DEPLOY*, .github) are intentionally left untouched.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * docs(readme): add \"Build agents from Claude (MCP server)\" setup section  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * fix(ci): sync backend lock, guard agentConversation call; docs(skill): Phase 4 latest  - backend/package-lock.json regenerated to match package.json (MCP deps) so   `npm ci` passes - ChatWindow: guard api.agentConversation?.status?.() so the header never breaks   when the endpoint/api shape is absent (fixes ChatWindow.header unit tests) - SKILL.md Phase 4: drop \"(optional)\", add read_sheet_values + the Sheets   `upsert` op (recommended for logging)  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  ---------  Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>") [#63](https://github.com/Forgemind-git/ForgeChat/pull/63) [)](https://github.com/Forgemind-git/ForgeChat/commit/448091550d3167c0d0a51ea59cadafdcfe0b0477 "Sync working-copy code: AI agent suite + MCP server (v1.2.0) (#63)  * feat: sync working-copy code — AI agent suite + MCP server (v1.2.0)  Brings the latest /root/Forge-Chat working code into ForgeChat: - Sheets `upsert` op, CRM write-back tools, human handoff (escalate + keywords +   round-robin + pause/resume + chat take-over), auto-summary on close,   \"new conversations only\" trigger mode - MCP agent-builder server (stdio + HTTP): read_sheet_values, upsert, discovery - Version bump to 1.2.0  ForgeChat's curated docs/CI (README, CONTRIBUTING, CHANGELOG, DEPLOY*, .github) are intentionally left untouched.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * docs(readme): add \"Build agents from Claude (MCP server)\" setup section  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * fix(ci): sync backend lock, guard agentConversation call; docs(skill): Phase 4 latest  - backend/package-lock.json regenerated to match package.json (MCP deps) so   `npm ci` passes - ChatWindow: guard api.agentConversation?.status?.() so the header never breaks   when the endpoint/api shape is absent (fixes ChatWindow.header unit tests) - SKILL.md Phase 4: drop \"(optional)\", add read_sheet_values + the Sheets   `upsert` op (recommended for logging)  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  ---------  Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>") | 2 weeks agoJun 10, 2026 |
| [TRADEMARK.md](https://github.com/Forgemind-git/ForgeChat/blob/main/TRADEMARK.md "TRADEMARK.md") | [TRADEMARK.md](https://github.com/Forgemind-git/ForgeChat/blob/main/TRADEMARK.md "TRADEMARK.md") | [docs(brand): align Meta / WhatsApp wording with BSP brand guidelines (](https://github.com/Forgemind-git/ForgeChat/commit/ce38b92a9ee683fcc5e12c3327e9c9f08288fddd "docs(brand): align Meta / WhatsApp wording with BSP brand guidelines (#40)  ForgeChat is a Meta Business Solution Provider integration, so all user-facing strings and docs need to follow the WhatsApp Brand Guidelines and Meta Brand Guidelines for Business Solution Providers. This commit fixes a set of phrasings that either implied Meta endorsement, treated Meta product names as our own, or used the deprecated \"WhatsApp Business API\" name.  Headline changes - README intro: drop \"official Meta WhatsApp Cloud API … not a risky   unofficial hack\". The \"official\" framing implies BSP-tier endorsement,   which ForgeChat does not claim; the \"unofficial hack\" line was also   editorial/disparaging toward other libraries. Rewrite as \"built on the   WhatsApp Cloud API (part of the WhatsApp Business Platform, hosted by   Meta) — the documented, ToS-compliant way to send and receive WhatsApp   business messages\". - Login splash: \"The unified WhatsApp Business platform for teams\"   reads as if ForgeChat *is* the WhatsApp Business Platform. Reword to   \"The unified team inbox for the WhatsApp Business Platform\" so the   Meta product is the underlying service and ForgeChat is the inbox. - TRADEMARK.md: add a new \"Third-Party Trademarks\" section that   acknowledges WhatsApp / WhatsApp Business / WhatsApp Business   Platform (WhatsApp LLC) and Meta / Meta Business Suite / Facebook /   Instagram (Meta Platforms, Inc.), and disclaims affiliation /   endorsement, as required by Meta's BSP brand guidelines. - README footer: add a matching one-paragraph affiliation disclaimer. - frontend/index.html <title>: \"ForgeChat — WhatsApp Chat Viewer\" reads   like a product-name claim. Switch to \"Inbox & CRM for WhatsApp   Business\" (descriptive use only).  Naming clean-ups - \"WhatsApp Business API\" → \"WhatsApp Cloud API\" (the umbrella name is   now WhatsApp Business Platform; the product we hit is Cloud API):   TemplateBuilderPage subtitle, AdminSettings credentials hint,   AutomationBuilderView direct-message warning. - \"WhatsApp account\" → \"WhatsApp Business account\" in user-facing   surfaces only (empty state, edit/add modal title, every error string   in routes/whatsappAccounts.js and services/messageSender.js). Code   identifiers, route paths, table names, and internal comments stay   untouched. - README: \"Meta WhatsApp Business account\" → \"WhatsApp Business   Account (managed in Meta Business Suite)\" (the grammatically correct   Meta product name). - AutomationBuilderView: remove the dev-mockup comment block that   called the file \"WhatsFlow AI — Premium WhatsApp Automation Builder\";   \"WhatsFlow\" starts with \"Whats\", which Meta's brand guide explicitly   warns against in third-party names. The file already ships in the   public repo, so the comment goes too.  No behavior changes — UI labels, error strings, and docs only. The preview phone frame, webhook field names, and \"by Meta\" actor mentions (\"approved by Meta\", \"rejected by Meta\", \"required by Meta\") stay as nominative use.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") [#…](https://github.com/Forgemind-git/ForgeChat/pull/40) | last monthMay 26, 2026 |
| [VERSIONING.md](https://github.com/Forgemind-git/ForgeChat/blob/main/VERSIONING.md "VERSIONING.md") | [VERSIONING.md](https://github.com/Forgemind-git/ForgeChat/blob/main/VERSIONING.md "VERSIONING.md") | [ForgeChat — initial public release](https://github.com/Forgemind-git/ForgeChat/commit/1b3af0df4eaab72cbdce1d6b443bb02dda934175 "ForgeChat — initial public release  Public, source-available release of ForgeChat, a full-stack WhatsApp CRM on the Meta WhatsApp Cloud API. Published with a fresh history; see CHANGELOG.md for the 1.0.1 feature set and the Sustainable Use License in LICENSE.md.  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com> Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | last monthMay 24, 2026 |
| [docker-compose.prod.yml](https://github.com/Forgemind-git/ForgeChat/blob/main/docker-compose.prod.yml "docker-compose.prod.yml") | [docker-compose.prod.yml](https://github.com/Forgemind-git/ForgeChat/blob/main/docker-compose.prod.yml "docker-compose.prod.yml") | [feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, te…](https://github.com/Forgemind-git/ForgeChat/commit/bb8a60d12069c05be13d67ed4d398c57e596afa1 "feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, template rendering (#55)  Sync the full application into the public repo for the official v1.1.0 release.  Added - AI agents that reply automatically: engine, builder UI, live preview, run   history, keyword/any-message/new-contact triggers, and media-send. - AI model connectors (OpenAI, Anthropic) with a Settings → AI Models tab. - Google integration (Sheets lookup + Drive). Client ID/Secret/redirect are   entered in Settings → Integrations and stored encrypted in the DB — no env files. - Voice-note understanding: incoming audio is transcribed and answered as text. - WhatsApp-style template rendering in chat & broadcast previews, including   {{1}} variable substitution and image headers. - Custom-text variables in bulk broadcasts. - Bundled docker-compose.yml (+ docker-compose.prod.yml overlay) so a fresh   clone runs with a single `docker compose up -d`, plus clearer macOS notes. - Server-sent events for live UI updates; boot-time migration runner.  Changed - Brand-language pass for Meta / WhatsApp guidelines (README, login splash,   TRADEMARK.md, affiliation disclaimer). - license-check CI: allow url-template@2.0.8 (BSD-3-Clause googleapis dep). - Versions bumped to 1.1.0; CHANGELOG updated.  Notes - README video preview kept unchanged (GIF tour + YouTube link). - All documentation/clone URLs point at the public ForgeChat repo.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | 3 weeks agoJun 4, 2026 |
| [docker-compose.sample.yml](https://github.com/Forgemind-git/ForgeChat/blob/main/docker-compose.sample.yml "docker-compose.sample.yml") | [docker-compose.sample.yml](https://github.com/Forgemind-git/ForgeChat/blob/main/docker-compose.sample.yml "docker-compose.sample.yml") | [ForgeChat — initial public release](https://github.com/Forgemind-git/ForgeChat/commit/1b3af0df4eaab72cbdce1d6b443bb02dda934175 "ForgeChat — initial public release  Public, source-available release of ForgeChat, a full-stack WhatsApp CRM on the Meta WhatsApp Cloud API. Published with a fresh history; see CHANGELOG.md for the 1.0.1 feature set and the Sustainable Use License in LICENSE.md.  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com> Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | last monthMay 24, 2026 |
| [docker-compose.yml](https://github.com/Forgemind-git/ForgeChat/blob/main/docker-compose.yml "docker-compose.yml") | [docker-compose.yml](https://github.com/Forgemind-git/ForgeChat/blob/main/docker-compose.yml "docker-compose.yml") | [feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, te…](https://github.com/Forgemind-git/ForgeChat/commit/bb8a60d12069c05be13d67ed4d398c57e596afa1 "feat: ForgeChat v1.1.0 — AI agents, LLM connectors, Google Sheets, template rendering (#55)  Sync the full application into the public repo for the official v1.1.0 release.  Added - AI agents that reply automatically: engine, builder UI, live preview, run   history, keyword/any-message/new-contact triggers, and media-send. - AI model connectors (OpenAI, Anthropic) with a Settings → AI Models tab. - Google integration (Sheets lookup + Drive). Client ID/Secret/redirect are   entered in Settings → Integrations and stored encrypted in the DB — no env files. - Voice-note understanding: incoming audio is transcribed and answered as text. - WhatsApp-style template rendering in chat & broadcast previews, including   {{1}} variable substitution and image headers. - Custom-text variables in bulk broadcasts. - Bundled docker-compose.yml (+ docker-compose.prod.yml overlay) so a fresh   clone runs with a single `docker compose up -d`, plus clearer macOS notes. - Server-sent events for live UI updates; boot-time migration runner.  Changed - Brand-language pass for Meta / WhatsApp guidelines (README, login splash,   TRADEMARK.md, affiliation disclaimer). - license-check CI: allow url-template@2.0.8 (BSD-3-Clause googleapis dep). - Versions bumped to 1.1.0; CHANGELOG updated.  Notes - README video preview kept unchanged (GIF tour + YouTube link). - All documentation/clone URLs point at the public ForgeChat repo.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | 3 weeks agoJun 4, 2026 |
| [install.ps1](https://github.com/Forgemind-git/ForgeChat/blob/main/install.ps1 "install.ps1") | [install.ps1](https://github.com/Forgemind-git/ForgeChat/blob/main/install.ps1 "install.ps1") | [fix(installer): map host port 80 to frontend in local mode (](https://github.com/Forgemind-git/ForgeChat/commit/9822e2e910925e0dc5c6d03c7b78801df8ded346 "fix(installer): map host port 80 to frontend in local mode (#41)  Both install.sh (local mode) and install.ps1 (always local) copy docker-compose.sample.yml as the deployment compose file and then start only forgecrm-backend + forgecrm-frontend — Caddy is intentionally unused locally. But docker-compose.sample.yml only maps host port 80 via the caddy service; forgecrm-frontend (nginx :80) has no ports mapping, so http://localhost never resolves on a fresh local install. Users had to manually add the port mapping to the gitignored docker-compose.yml.  Fix - install.sh, local mode: after copying the sample, idempotently inject        ports:         - \"80:80\"    into the forgecrm-frontend service block of the copied   docker-compose.yml using awk (portable between GNU and BSD/macOS sed). - install.ps1: do the same line-by-line in PowerShell after copying the   sample. The script is local-mode-only by design, so no branching.  Idempotency The check is scoped to forgecrm-frontend's own block — a naive file-wide grep for `- \"80:80\"` would false-positive on the existing caddy port mapping in the sample. The scoped check walks lines, marks \"in block\" between `forgecrm-frontend:` and the next top-level service, and only matches `- \"80:80\"` while inside that block.  Verified - awk injection produces valid YAML (`yaml.safe_load` round-trips   cleanly, forgecrm-frontend gains `ports: ['80:80']`, caddy keeps   `ports: ['80:80', '443:443']`). - Re-running the inject is a no-op (idempotent). - install.sh server mode is untouched — Caddy still owns host port 80   there.  Docs were already correct; this just makes the README's promise (\"Open http://localhost — it should load\") true for fresh installs.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") [#41](https://github.com/Forgemind-git/ForgeChat/pull/41) [)](https://github.com/Forgemind-git/ForgeChat/commit/9822e2e910925e0dc5c6d03c7b78801df8ded346 "fix(installer): map host port 80 to frontend in local mode (#41)  Both install.sh (local mode) and install.ps1 (always local) copy docker-compose.sample.yml as the deployment compose file and then start only forgecrm-backend + forgecrm-frontend — Caddy is intentionally unused locally. But docker-compose.sample.yml only maps host port 80 via the caddy service; forgecrm-frontend (nginx :80) has no ports mapping, so http://localhost never resolves on a fresh local install. Users had to manually add the port mapping to the gitignored docker-compose.yml.  Fix - install.sh, local mode: after copying the sample, idempotently inject        ports:         - \"80:80\"    into the forgecrm-frontend service block of the copied   docker-compose.yml using awk (portable between GNU and BSD/macOS sed). - install.ps1: do the same line-by-line in PowerShell after copying the   sample. The script is local-mode-only by design, so no branching.  Idempotency The check is scoped to forgecrm-frontend's own block — a naive file-wide grep for `- \"80:80\"` would false-positive on the existing caddy port mapping in the sample. The scoped check walks lines, marks \"in block\" between `forgecrm-frontend:` and the next top-level service, and only matches `- \"80:80\"` while inside that block.  Verified - awk injection produces valid YAML (`yaml.safe_load` round-trips   cleanly, forgecrm-frontend gains `ports: ['80:80']`, caddy keeps   `ports: ['80:80', '443:443']`). - Re-running the inject is a no-op (idempotent). - install.sh server mode is untouched — Caddy still owns host port 80   there.  Docs were already correct; this just makes the README's promise (\"Open http://localhost — it should load\") true for fresh installs.  Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | last monthMay 26, 2026 |
| [install.sh](https://github.com/Forgemind-git/ForgeChat/blob/main/install.sh "install.sh") | [install.sh](https://github.com/Forgemind-git/ForgeChat/blob/main/install.sh "install.sh") | [Sync working-copy code: AI agent suite + MCP server (v1.2.0) (](https://github.com/Forgemind-git/ForgeChat/commit/448091550d3167c0d0a51ea59cadafdcfe0b0477 "Sync working-copy code: AI agent suite + MCP server (v1.2.0) (#63)  * feat: sync working-copy code — AI agent suite + MCP server (v1.2.0)  Brings the latest /root/Forge-Chat working code into ForgeChat: - Sheets `upsert` op, CRM write-back tools, human handoff (escalate + keywords +   round-robin + pause/resume + chat take-over), auto-summary on close,   \"new conversations only\" trigger mode - MCP agent-builder server (stdio + HTTP): read_sheet_values, upsert, discovery - Version bump to 1.2.0  ForgeChat's curated docs/CI (README, CONTRIBUTING, CHANGELOG, DEPLOY*, .github) are intentionally left untouched.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * docs(readme): add \"Build agents from Claude (MCP server)\" setup section  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * fix(ci): sync backend lock, guard agentConversation call; docs(skill): Phase 4 latest  - backend/package-lock.json regenerated to match package.json (MCP deps) so   `npm ci` passes - ChatWindow: guard api.agentConversation?.status?.() so the header never breaks   when the endpoint/api shape is absent (fixes ChatWindow.header unit tests) - SKILL.md Phase 4: drop \"(optional)\", add read_sheet_values + the Sheets   `upsert` op (recommended for logging)  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  ---------  Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>") [#63](https://github.com/Forgemind-git/ForgeChat/pull/63) [)](https://github.com/Forgemind-git/ForgeChat/commit/448091550d3167c0d0a51ea59cadafdcfe0b0477 "Sync working-copy code: AI agent suite + MCP server (v1.2.0) (#63)  * feat: sync working-copy code — AI agent suite + MCP server (v1.2.0)  Brings the latest /root/Forge-Chat working code into ForgeChat: - Sheets `upsert` op, CRM write-back tools, human handoff (escalate + keywords +   round-robin + pause/resume + chat take-over), auto-summary on close,   \"new conversations only\" trigger mode - MCP agent-builder server (stdio + HTTP): read_sheet_values, upsert, discovery - Version bump to 1.2.0  ForgeChat's curated docs/CI (README, CONTRIBUTING, CHANGELOG, DEPLOY*, .github) are intentionally left untouched.  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * docs(readme): add \"Build agents from Claude (MCP server)\" setup section  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  * fix(ci): sync backend lock, guard agentConversation call; docs(skill): Phase 4 latest  - backend/package-lock.json regenerated to match package.json (MCP deps) so   `npm ci` passes - ChatWindow: guard api.agentConversation?.status?.() so the header never breaks   when the endpoint/api shape is absent (fixes ChatWindow.header unit tests) - SKILL.md Phase 4: drop \"(optional)\", add read_sheet_values + the Sheets   `upsert` op (recommended for logging)  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>  ---------  Co-authored-by: Claude Opus 4.8 <noreply@anthropic.com>") | 2 weeks agoJun 10, 2026 |
| [package-lock.json](https://github.com/Forgemind-git/ForgeChat/blob/main/package-lock.json "package-lock.json") | [package-lock.json](https://github.com/Forgemind-git/ForgeChat/blob/main/package-lock.json "package-lock.json") | [ForgeChat — initial public release](https://github.com/Forgemind-git/ForgeChat/commit/1b3af0df4eaab72cbdce1d6b443bb02dda934175 "ForgeChat — initial public release  Public, source-available release of ForgeChat, a full-stack WhatsApp CRM on the Meta WhatsApp Cloud API. Published with a fresh history; see CHANGELOG.md for the 1.0.1 feature set and the Sustainable Use License in LICENSE.md.  Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com> Signed-off-by: KingArthur000 <sathyaprakashelango@gmail.com>") | last monthMay 24, 2026 |
| View all files |

## Repository files navigation

[![ForgeChat Logo](https://github.com/Forgemind-git/ForgeChat/raw/main/frontend/public/forgemind-logo.gif)](https://github.com/Forgemind-git/ForgeChat/blob/main/frontend/public/forgemind-logo.gif)[![ForgeChat Logo](https://github.com/Forgemind-git/ForgeChat/raw/main/frontend/public/forgemind-logo.gif)](https://github.com/Forgemind-git/ForgeChat/blob/main/frontend/public/forgemind-logo.gif)[Open ForgeChat Logo in new window](https://github.com/Forgemind-git/ForgeChat/blob/main/frontend/public/forgemind-logo.gif)

# ForgeChat

[Permalink: ForgeChat](https://github.com/Forgemind-git/ForgeChat#forgechat)

**Your own WhatsApp Business inbox & CRM — running on your own server**

[What is it?](https://github.com/Forgemind-git/ForgeChat#-what-is-forgechat) •
[Features](https://github.com/Forgemind-git/ForgeChat#-what-you-can-do) •
[Deploy](https://github.com/Forgemind-git/ForgeChat#-deploy-it-yourself) •
[Connect WhatsApp](https://github.com/Forgemind-git/ForgeChat#-connect-your-whatsapp) •
[Use it](https://github.com/Forgemind-git/ForgeChat#-everyday-use) •
[Help](https://github.com/Forgemind-git/ForgeChat#-help--troubleshooting)

![Version](https://camo.githubusercontent.com/82607e69abe99314712caaca3e9c3d804b6290df91f9771848c2c84b1d6bf4b8/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f76657273696f6e2d312e312e302d626c75652e737667)![License](https://camo.githubusercontent.com/92f230bf95227a61c503688e2eb03902e7dd8e49760f64c9179a114f3bc6b22b/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6c6963656e73652d5375737461696e61626c652532305573652d677265656e2e737667)![fair-code](https://camo.githubusercontent.com/27175778df6e517b640e4f83497356dd777a7f9288b8e2c4252e0cca8acbcaf8/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f666169722d2d636f64652d2545322539432539332d627269676874677265656e2e737667)![No coding needed](https://camo.githubusercontent.com/a41afb7c89f49631b6e18d40410975928de9e9f64974061dea63af373ff5d7da/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f73657475702d6e6f253230636f64696e672532306e65656465642d737563636573732e737667)![Docker](https://camo.githubusercontent.com/bd576d25bf8581259e6423c54d4d7c85894ab86c8e400118dc3d4567000dbeea/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646f636b65722d72656164792d3234393645442e737667)

[![ForgeChat video tour](https://github.com/Forgemind-git/ForgeChat/raw/main/docs/forgechat-overview.gif)](https://youtu.be/tvYR0cGOj_4)[![ForgeChat video tour](https://github.com/Forgemind-git/ForgeChat/raw/main/docs/forgechat-overview.gif)](https://youtu.be/tvYR0cGOj_4)[Open ForgeChat video tour in new window](https://youtu.be/tvYR0cGOj_4)

▶ Video tour (above, no audio) — [watch the full version on YouTube](https://youtu.be/tvYR0cGOj_4) with narration.

Need a server to run it on? [**Get a Hostinger VPS at 20% off**](https://www.hostinger.com/in?REFERRALCODE=RZ8CONTACT7T) (affiliate link).

* * *

## 🤔 What is ForgeChat?

[Permalink: 🤔 What is ForgeChat?](https://github.com/Forgemind-git/ForgeChat#-what-is-forgechat)

**ForgeChat** is a free WhatsApp Business inbox and CRM that **you host yourself**. Instead of paying a monthly fee to a SaaS company that keeps all your customer chats on _their_ servers, you run ForgeChat on your own server — so **you own your data and your customer conversations**.

It connects to the **WhatsApp Cloud API** (part of the **WhatsApp Business Platform**, hosted by Meta) — the documented, ToS-compliant way to send and receive WhatsApp business messages — and gives your whole team a clean, chat-style screen to:

- 💬 **Reply to customers** from a shared team inbox
- 🗂️ **Keep a customer database** with tags, notes, and custom fields
- 📣 **Send bulk broadcasts** to many customers at once
- 🤖 **Build auto-replies** with a drag-and-drop builder (no coding)
- 🧠 **Let an AI agent reply for you** — connect an AI model and it answers customers automatically (voice notes included)
- 📋 **Track deals** on a sales pipeline board

> **You don't need to be a programmer to set this up.** If you can install Docker and copy-paste two commands, you can run ForgeChat. It takes about **5 minutes**.

* * *

## 📸 What it looks like

[Permalink: 📸 What it looks like](https://github.com/Forgemind-git/ForgeChat#-what-it-looks-like)

| Team Inbox | Auto-reply Builder |
| :-: | :-: |
| [![Chats](https://github.com/Forgemind-git/ForgeChat/raw/main/docs/ui-screenshots/11-chats-conversation.png)](https://github.com/Forgemind-git/ForgeChat/blob/main/docs/ui-screenshots/11-chats-conversation.png) | [![Automations](https://github.com/Forgemind-git/ForgeChat/raw/main/docs/ui-screenshots/04-automation-builder.png)](https://github.com/Forgemind-git/ForgeChat/blob/main/docs/ui-screenshots/04-automation-builder.png) |
| **Message Templates** | **Customer Database** |
| [![Templates](https://github.com/Forgemind-git/ForgeChat/raw/main/docs/ui-screenshots/08-template-builder-form.png)](https://github.com/Forgemind-git/ForgeChat/blob/main/docs/ui-screenshots/08-template-builder-form.png) | [![Contacts](https://github.com/Forgemind-git/ForgeChat/raw/main/docs/ui-screenshots/12-contacts.png)](https://github.com/Forgemind-git/ForgeChat/blob/main/docs/ui-screenshots/12-contacts.png) |
| **Bulk Broadcasts** | **Settings** |
| [![Bulk](https://github.com/Forgemind-git/ForgeChat/raw/main/docs/ui-screenshots/13-bulk-message.png)](https://github.com/Forgemind-git/ForgeChat/blob/main/docs/ui-screenshots/13-bulk-message.png) | [![Admin](https://github.com/Forgemind-git/ForgeChat/raw/main/docs/ui-screenshots/15-admin-general.png)](https://github.com/Forgemind-git/ForgeChat/blob/main/docs/ui-screenshots/15-admin-general.png) |
| **🧠 AI Agents** | **AI Agent Builder** |
| [![AI Agents](https://github.com/Forgemind-git/ForgeChat/raw/main/docs/ui-screenshots/22-ai-agents.png)](https://github.com/Forgemind-git/ForgeChat/blob/main/docs/ui-screenshots/22-ai-agents.png) | [![AI Agent Builder](https://github.com/Forgemind-git/ForgeChat/raw/main/docs/ui-screenshots/23-ai-agent-builder.png)](https://github.com/Forgemind-git/ForgeChat/blob/main/docs/ui-screenshots/23-ai-agent-builder.png) |

* * *

## ✨ What you can do

[Permalink: ✨ What you can do](https://github.com/Forgemind-git/ForgeChat#-what-you-can-do)

### 💬 Chat with customers

[Permalink: 💬 Chat with customers](https://github.com/Forgemind-git/ForgeChat#-chat-with-customers)

- A **shared team inbox** that looks just like WhatsApp
- Send and receive **text, photos, videos, voice notes, and documents**
- **Record voice notes** right inside the chat box
- React with emojis, reply to specific messages, and star important ones
- ForgeChat reminds you about WhatsApp's **24-hour reply rule** and suggests a template when needed

### 🗂️ Manage customers

[Permalink: 🗂️ Manage customers](https://github.com/Forgemind-git/ForgeChat#%EF%B8%8F-manage-customers)

- A full **contact list** with names and phone numbers
- Organize people with **color-coded tags and categories**
- Add your own **custom fields** (e.g. city, order number, plan)
- **Import contacts** from an Excel/CSV spreadsheet
- Track sales opportunities on a **deals pipeline (Kanban board)**

### 📣 Reach people at scale

[Permalink: 📣 Reach people at scale](https://github.com/Forgemind-git/ForgeChat#-reach-people-at-scale)

- Build approved **WhatsApp message templates** with a live phone preview
- Send **bulk broadcasts** (templates, text, links, images, video, audio, documents)
- Watch **live delivery status** for every recipient
- See **template performance** with charts and click stats

### 🤖 Automate replies

[Permalink: 🤖 Automate replies](https://github.com/Forgemind-git/ForgeChat#-automate-replies)

- A **drag-and-drop builder** for auto-replies — no coding
- Trigger flows on **keywords**, **any new message**, **new contacts**, and delivery/read events
- Every automation run is **logged** so you can see exactly what happened

### 🧠 AI agents that reply for you

[Permalink: 🧠 AI agents that reply for you](https://github.com/Forgemind-git/ForgeChat#-ai-agents-that-reply-for-you)

- Connect an **AI model** (OpenAI, Claude, and more) and let an agent **answer customers automatically**
- Shape its behaviour with a plain-English **system prompt**, conversation **context**, and **tools** — no coding
- It understands **voice notes** too — incoming audio is **transcribed** and answered like any text
- Let it **look things up in Google Sheets** and **send media** back to the customer
- Trigger on a **keyword** or let it handle **every chat**, with a session window so it can hold a multi-turn conversation
- **Test it in a live preview** before going live, and review **every run** step by step
- **Set it up in the app, not config files** — connect **Google (Sheets)** and your **AI model** under **Settings → Integrations**. A shop can link a live stock/price sheet so an agent instantly answers _"is this in stock?"_ or _"what's the price?"_ — no `.env` editing

### 🔐 Keep it secure & organized

[Permalink: 🔐 Keep it secure & organized](https://github.com/Forgemind-git/ForgeChat#-keep-it-secure--organized)

- **Team accounts** with roles — admins control who sees what
- Assign specific chats to specific team members
- Secure login, encrypted WhatsApp tokens, and protected access throughout

* * *

## 🚀 Deploy it yourself

[Permalink: 🚀 Deploy it yourself](https://github.com/Forgemind-git/ForgeChat#-deploy-it-yourself)

The only thing you need installed is **Docker** — everything else (secure keys, database, tables) is set up automatically on first start. Pick how you want to run it:

| Run on | Best for |
| --- | --- |
| 🍎 **macOS** | Trying it on your own Mac |
| 🪟 **Windows** | Trying it on your own PC |
| 🖥️ **Server** | Real 24/7 use with your own domain + HTTPS |

> 🍎 **Mac** and 🪟 **Windows** run locally with **Docker Desktop** — perfect for testing and demos. To send and receive **real WhatsApp messages** you need a public `https://` address, so for production use the 🖥️ **Server** path below.

### 🍎 macOS

[Permalink: 🍎 macOS](https://github.com/Forgemind-git/ForgeChat#-macos)

1. Install **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (pick the **Apple Silicon** or **Intel** build to match your Mac).
2. **Open Docker Desktop and wait until it says "Engine running"** (bottom-left). `docker compose` can't start anything until the engine is up.
3. In **Terminal**, run:



```
git clone https://github.com/Forgemind-git/ForgeChat.git
cd ForgeChat
docker compose up -d
# then print the exact address to open:
echo "ForgeChat is running at http://localhost:$(docker compose port forgecrm-frontend 80 | cut -d: -f2)"
```

4. Open the **[http://localhost:…](http://localhost:%E2%80%A6/)** address the last command printed (default **[http://localhost:8080](http://localhost:8080/)**), and create your admin account right in the browser.

No config files, no secrets, no database commands — ForgeChat creates its own secure keys and sets up its database automatically. The first launch builds the app, so give it a minute. Want a different port? `HTTP_PORT=9000 docker compose up -d`.

> **Want real WhatsApp messages on this local install?** You'll start one free Cloudflare Tunnel command so Meta can reach your webhook — see **[Connect your WhatsApp](https://github.com/Forgemind-git/ForgeChat#-connect-your-whatsapp)** below. Keep using the app at `http://localhost:8080`.

### 🪟 Windows

[Permalink: 🪟 Windows](https://github.com/Forgemind-git/ForgeChat#-windows)

1. Install **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (keep **WSL 2** ticked) and **[Git for Windows](https://git-scm.com/download/win)** (click _Next_ through the installer), then restart your PC.
2. **Open Docker Desktop and wait until it says "Engine running"** (bottom-left) before continuing — `docker compose` can't start anything until the engine is up.
3. In **PowerShell**, run:



```
git clone https://github.com/Forgemind-git/ForgeChat.git
cd ForgeChat
docker compose up -d
# then print the exact address to open:
"ForgeChat is running at http://localhost:$((docker compose port forgecrm-frontend 80).Split(':')[-1].Trim())"
```

4. Open the **[http://localhost:…](http://localhost:%E2%80%A6/)** address the last command printed (default **[http://localhost:8080](http://localhost:8080/)**), and create your admin account right in the browser.

No config files, no secrets, no database commands — ForgeChat sets everything up on first start. The first launch builds the app, so give it a minute. Want a different port? `$env:HTTP_PORT=9000; docker compose up -d`.

> **Want real WhatsApp messages on this local install?** You'll start one free Cloudflare Tunnel command so Meta can reach your webhook — see **[Connect your WhatsApp](https://github.com/Forgemind-git/ForgeChat#-connect-your-whatsapp)** below. Keep using the app at `http://localhost:8080`.

### 🖥️ Server — your own domain with automatic HTTPS

[Permalink: 🖥️ Server — your own domain with automatic HTTPS](https://github.com/Forgemind-git/ForgeChat#%EF%B8%8F-server--your-own-domain-with-automatic-https)

This is the **production** path. To actually **send and receive WhatsApp messages**, the app needs a public web address (`https://…`) that Meta can reach — a plain `localhost` install can't receive messages.

1. Rent a small server ( **2 GB+ RAM**) with ports **80** and **443** free — e.g. a **[Hostinger VPS at 20% off](https://www.hostinger.com/in?REFERRALCODE=RZ8CONTACT7T)** (affiliate link).
2. Register a domain you own and point its DNS **A record** at the server's IP address.
3. Install Docker (`curl -fsSL https://get.docker.com | sh`), then clone and run the installer:



```
git clone https://github.com/Forgemind-git/ForgeChat.git
cd ForgeChat
./install.sh
```







It asks for your domain, checks that DNS and the ports are ready, then starts everything. That's it.

A secure HTTPS certificate is obtained and renewed **automatically**. Open **[https://your-domain](https://your-domain/)**, create your admin account, then connect WhatsApp (below).

Prefer to run it yourself without the installer?

```
DOMAIN=chat.yourbusiness.com docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

The installer is just a friendly wrapper around this command plus DNS/port pre-checks.

> ⚠️ **Keep the `secrets` volume.** ForgeChat stores its encryption key there. If you delete it, saved WhatsApp tokens can no longer be decrypted and you'll have to reconnect WhatsApp.

### Optional settings

[Permalink: Optional settings](https://github.com/Forgemind-git/ForgeChat#optional-settings)

Everything works out of the box. If you want to override something (database password, port, or feature keys like an LLM provider for AI agents), create a `.env` file next to `docker-compose.yml` — see [`backend/.env.example`](https://github.com/Forgemind-git/ForgeChat/blob/main/backend/.env.example). None of it is required.

* * *

## 📱 Connect your WhatsApp

[Permalink: 📱 Connect your WhatsApp](https://github.com/Forgemind-git/ForgeChat#-connect-your-whatsapp)

To send and receive real messages, link your **WhatsApp Business Account**. You need two things: a **public HTTPS address** Meta can reach, and your **Meta account details**. It's a one-time setup.

### Step 1 — Get a public address Meta can reach

[Permalink: Step 1 — Get a public address Meta can reach](https://github.com/Forgemind-git/ForgeChat#step-1--get-a-public-address-meta-can-reach)

Meta delivers incoming messages to a **webhook**, so it needs a public `https://` URL.

- 🖥️ **Server install:** you already have one — your domain (e.g. `https://chat.yourbusiness.com`). **Skip to Step 2.**

- 🍎🪟 **Local install (Mac/Windows):**`localhost` isn't reachable from the internet, so start the **built-in Cloudflare Tunnel** — no account, nothing to install, it runs as a container. From the `ForgeChat` folder:



```
docker compose --profile tunnel up -d
docker compose logs -f tunnel
```







The log keeps streaming; within a few seconds it prints a line like `https://two-cats-run.trycloudflare.com` — that's your **public URL** for Step 3. Copy it, then press **Ctrl+C** to stop watching. (Use `-f` as shown: plain `docker compose logs tunnel` often runs the split-second _before_ the URL is ready, which is why it can look empty the first time.)


> ⚠️ **Log in and use the app at `http://localhost:8080`** — _not_ the `…trycloudflare.com` URL. The tunnel exists only so Meta can reach your webhook; opening the app through it fails with a CORS error on login.
> ℹ️ The tunnel URL changes whenever you restart it; if it changes, update the **Callback URL** in Meta (Step 3). Stop it later with `docker compose --profile tunnel down`. _(Prefer ngrok? It works too, but needs a free account + authtoken — the built-in tunnel is the quickest start.)_


### Step 2 — Add the account in ForgeChat

[Permalink: Step 2 — Add the account in ForgeChat](https://github.com/Forgemind-git/ForgeChat#step-2--add-the-account-in-forgechat)

1. **Log in** to ForgeChat (at `http://localhost:8080`, or your domain) → **Settings** → **WhatsApp Accounts** → **Add**.
2. From the [Meta Business dashboard](https://business.facebook.com/) (your app → **WhatsApp → API Setup**), copy these into the form: **Phone Number ID**, **WABA ID**, **Meta App ID**, and a **Meta access token**. Also make up a **verify token** — any random text (you'll paste the _same_ value into Meta in Step 3). ForgeChat encrypts the access token and **auto-detects your business phone number and name from Meta** using that token — so make sure it's valid (a _test number_'s token from the API Setup page expires after 24 hours).

### Step 3 — Point Meta's webhook at ForgeChat

[Permalink: Step 3 — Point Meta's webhook at ForgeChat](https://github.com/Forgemind-git/ForgeChat#step-3--point-metas-webhook-at-forgechat)

In the **Meta dashboard** → **WhatsApp → Configuration → Webhook → Edit**:

- **Callback URL:** your **public URL** from Step 1, followed by `/api/webhook/whatsapp`
  - Local example: `https://two-cats-run.trycloudflare.com/api/webhook/whatsapp`
  - Server example: `https://chat.yourbusiness.com/api/webhook/whatsapp`
  - ⚠️ On a local install, **ignore the `http://localhost…` URL the ForgeChat form shows** — Meta can't reach localhost. Use your **tunnel** address here instead.
- **Verify token:** the exact verify token you entered in ForgeChat (Step 2).
- Click **Verify and save** — Meta calls your webhook to confirm it (ForgeChat and the tunnel must be running).
- **Subscribe to these webhook fields** (under _WhatsApp Business Account_):

  - `messages` — incoming messages + delivery/read statuses _(required)_
  - `message_template_status_update` — template approved / rejected / paused by Meta
  - `message_template_quality_update` — template quality rating changes (GREEN / YELLOW / RED)
  - `message_template_components_update` — edits to an approved template's content
  - `template_category_update` — Meta re-categorises a template
  - `template_correct_category_detection` — Meta's suggested correct category
  - `smb_message_echoes` — copies of messages your team sends from the WhatsApp app, so they also appear in ForgeChat (coexistence)

**Verify it works:** send a real WhatsApp message from your phone to the business number — it should appear in **Chats** within seconds, and your reply from ForgeChat should arrive back on your phone.

> ℹ️ You can explore the whole app (inbox, contacts, automations, templates) **before** connecting WhatsApp — you just won't send/receive real messages until this step is done.

* * *

## 🧭 Everyday use

[Permalink: 🧭 Everyday use](https://github.com/Forgemind-git/ForgeChat#-everyday-use)

| You want to… | Go to… |
| --- | --- |
| Reply to customers | **Chats** |
| Add or edit customers, tags, custom fields | **Contacts** |
| Create approved WhatsApp templates | **Template Builder** |
| Send a message to many people at once | **Bulk Message** |
| Set up keyword auto-replies | **Automations** |
| Set up an AI agent that replies for you | **AI Agents** |
| Track sales/deals | **Pipelines** |
| Add team members & control access | **Settings → Users** |

* * *

## 🔌 Build agents from Claude (MCP server)

[Permalink: 🔌 Build agents from Claude (MCP server)](https://github.com/Forgemind-git/ForgeChat#-build-agents-from-claude-mcp-server)

ForgeChat ships an **MCP server** so you can **build and manage your WhatsApp AI agents by chatting with Claude** (Claude Desktop, or any MCP client) — it asks what you need, looks up your real WhatsApp numbers, AI models, Google Sheets, media and templates, and creates a fully-configured agent for you. No dashboard required.

### Step 1 — Turn it on and get a key

[Permalink: Step 1 — Turn it on and get a key](https://github.com/Forgemind-git/ForgeChat#step-1--turn-it-on-and-get-a-key)

In ForgeChat, open **Settings → MCP Tools**:

1. Flip the **master switch** on, and enable the **capabilities** you want (discovery, create/update agents, manage tools, delete).
2. Click **Generate key** and copy the `fck_live_…` value — it's shown **once**.

### Step 2 — Connect Claude (pick one)

[Permalink: Step 2 — Connect Claude (pick one)](https://github.com/Forgemind-git/ForgeChat#step-2--connect-claude-pick-one)

**A) Remote — just a URL (easiest)**
The MCP Tools page shows a ready-to-paste connect URL:

```
https://your-domain/api/mcp/http/<your-key>
```

In Claude (web/desktop/mobile) → **Settings → Connectors → Add custom connector** → paste that URL. Done.

**B) Local — run the bundled server**
Use the server in [`mcp-server/`](https://github.com/Forgemind-git/ForgeChat/blob/main/mcp-server) (`npm install` once), then add this to your `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`, Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```
{
  "mcpServers": {
    "forgechat-agents": {
      "command": "node",
      "args": ["/path/to/ForgeChat/mcp-server/src/index.js"],
      "env": {
        "FORGECHAT_API_URL": "https://your-domain/api/mcp/v1",
        "FORGECHAT_API_KEY": "fck_live_PASTE_YOUR_KEY"
      }
    }
  }
}
```

### Step 3 — Use it

[Permalink: Step 3 — Use it](https://github.com/Forgemind-git/ForgeChat#step-3--use-it)

Fully quit and reopen Claude, then say **“create a ForgeChat agent”** — it walks you through the setup questions and builds the agent. Each capability is gated by the toggles in **Settings → MCP Tools** (a disabled one returns a clear error), and the key can be revoked any time from the same page.

> Replace `your-domain` with wherever ForgeChat is hosted. The bearer key works over the internet; your ForgeChat login cookie is never involved. See [`mcp-server/README.md`](https://github.com/Forgemind-git/ForgeChat/blob/main/mcp-server/README.md) for the full tool list and debugging tips.

* * *

## 🔄 Keeping it running

[Permalink: 🔄 Keeping it running](https://github.com/Forgemind-git/ForgeChat#-keeping-it-running)

**Update to the latest version** (run on your server, inside the `ForgeChat` folder):

```
git pull
docker compose up -d --build         # add the prod overlay flags if you use a domain
```

New database changes are applied automatically on start — nothing else to run.

**Back up your data** (highly recommended — set up a daily automatic backup):

```
mkdir -p ~/backups
crontab -e
# add this line to back up every day at 3 AM and keep 7 days:
0 3 * * * cd ~/ForgeChat && docker compose exec -T forgecrm-db pg_dump -U postgres postgres | gzip > ~/backups/forgechat-$(date +\%Y\%m\%d).sql.gz && find ~/backups -name '*.sql.gz' -mtime +7 -delete
```

> Also keep the `secrets` volume safe — it holds the key that decrypts your stored WhatsApp tokens.

* * *

## 🆘 Help & Troubleshooting

[Permalink: 🆘 Help & Troubleshooting](https://github.com/Forgemind-git/ForgeChat#-help--troubleshooting)

| Problem | What to do |
| --- | --- |
| **`This site can't be reached` / `exec format error` (Apple Silicon Mac)** | If `localhost:8080` won't load and `docker compose logs forgecrm-frontend` shows `exec /docker-entrypoint.sh: exec format error`, Docker Desktop's **containerd image store** built the web image for the wrong CPU. One-time fix: open **Docker Desktop → Settings → General**, **uncheck** "Use containerd for pulling and storing images", click **Apply & Restart**, then rebuild: `docker compose build --no-cache && docker compose up -d`. |
| **`The system cannot find the file specified` / `pipe/dockerDesktopLinuxEngine` (Windows or Mac)** | Docker Desktop isn't running. Open it and wait for **"Engine running"**, then re-run `docker compose up -d`. Confirm the engine is reachable with `docker version` — the **Server:** section must appear (not just **Client:**). If Docker Desktop won't start on Windows, the **WSL 2** backend is likely missing: run `wsl --install` in an **Administrator** PowerShell, restart, and try again. |
| **Login fails with `500` when opening the `…trycloudflare.com` URL** | You're browsing the app through the tunnel — use **`http://localhost:8080`** instead. The tunnel is only for Meta's webhook; logging in through it is blocked by CORS. |
| **WhatsApp connected but no chats appear** | ForgeChat auto-detects your business number from Meta using the access token — if that token was invalid/expired when you connected, the number stays blank and chats for it are hidden (they're still saved). Fix: **Settings → WhatsApp Accounts → edit → paste a valid access token → Save** to re-fetch it. Received messages then appear immediately. |
| **No tunnel URL in the logs** | The URL prints a few seconds _after_ the tunnel starts, so watch it in **follow mode**: `docker compose logs -f tunnel`, wait for the `https://…trycloudflare.com` line, then press Ctrl+C. (Plain `docker compose logs tunnel` can run before it's printed — that's why it looks empty the first time.) |
| **The page won't load (production)** | Your domain may not point to the server yet. Double-check the DNS "A record", wait a few minutes, then refresh. |
| **"502" error or blank screen** | The app may still be starting. Wait a minute, then check the logs: `docker compose logs forgecrm-backend`. |
| **Can't log in** | Use the admin email/password you created in the setup screen. Forgot it? An admin can reset it under **Settings → Users**. |
| **Build got "Killed" / "out of memory"** | The build ran out of RAM. Use **2 GB+**, or add swap and rebuild: `fallocate -l 2G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile`. |
| **Messages aren't arriving** | Re-check the **webhook** in the Meta dashboard: subscribe to `messages`, make sure the **Callback URL ends with `/api/webhook/whatsapp`**, and the **Verify token matches exactly** what you entered in ForgeChat (no extra spaces). |
| **Changed an optional `.env` setting** | Re-create the containers so they pick up the new values: `docker compose up -d`. |
| **HTTPS certificate won't issue (production)** | DNS isn't pointing at the server yet. Check with `dig +short chat.yourbusiness.com` (should return your server IP), then `docker compose -f docker-compose.yml -f docker-compose.prod.yml restart caddy`. |
| **Reconnected WhatsApp after a reset and tokens are gone** | The `secrets` volume (encryption key) was likely removed. Re-enter the WhatsApp access token in **Settings → WhatsApp Accounts**. |
| **Is my data safe?** | Yes — everything lives on _your_ server. WhatsApp tokens are encrypted, and access is protected by login. Just keep your backups (above). |

Still stuck? Open an issue on [GitHub](https://github.com/Forgemind-git/ForgeChat/issues) and we'll help.

* * *

## 🔒 Security

[Permalink: 🔒 Security](https://github.com/Forgemind-git/ForgeChat#-security)

- Everything runs on **your** server — your data never leaves it.
- WhatsApp access tokens are **encrypted** at rest (AES-256-GCM).
- Login uses secure httpOnly cookies; passwords are hashed with bcrypt.
- Incoming webhooks are verified with Meta's signature so fake messages are rejected.
- The API is protected with rate limiting, security headers, and parameterized database queries.

Found a security issue? Please report it privately — see **[SECURITY.md](https://github.com/Forgemind-git/ForgeChat/blob/main/SECURITY.md)**. Don't open a public issue.

* * *

## 🤝 Contributing

[Permalink: 🤝 Contributing](https://github.com/Forgemind-git/ForgeChat#-contributing)

Contributions are welcome! See **[CONTRIBUTING.md](https://github.com/Forgemind-git/ForgeChat/blob/main/CONTRIBUTING.md)** for setup and conventions, and the **[CODE\_OF\_CONDUCT.md](https://github.com/Forgemind-git/ForgeChat/blob/main/CODE_OF_CONDUCT.md)**. Release history is in **[CHANGELOG.md](https://github.com/Forgemind-git/ForgeChat/blob/main/CHANGELOG.md)**.

* * *

## 📄 License

[Permalink: 📄 License](https://github.com/Forgemind-git/ForgeChat#-license)

ForgeChat is [**fair-code**](https://faircode.io/) distributed under the **[Sustainable Use License](https://github.com/Forgemind-git/ForgeChat/blob/main/LICENSE.md)**.

- ✅ Use it for your own business, personal, or non-commercial purposes.
- ✅ Share it free of charge for non-commercial purposes.
- ❌ No reselling or paid hosting as a service without permission.

Copyright © 2026 **Forgemind Techhub LLP**. **Forgemind AI** is a trademark of Forgemind Techhub LLP — see **[TRADEMARK.md](https://github.com/Forgemind-git/ForgeChat/blob/main/TRADEMARK.md)**.

> **WhatsApp** is a trademark of WhatsApp LLC. **Meta** is a trademark of Meta Platforms, Inc. ForgeChat is an independent application that connects to the WhatsApp Cloud API (hosted by Meta), and is **not** affiliated with, endorsed by, sponsored by, or otherwise officially connected to Meta Platforms, Inc. or WhatsApp LLC.

* * *

**ForgeChat** — own your inbox.

Made with ❤️ by [Forgemind](https://github.com/Forgemind-git)

## About

Self-hostable, source-available WhatsApp CRM built on the Meta WhatsApp Cloud API — chats, contacts, templates, broadcasts, and a visual automation builder.


### Topics

[react](https://github.com/topics/react "Topic: react") [nodejs](https://github.com/topics/nodejs "Topic: nodejs") [express](https://github.com/topics/express "Topic: express") [postgresql](https://github.com/topics/postgresql "Topic: postgresql") [crm](https://github.com/topics/crm "Topic: crm") [self-hosted](https://github.com/topics/self-hosted "Topic: self-hosted") [whatsapp](https://github.com/topics/whatsapp "Topic: whatsapp") [fair-code](https://github.com/topics/fair-code "Topic: fair-code") [whatsapp-cloud-api](https://github.com/topics/whatsapp-cloud-api "Topic: whatsapp-cloud-api")

### Resources

[Readme](https://github.com/Forgemind-git/ForgeChat#readme-ov-file)

### License

[View license](https://github.com/Forgemind-git/ForgeChat#License-1-ov-file)

### Code of conduct

[Code of conduct](https://github.com/Forgemind-git/ForgeChat#coc-ov-file)

### Contributing

[Contributing](https://github.com/Forgemind-git/ForgeChat#contributing-ov-file)

### Security policy

[Security policy](https://github.com/Forgemind-git/ForgeChat#security-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Forgemind-git/ForgeChat).

[Activity](https://github.com/Forgemind-git/ForgeChat/activity)

[Custom properties](https://github.com/Forgemind-git/ForgeChat/custom-properties)

### Stars

[**31**\\
stars](https://github.com/Forgemind-git/ForgeChat/stargazers)

### Watchers

[**1**\\
watching](https://github.com/Forgemind-git/ForgeChat/watchers)

### Forks

[**11**\\
forks](https://github.com/Forgemind-git/ForgeChat/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FForgemind-git%2FForgeChat&report=Forgemind-git+%28user%29)

## [Releases\  4](https://github.com/Forgemind-git/ForgeChat/releases)

[v1.2.1 — Media-template broadcast fix\\
Latest\\
\\
last weekJun 17, 2026](https://github.com/Forgemind-git/ForgeChat/releases/tag/v1.2.1)

[\+ 3 releases](https://github.com/Forgemind-git/ForgeChat/releases)

## [Packages\  2](https://github.com/orgs/Forgemind-git/packages?repo_name=ForgeChat)

- [forgechat-backend](https://github.com/orgs/Forgemind-git/packages/container/package/forgechat-backend)
- [forgechat-frontend](https://github.com/orgs/Forgemind-git/packages/container/package/forgechat-frontend)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/Forgemind-git/ForgeChat).

## [Contributors\  5](https://github.com/Forgemind-git/ForgeChat/graphs/contributors)

- [![@sathyaprakash000](https://avatars.githubusercontent.com/u/55381501?s=64&v=4)](https://github.com/sathyaprakash000)
- [![@claude](https://avatars.githubusercontent.com/u/81847?s=64&v=4)](https://github.com/claude)
- [![@sthirumalairajan2212](https://avatars.githubusercontent.com/u/92260025?s=64&v=4)](https://github.com/sthirumalairajan2212)
- [![@dependabot[bot]](https://avatars.githubusercontent.com/in/29110?s=64&v=4)](https://github.com/apps/dependabot)
- [![@madesh6554](https://avatars.githubusercontent.com/u/128010884?s=64&v=4)](https://github.com/madesh6554)

## Languages

- [JavaScript99.2%](https://github.com/Forgemind-git/ForgeChat/search?l=javascript)
- Other0.8%

You can’t perform that action at this time.