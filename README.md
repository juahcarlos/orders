### Installation & Setup

**Clone**:
git clone <repo_url>
cd <project_dir>

**Environment**: 
Create an `.env` file in the <project_dir>.

**Launch**:
docker compose up --build -d

**Migrations**:
docker compose exec app alembic upgrade head

**Tests**:
docker compose exec app python -m pytest