"""
Simple caching utility for image descriptions
"""
import hashlib
from functools import lru_cache
from PIL import Image
import io


def get_image_hash(image_file):
    """
    Generate a hash for an uploaded image file to use as cache key

    Args:
        image_file: FileStorage object from Flask request

    Returns:
        str: SHA256 hash of the image
    """
    # Read image bytes
    image_file.seek(0)  # Reset file pointer
    image_bytes = image_file.read()
    image_file.seek(0)  # Reset again for processing

    # Generate hash
    hash_obj = hashlib.sha256(image_bytes)
    return hash_obj.hexdigest()


class DescriptionCache:
    """Simple in-memory cache for image descriptions"""

    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.access_order = []  # Track LRU

    def get(self, key):
        """Get cached description"""
        if key in self.cache:
            # Update access order for LRU
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, key, value):
        """Set cached description with LRU eviction"""
        if key in self.cache:
            # Update existing
            self.access_order.remove(key)
        elif len(self.cache) >= self.max_size:
            # Evict least recently used
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]

        self.cache[key] = value
        self.access_order.append(key)

    def clear(self):
        """Clear all cached items"""
        self.cache.clear()
        self.access_order.clear()

    def size(self):
        """Get current cache size"""
        return len(self.cache)


# Global cache instance
description_cache = DescriptionCache(max_size=100)
