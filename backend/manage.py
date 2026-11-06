#!/usr/bin/env python3
"""
EVnesia Automotive Backend - Unified Management CLI
Usage:
    python manage.py <command> [options]

Commands:
    status         Show status of database, dataset, and backend environment
    run            Start the FastAPI development server
    seed           Initialize and seed SQLite database
    audit          Audit frontend car dataset for data integrity & missing specs
    export         Export and normalize car catalog to frontend JSON
"""

import sys
import os
import argparse
import json
import sqlite3

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
FRONTEND_DATA_PATH = os.path.join(REPO_ROOT, "src", "data", "electrified-cars.json")
DB_PATH = os.path.join(BASE_DIR, "autodrive.db")


def cmd_status(args):
    print("=" * 60)
    print("[*] EVnesia Automotive Backend - Status Overview")
    print("=" * 60)
    print(f"• Python Version : {sys.version.split()[0]}")
    print(f"• Backend Root   : {BASE_DIR}")

    # Database check (Supabase / SQLAlchemy)
    try:
        from app.database import engine, check_db_connection, SessionLocal
        from app.models.car import Car
        from app.models.brand import Brand
        from app.models.article import CMSArticle
        from app.core.config import settings

        db_target = settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL
        print(f"• Database Target: {db_target}")
        if check_db_connection():
            db = SessionLocal()
            try:
                cars_count = db.query(Car).count()
                brands_count = db.query(Brand).count()
                articles_count = db.query(CMSArticle).count()
                provider = "Neon Lakebase Postgres" if "neon" in db_target else "PostgreSQL"
                print(f"  └─ Status      : ✅ Connected ({provider})")
                print(f"  └─ DB Records  : {cars_count} cars, {brands_count} brands, {articles_count} synced articles")
            finally:
                db.close()
        else:
            print("  └─ Status      : ❌ Connection Failed")
    except Exception as e:
        print(f"  └─ DB Error    : {e}")


    # Frontend dataset check
    print(f"• Frontend Data  : {FRONTEND_DATA_PATH}")
    if os.path.exists(FRONTEND_DATA_PATH):
        try:
            with open(FRONTEND_DATA_PATH, "r", encoding="utf-8") as f:
                cars = json.load(f)
            brands = set(c.get("brand") for c in cars if c.get("brand"))
            bev = sum(1 for c in cars if c.get("engineType") == "bev")
            phev = sum(1 for c in cars if c.get("engineType") == "phev")
            hev = sum(1 for c in cars if c.get("engineType") == "hev")
            print(f"  └─ Total Models: {len(cars)} cars across {len(brands)} brands")
            print(f"  └─ Powertrains : {bev} BEV, {phev} PHEV, {hev} HEV")
        except Exception as e:
            print(f"  └─ Error reading JSON: {e}")
    else:
        print("  └─ Status      : Not Found")

    print("=" * 60)


def cmd_run(args):
    port = args.port or int(os.getenv("PORT", 8000))
    host = args.host or os.getenv("HOST", "0.0.0.0")
    print(f"Starting EVnesia FastAPI Backend on http://localhost:{port}")
    print(f"Swagger UI Docs: http://localhost:{port}/docs")
    try:
        import uvicorn
        uvicorn.run("app.main:app", host=host, port=port, reload=True)
    except ImportError:
        print("Error: 'uvicorn' is not installed in the current environment.")
        print("Please activate your virtual environment: .\\venv\\Scripts\\activate")


def cmd_seed(args):
    print("[*] Running database seeder...")
    import seed
    seed.seed_database()


def cmd_audit(args):
    # 1. Audit Database Supabase / PostgreSQL
    try:
        from scripts.data_tools.audit_and_clean_specs import run_audit
        run_audit()
    except Exception as e:
        print(f"Notice: Could not run full database audit ({e}). Auditing JSON fallback.\n")

    # 2. Audit Frontend Dataset JSON
    if not os.path.exists(FRONTEND_DATA_PATH):
        print(f"Error: Dataset not found at {FRONTEND_DATA_PATH}")
        return

    with open(FRONTEND_DATA_PATH, "r", encoding="utf-8") as f:
        cars = json.load(f)

    print(f"\n[*] Memeriksa {len(cars)} mobil di file frontend electrified-cars.json:")
    issues = []
    for i, c in enumerate(cars, 1):
        b = c.get("brand", "Unknown")
        n = c.get("name", "Unknown")
        vars_list = c.get("variants", [])
        if not vars_list:
            issues.append(f"[{b}] {n} belum memiliki varian!")
        for v in vars_list:
            v_name = v.get("name", "")
            v_price = v.get("price", 0)
            if v_price == 0:
                issues.append(f"[{b}] {n} varian '{v_name}' harga 0.")

    if not issues:
        print("  [OK] Validasi Frontend Dataset lolos: Seluruh mobil memiliki varian & harga OTR valid.\n")
    else:
        print(f"  [PERINGATAN] Ditemukan {len(issues)} potensi catatan:")
        for iss in issues[:10]:
            print(f"    - {iss}")


def cmd_export(args):
    print("[*] Exporting database / compiled dataset to frontend...")
    import export_frontend_cars
    export_frontend_cars.export_cars()



def cmd_cms_sync(args):
    print("=" * 60)
    print("📡 Inova CMS Open API (Grup Indosatu) - Sync Tool")
    print("=" * 60)
    from app.services.cms_client import InovaCMSClient, CMSClientError
    from app.services.cms_sync_service import cms_sync_service
    from app.database import SessionLocal

    client = InovaCMSClient()
    print(f"• Base URL    : {client.base_url}")
    print(f"• Access Key  : {client.access_key[:8] + '...' if client.access_key else 'Belum diisi (None)'}")
    print(f"• Portal ID   : {client.portal_id or 'Belum diisi (None)'}")
    print(f"• Configured  : {'✅ Ya' if client.is_configured else '❌ Belum (.env)'}")

    if args.health:
        print("\n[*] Menguji koneksi HMAC-SHA256 ke CMS (GET /health)...")
        if not client.is_configured:
            print("[!] Kredensial CMS_ACCESS_KEY dan CMS_SECRET belum diisi di backend/.env.")
            return
        try:
            res = client.health()
            print("[OK] Health check berhasil!")
            print(json.dumps(res, indent=2))
        except CMSClientError as e:
            print(f"[ERROR] Health check gagal: {e}")
        return

    portal_id = args.portal or client.portal_id
    if not portal_id:
        print("\n[!] Harap tentukan portal_id via parameter --portal <UUID> atau isi CMS_PORTAL_ID di .env.")
        return

    print(f"\n[*] Memulai sinkronisasi artikel untuk portal: {portal_id}")
    db = SessionLocal()
    try:
        res = cms_sync_service.sync_articles(
            db=db,
            portal_id=portal_id,
            force_full_sync=args.force,
            limit_per_page=args.limit,
            max_pages=args.pages
        )
        print("\n[*] Hasil Sinkronisasi:")
        print(json.dumps(res, indent=2))
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="EVnesia Automotive Backend Unified CLI",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available management commands")

    # status
    subparsers.add_parser("status", help="Show system, database, and dataset status")

    # cms-sync
    cms_parser = subparsers.add_parser("cms-sync", help="Sync articles from Inova CMS Open API to Supabase")
    cms_parser.add_argument("--health", action="store_true", help="Test HMAC health check connection")
    cms_parser.add_argument("--portal", type=str, help="Portal UUID (overrides CMS_PORTAL_ID)")
    cms_parser.add_argument("--force", action="store_true", help="Force full sync ignoring last checkpoint")
    cms_parser.add_argument("--limit", type=int, default=50, help="Articles per page (default: 50)")
    cms_parser.add_argument("--pages", type=int, default=10, help="Max pages to fetch (default: 10)")

    # run
    run_parser = subparsers.add_parser("run", help="Start FastAPI development server")
    run_parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    run_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")

    # seed
    subparsers.add_parser("seed", help="Seed database from compiled reference data")

    # audit
    subparsers.add_parser("audit", help="Audit frontend car dataset integrity")

    # export
    subparsers.add_parser("export", help="Export dataset to frontend electrified-cars.json")

    args = parser.parse_args()

    if not args.command:
        cmd_status(args)
        print("\nTip: Use 'python manage.py --help' to see all available commands.")
        return

    commands = {
        "status": cmd_status,
        "run": cmd_run,
        "seed": cmd_seed,
        "audit": cmd_audit,
        "export": cmd_export,
        "cms-sync": cmd_cms_sync,
    }

    cmd_fn = commands.get(args.command)
    if cmd_fn:
        cmd_fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

