# Campus Customs storefront

A responsive Yale-inspired storefront with a React/TypeScript frontend, FastAPI API, SQLite catalogue and accounts, and a PydanticAI shopping assistant powered through Portkey.

## Required local files

The course data pack is intentionally excluded from GitHub. Before running the project, place it inside the repository with this exact layout:

```text
data/
├── campus_customs.db
└── products/
    └── product image files referenced by the database
```

The SQLite database and product images must remain local because `.gitignore` excludes `data/campus_customs.db` and `data/products/`.

## Environment setup

Create the local environment file from the safe template and add your real Portkey key only to `.env`:

```bash
cp .env.example .env
```

Replace the `PORTKEY_API_KEY` placeholder in the copied `.env` file with your real Portkey key.

Never commit `.env`. The backend uses OpenAI through Portkey with `gpt-5.6-luna`.

Create and install the Python environment from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

## Run locally

Open two terminals and activate `.venv` in the backend terminal.

Terminal 1 — run this exact command from the `backend` folder:

```bash
source .venv/bin/activate
cd backend
uvicorn main:app --reload --port 8000
```

Terminal 2 — run Vite from the `frontend` folder:

```bash
cd frontend
npm run dev
```

Open <http://127.0.0.1:5173>. Vite proxies `/api` and `/images` to FastAPI at `127.0.0.1:8000`.

The supplied local data pack includes the test login `test@campuscustoms.yale.edu` with password `password`.

## Verification

Run backend tests from the project root:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Run the frontend production build:

```bash
cd frontend
npm run build
```

The implementation harness is in `output/harness.md`; usability and design notes are in `output/usability.md` and `output/design.md`; and `output/app_check.html` contains the live-site evidence.
