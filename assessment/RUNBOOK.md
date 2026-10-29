# Run and review

All data used by the tests and demo is synthetic. Keep runtime files, tokens and candidate data out of Git.

## Windows runtime prepared in this folder

The hidden `.runtime` folder contains isolated dependencies used during verification. It is excluded from commits and the source archive. The PostgreSQL test port is 54329; the web port is 5173; the API port is 3001. No system database service is installed.

See the verified results in `verification.json` and the command logs in this folder. A passing browser fixture test is not a live Gemini or audio interview test.

## Standard setup

Follow `api/README.md` and `web/README.md`. Use Ruby 3.3.2, PostgreSQL 16 and Redis. Supply your own local signing secret and Gemini credentials through environment variables. Do not commit them.

```powershell
cd api
bundle install
bundle exec rails db:prepare
bundle exec rails runner db/evidence_demo.rb
bundle exec rails server -p 3001
```

The optional seed uses a deterministic injected model response and runs the real validator and persistence pipeline. It does not call Gemini. It writes a local demo token and the review URL path to `api/tmp/evidence-demo.json`. Set the frontend `VITE_DEV_TOKEN` to that token in an ignored `.env.local`, and set `VITE_API_BASE_URL=http://localhost:3001/api/v1`.

```powershell
cd web
npm ci
npm run dev
```

For actual portfolio generation, start Redis and the Sidekiq worker and configure your own provider key. Standalone password login is disabled by default. The synthetic seed token lets reviewers inspect this slice without enabling it. Production must use a trusted organization sign-in issuer; `ALLOW_LOCAL_LOGIN=true` is restricted to the development environment.

## Docker alternative

Docker is optional and was not available on this host. `compose.yml` binds public app ports to localhost. Its trust-auth database has no published host port and is for local development only. Do not deploy it as a production configuration.

Set `SECRET_KEY_BASE` in your shell, then:

```sh
docker compose build api
docker compose run --rm api bundle exec rails db:prepare
docker compose up -d api worker web
docker compose exec api bundle exec rails runner db/evidence_demo.rb
docker compose cp api:/app/tmp/evidence-demo.json api/tmp/evidence-demo.json
```

Copy the locally generated demo token from the API container into an ignored frontend environment file. Use your own key for live model calls.

## Verification

```sh
cd api
RAILS_ENV=test bundle exec rails db:prepare
bundle exec rspec --format documentation
cd ../web
npm test
npm run build
npx playwright install chromium
npm run test:e2e
```

On Windows the browser tests use installed Chrome. On CI they use Playwright Chromium. Browser fixtures deliberately simulate loading, failure and partial evidence; live API verification is recorded separately.
