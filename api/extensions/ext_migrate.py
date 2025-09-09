from dify_app import DifyApp
from configs import dify_config


def init_app(app: DifyApp):
    import flask_migrate  # type: ignore

    from extensions.ext_database import db

    # Migration directory has to be mannually specified since mergeing 1.8.0, 
    # haven't found why yet
    if "mysql" in dify_config.SQLALCHEMY_DATABASE_URI_SCHEME:
        directory="migrations-mysql"

    flask_migrate.Migrate(app, db, directory=directory)
