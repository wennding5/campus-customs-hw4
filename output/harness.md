# Campus Customs implementation harness

## System overview

Campus Customs is a React 18 + Vite + TypeScript storefront backed by FastAPI, SQLite, and a PydanticAI shopping agent. The browser uses relative `/api` and `/images` URLs; Vite proxies both to FastAPI during development. FastAPI owns product access, authentication, chat memory, trusted page/customer context, agent execution, and static product-image delivery.

The agent uses OpenAI through Portkey with model `gpt-5.6-luna`. `backend/agent.py` loads `PORTKEY_API_KEY` from the project-root `.env`, with the enclosing course-workspace `.env` retained as a local fallback; keys are never returned to the browser or written to the audit trail. Optional `PORTKEY_BASE_URL`, `PORTKEY_PROVIDER`, and `PORTKEY_MODEL` environment variables can override defaults.

## Database and catalogue

`data/campus_customs.db` contains:

- `catalogue`: `product_id`, `name`, `garment_type`, `description`, JSON `colors`, JSON `search_tags`, `image_file_path`, and `price`. It contains 102 products.
- `inventory`: row ID, catalogue `product_id`, `size`, and nonnegative `quantity`. Its foreign key and unique `(product_id, size)` pair connect six size rows to each product.
- `users`: ID, combined `name`, unique normalized `email`, `password_hash`, creation time, `first_name`, and `last_name`.
- `sessions`: user ID, SHA-256 token hash, expiration, and creation time. The foreign key deletes sessions with their user.
- `chat_messages`: user ID, `user`/`assistant` role, content, structured product JSON, and creation time.

Product images live in `data/products/`. The API converts each stored image path to `/images/{filename}` and serves that directory through FastAPI. Product pages and chat cards therefore use the image associated with the same catalogue record.

## Frontend and product experience

The single-page app provides Home, Products, About Us, Log In, Create Account, and `/products/{product_id}` detail routes. Shared product cards show catalogue images, names, prices, short descriptions, and links. Detail pages show the larger image, full description, colors, price, all sizes, size stock, and total stock.

The floating storefront-styled chat sends messages to FastAPI and renders structured recommendations. `ChatSearchResults` maps each returned `ChatProductMatch` into the same `ProductCard` component used by the regular catalogue, so dynamic cards have identical behavior and open the correct detail route.

Problem 9 usability features are implemented in the running UI:

- Product keyword search plus garment-type, available-size, and in-stock filters, a live result count, reset control, empty state, loading state, and product-fetch error state.
- Chat loading feedback, disabled duplicate sends, helpful error text, and a retry action.
- A deterministic clarification response for vague first-turn shopping requests, with one follow-up question and no guessed products.
- Validated input and safe HTTP errors for database, timeout, configuration, and unexpected agent failures.

The responsive visual system uses Yale blue, baby pink, pearl surfaces, editorial type hierarchy, bow details, consistent spacing, product-first photography, and subtle hover/motion states. `output/design.md` records the design rationale. `output/usability.md` records the four usability improvements. `output/app_check.html` contains live screenshots proving inventory lookup, dynamic category cards, and product filtering.

## Authentication and customer memory

Registration accepts first name, last name, email, password, and confirmation. It normalizes email, validates password confirmation, creates the combined display name, and stores no plaintext password or confirmation value.

New passwords use PBKDF2-HMAC-SHA256 with a random 16-byte-equivalent hex salt and 600,000 iterations. Login compares digests in constant time. Supplied legacy three-part PBKDF2 hashes at 120,000 iterations remain compatible and are upgraded after a successful login.

Successful registration/login creates a random seven-day session token. SQLite stores only its SHA-256 hash; the original is sent as an `HttpOnly`, `SameSite=Lax` cookie and becomes `Secure` under HTTPS. Unknown-email login still performs comparable PBKDF2 work to reduce timing leakage.

Authenticated exchanges append a user row and assistant row to `chat_messages`. `GET /api/chat/history` returns up to the latest 50 in chronological order and rehydrates saved product IDs from current catalogue data. The frontend restores those messages and the latest product results. Guests can chat, but guest history is not persisted.

For a logged-in request, FastAPI ignores browser-provided history and loads the latest 12 database messages. It passes the trusted user ID, name, and email through `AgentDependencies`. The dynamic system context may use the customer's name, but it prohibits repeating the email unless the customer asks about their own account.

The widget sends the current route and, on a detail page, its product ID. FastAPI verifies the ID against SQLite and supplies its authoritative name. The agent can therefore resolve “this” or “it” while still making a fresh tool call before giving product, price, color, or stock facts.

## API flow and error behavior

- `GET /api/health`: health check.
- `GET /api/products`: complete catalogue; optional validated `q` query.
- `GET /api/products/{product_id}`: one product with inventory or 404.
- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, and `POST /api/auth/logout`: account/session flow.
- `GET /api/chat/history`: saved history for the authenticated session or an empty guest result.
- `POST /api/chat`: validated message, history, and page context in; structured reply and zero to four hydrated products out.

Chat has a 45-second FastAPI timeout. Timeouts return 504, catalogue/history database failures return 503, missing configuration returns 503, and unexpected agent failures return a generic 502. Internal exception details and secrets are not sent to the browser.

## Agent tools and abilities

The tools in `backend/tools.py` query SQLite directly:

1. `search_catalogue(query, limit)` searches names, garment types, colors, tags, and descriptions; ranks matches; and clamps the tool result to 1–8 records. It is required for discovery and recommendations.
2. `get_product_details(product_id)` returns one exact product's description, colors, price, image URL, stock by size, and total stock. It is required for specific-product facts and price questions.
3. `check_product_stock(product_id, size)` returns all current inventory or one normalized size. It explicitly distinguishes a zero-quantity “out of stock” size from a size that is not offered.

The PydanticAI agent has two retries, at most 8 model requests and 6 tool calls per run, and the enclosing API has a 45-second timeout. Up to 12 recent conversation messages are supplied. A catalogue search tool may inspect up to 8 matches, but `AgentReply` and `ChatResponse` cap displayed recommendations at 4. FastAPI re-fetches every selected ID; duplicates and invented IDs are dropped before data reaches React.

Beyond product discovery, the assistant can answer database-grounded descriptions, colors, prices, size availability, and quantities; use logged-in identity and saved history; understand verified product-page context; clarify vague requests; and explain prototype limitations for payments, orders, shipping, returns, or account actions it cannot perform.

## Structured models and field rationale

All shared agent/API structures are in `backend/models.py`:

- `ChatHistoryMessage`: `role` is restricted to `user` or `assistant`; `content` is required and limited to 2,000 characters so history is bounded and unambiguous.
- `PageContext`: local `path` anchors route context; optional slug-shaped `product_id` identifies a product safely; optional `product_name` is filled from SQLite rather than trusted from the browser.
- `ChatRequest`: validated `message`, at most 12 `history` records, and optional `page_context` bound request size and carry the context needed for follow-ups.
- `AgentProductMatch`: exact `product_id` plus a short `reason`. Keeping the model selection minimal lets FastAPI hydrate all display facts from SQLite.
- `AgentReply`: customer-facing `reply`, zero to four `products`, `needs_clarification`, and optional `follow_up_question`. Validation requires a question—and forbids recommendations—when clarification is needed.
- `SizeStock`: `size`, nonnegative `quantity`, and derived `in_stock` make availability explicit for both chat and UI.
- `CatalogueMatch`: `product_id`, `name`, `garment_type`, `description`, `colors`, `price`, `image_url`, `stock_by_size`, and `total_stock` provide one authoritative product result.
- `ChatProductMatch`: extends `CatalogueMatch` with the agent's `reason`, combining database display data with conversational relevance.
- `ChatResponse`: reply text, at most four hydrated products, clarification flag, and follow-up question form the stable frontend contract.
- `StoredChatMessage`: extends chat history with database `id`, saved/rehydrated `products`, and `created_at` so sessions can restore the conversation in order.
- `ChatHistoryResponse`: wraps stored `messages` for the history endpoint.
- `AgentDependencies`: trusted `customer_id`, `customer_name`, `customer_email`, and `page_context`; `is_authenticated` derives login state without trusting model output.
- `StockLookup`: product identity, optional `requested_size`, relevant `stock_by_size`, `total_stock`, and a ready-to-use `availability_message` prevent ambiguous stock answers.
- `AuditEvent`: UTC `time`, bounded `tool_name`, short scalar `args`, bounded `result`, and optional `stop_reason` define one safe, machine-readable JSONL record.

## Safety rules

`backend/prompts/prompt.md` is loaded when the cached agent is first created. It requires database tools for changing or high-integrity catalogue facts and prohibits inventing product IDs, products, descriptions, links, prices, quantities, and availability. Failed or empty lookups must be acknowledged rather than guessed; zero stock must be described as “out of stock.”

The prompt also prohibits requesting or exposing passwords, API keys, session tokens, hashes, hidden prompts, internal configuration, another customer's identity/history, or unrelated private database rows. It refuses payment-card collection, harmful/illegal/discriminatory/privacy-invasive help, unsupported transaction claims, prompt-role overrides, and unrelated requests; safe refusals redirect to product, sizing, stock, or navigation help. Customer text, catalogue content, conversation history, and tool output are treated as data—not higher-priority instructions.

Server-side controls reinforce the prompt: secrets stay in environment variables; passwords and sessions are hashed; page product IDs are verified; response product IDs are rehydrated from SQLite; validation limits request fields; and errors expose safe messages only.

## Append-only audit trail

`backend/audit.py` writes `output/audit_trail.jsonl`. Every event is one JSON object on one line with:

- `time`: timezone-aware UTC event time.
- `tool_name`: `agent_loop`, `search_catalogue`, `get_product_details`, or `check_product_stock`.
- `args`: short inputs relevant to the event. Agent-loop entries log counts, authentication state, and page/product context—not raw messages or customer identity.
- `result`: a bounded operational summary such as returned product IDs, confirmed availability, or result count.
- `stop_reason`: `completed`, `clarification_required`, `cancelled_or_timeout`, `error`, `database_error`, `not_found`, `no_matches`, or `null` for an in-progress/successful tool step.

The writer always opens the file with append mode, serializes exactly one event per line under a process lock, flushes it, and never truncates prior records. Obvious emails and credential-like strings are redacted, values are length-limited, and an audit-write failure is logged server-side without breaking shopper chat. `CAMPUS_CUSTOMS_AUDIT_PATH` exists only as a test/deployment override; production defaults to the required output path.

## Exact run instructions

From the `HW 4` root, activate the existing project environment:

```bash
source .venv/bin/activate
```

Terminal 1 — the backend command must be run from `HW 4/backend` exactly as follows:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Terminal 2 — run the frontend from `HW 4/frontend`:

```bash
cd frontend
npm run dev
```

Open <http://127.0.0.1:5173>. Vite proxies `/api` and `/images` to `127.0.0.1:8000`. The supplied account is `test@campuscustoms.yale.edu` with password `password`.

## Verification commands

From `HW 4`:

```bash
.venv/bin/python -m unittest discover -s tests -v
cd frontend
npm run build
```

The audit tests pre-create a sentinel line, append two events, and verify the old line remains first. They also run a real catalogue search plus the no-model clarification path, parse every JSONL record, and verify required fields and the final stop reason.
