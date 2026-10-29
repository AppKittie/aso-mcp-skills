# AppKittie ChatGPT plugin

The plugin combines AppKittie research tools with a focused research skill.
Its worker stays on Cloudflare. The upload ZIP contains connection settings,
listing metadata, the skill, and the existing AppKittie icon.

## Build and verify

From the MCP repository:

```bash
npm run plugin:build
npm test
```

The build writes `dist/appkittie-chatgpt-0.1.0.zip` and a SHA-256 checksum.
It uses an explicit file allowlist, fixed ZIP timestamps, and no source code,
environment files, credentials, or local marketplace configuration.

Edit `appkittie/plugin.json`, `appkittie/mcp.json`, and the skill as source.
The build regenerates `.codex-plugin/plugin.json` and `.mcp.json` compatibility
files. The portable manifest carries the review scenarios and listing metadata.
Never put client secrets or API keys in either MCP configuration.

In the frontend repository, run:

```bash
node --experimental-test-module-mocks --import tsx --test src/server/mcp-oauth/core.test.ts src/server/mcp-oauth/routes.test.ts
npm run typecheck
```

The route tests exercise sign-in redirects, consent, code exchange, API identity
resolution, permission changes, and revocation with mocked account/database/Redis
services. They do not substitute for testing the deployed connection in ChatGPT.

## Authentication and existing API keys

Users sign in through the existing AppKittie login, choose a team, and explicitly
approve access. Only team owners and admins can authorize a connection. The
consent screen explains saved-app access, API credits, and subscription limits.

Approval creates a `ChatGPT connection` row in the existing `api_key` table.
The row supplies the existing team identity, billing context, request-log foreign
key, and revocation controls. Its random hash has no issued API-key equivalent.
Existing API keys cannot be recovered from their hashes and are never fetched or
copied into the connection.

OAuth access and refresh tokens are opaque, stored by hash in Redis, and mapped
to that grant. Access lasts one hour; refresh tokens rotate and the grant expires
after 30 days. Reusing a refresh token revokes the grant. A lost Redis record
requires reconnection. No database migration or new runtime dependency is needed.
Configure Redis persistence and retention to keep connections available.

The API checks issuer, resource, expiry, scope, grant revocation, and current team
permissions before accepting an OAuth token. Only an explicit set of research
endpoints accepts the read scope, including the review/keyword POST endpoints.
Existing subscription, credit, and rate-limit checks still run. Deleting or
revoking the connection in **Settings → API keys** invalidates its tokens;
removing or demoting its authorizing team member also removes access.

The existing API-key endpoint remains `https://mcp.appkittie.com/mcp`.
The plugin uses the separate OAuth endpoint
`https://mcp.appkittie.com/chatgpt/mcp`. It advertises per-tool security schemes,
validates tokens before protected calls, and returns OAuth challenges for invalid
connections. Supported-country discovery remains public. The old Claude OAuth
shim is not used for the ChatGPT connection.

## Deploy and connect

1. Deploy the frontend changes, including the OAuth routes, API authentication
   adapter, and environment schema. The canonical production issuer is
   `https://www.appkittie.com`; the existing `DATABASE_URL`, `REDIS_URL`, and
   sign-in configuration are required.
2. In ChatGPT, add a custom MCP server using the new `/chatgpt/mcp` endpoint.
   Configure OAuth client ID `appkittie-chatgpt`, public-client authentication
   (`none`), and scope `appkittie:read`. No client secret is used.
3. Copy the exact HTTPS callback URL displayed by ChatGPT. Set frontend
   `MCP_OAUTH_REDIRECT_URIS` to that value. When the submission portal displays
   another callback, add it to the same comma-separated list. Apply the setting
   through the frontend's normal deployment process. No callbacks are accepted
   while this variable is empty; there are no wildcard redirects.
4. Deploy the MCP worker with the repository's normal `npm run deploy` command.
   Confirm the production hostname routes to this worker.
5. Connect in ChatGPT, sign in on AppKittie, select a team with API access and
   credits, and approve. Run all five positive and three negative scenarios in
   `appkittie/plugin.json`. Verify a protected tool requires reconnection after
   revoking the connection in AppKittie settings.

Deployment is a two-service change. Deploying the ZIP alone does not install
the frontend OAuth routes or update the Cloudflare worker. The package is built
locally; production deployment and a live ChatGPT sign-in test are still needed.

## Upload and review

Upload the ZIP through the OpenAI Platform Plugins dashboard under the verified
AppKittie publishing identity. The MCP server is declared in the initial ZIP.
Complete the connection and domain verification steps shown in the portal.

For domain verification, set the worker's `OPENAI_APPS_CHALLENGE` variable to the
exact challenge token shown by the portal. The worker serves it as plain text at
`https://mcp.appkittie.com/.well-known/openai-apps-challenge`. This is a public
verification value, not a credential. No token is included in the source package.

Before submitting for public review:

- Confirm the listing's privacy and terms URLs are accessible and accurately
  describe the integration's data handling.
- Provide a dedicated reviewer account with an eligible team, API credits, and
  representative data. Arrange a reviewer login that meets the portal's current
  requirements; the application's Google/email sign-in may need a supported
  reviewer-access arrangement. Keep credentials outside the ZIP.
- Run and record the supplied review scenarios against the deployed service.
  Record a video demonstration and add its accessible URL as
  `extensions.com.openai.review.demo_recording_url` in `appkittie/plugin.json`,
  then rebuild. The sample scenarios are prepared, not recorded live results.
- Resolve the portal's metadata, authentication, skill, and tool findings; submit
  for review. Publish only after approval.

The local ZIP validator checks package structure and configuration. OpenAI's
portal is authoritative for submission acceptance and review eligibility.

Official references: [package format](https://developers.openai.com/plugins/build/plugins),
[authentication](https://developers.openai.com/plugins/build/auth),
[testing](https://developers.openai.com/plugins/deploy/connect-chatgpt), and
[submission](https://developers.openai.com/plugins/deploy/submission).
