import sqlalchemy
import databases
from decouple import config
# DATABASE_URL = "postgresql://postgres:4253@localhost/testing"
# "postgresql://postgres:4253@localhost/store"

DATABASE_URL = (f"{config('DATABASE_TYPE')}://{config('DATABASE_USER')}:{config('DATABASE_PASSWORD')}"
                f"@localhost/{config('DATABASE_NAME')}")


database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
