import redis

class RedisSession():
    client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
    
    @classmethod
    def set_email(cls, token, email):
        cls.client.setex(f"auth<{token}>", 900, email)
    
    
    @classmethod
    def remove(cls, token):
        cls.client.delete(token)
        
    @classmethod
    def get_email(cls, token):
        #Returns None if there is no Session Data
        return cls.client.get(f"auth<{token}>")
    
    @classmethod
    def set_voter_session(cls, token, data):
        pass
    
    @classmethod
    def get_voter_session(cls, token):
        pass
    
    @classmethod
    def get_cached_voter(cls, token):
        data = cls.client.hgetall(f'user<{token}>')
        cls.client.expire(f'user<{token}>', 900)
        if data:
            return data
        else:
            return False

    @classmethod
    def cache_voter(cls, token, userData):
        cls.client.hset(f'user<{token}>', mapping=userData)
        cls.client.expire(f'user<{token}>', 900)