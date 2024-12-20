from models.engine.database import DBStorage
from models.redisengine.redisSession import RedisSession

session = RedisSession()
db = DBStorage()
db.reload()