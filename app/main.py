from app.db.session import engine


def main() -> None:
    print("risk-crm app container is ready")
    print(f"SQLAlchemy engine: {engine.url.render_as_string(hide_password=True)}")


if __name__ == "__main__":
    main()
