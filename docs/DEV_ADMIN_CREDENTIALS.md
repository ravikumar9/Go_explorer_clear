Development admin credentials (for local/dev db)

- Username: goexplorer_dev_admin
- Password: Thepowerof@9
- Email: dev-admin@goexplorer.dev

To create (or ensure) the admin user run:

    python manage.py create_dev_admin

Database and environment (DEV):

- Ensure your .env (or environment) contains:

    DB_NAME=goexplorer_dev
    DB_USER=goexplorer_dev_user

The project will use these vars to connect to your PostgreSQL dev database; otherwise it falls back to the included sqlite db (for local/dev).
Notes:
- This command is idempotent and will not overwrite an existing user with the same username.
- For production, create a secure superuser and keep credentials secret.