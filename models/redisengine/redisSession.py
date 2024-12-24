import redis

class RedisSession():
    client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
    
    
    @classmethod
    def remove(cls, token):
        """
        Removes the cached voter data associated with the given token from the cache.

        Args:
            token (str): The token associated with the voter whose data needs to be removed 
                        from the cache. This token is used to identify the cached voter data.

        Returns:
            None
        """
        cls.client.delete(token)
    
    
    @classmethod
    def get_cached_voter(cls, token):
        """
        Retrieves the cached voter data associated with the given token.

        Args:
            token (str): The token associated with the voter whose cached data is to be retrieved.

        Returns:
            dict or bool: Returns the cached voter data as a dictionary if found, 
                        or `False` if no data is found for the given token.
        """
        data = cls.client.hgetall(f'user<{token}>')
        cls.client.expire(f'user<{token}>', 900)
        if data:
            return data
        else:
            return False

    @classmethod
    def cache_voter(cls, token, userData, ttl=3900):
        """
        Sets the cached voter data associated with the given token and assigns an expiration time.


        Args:
            token (str): The token associated with the voter whose data is to be cached.
            userData (dict): A dictionary containing the voter data to be cached.
            ttl (int): The time-to-live (TTL) in seconds for the cached data. After this period, 
                    the cached data will be automatically removed from the cache.

        Returns:
            None
        """
        cls.client.hset(f'user<{token}>', mapping=userData)
        cls.client.expire(f'user<{token}>', ttl)