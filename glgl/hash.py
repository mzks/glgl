import json
from base64 import b32encode
from hashlib import sha1

def hashablize(obj):
    try:
        hash(obj)
    except TypeError:
        if isinstance(obj, dict):
            return tuple((k, hashablize(v)) for (k, v) in sorted(obj.items()))
        elif hasattr(obj, '__iter__'):
            return tuple(hashablize(o) for o in obj)
        else:
            raise TypeError("Can't hashablize object of type %r" % type(obj))
    else:
        return obj


def deterministic_hash(thing, length=10):
    """Return a base32 lowercase string of length determined from hashing
    a container hierarchy
    """
    hashable = hashablize(thing)
    jsonned = json.dumps(hashable, cls=json.JSONEncoder)
    digest = sha1(jsonned.encode('ascii')).digest()
    return b32encode(digest)[:length].decode('ascii').lower()
