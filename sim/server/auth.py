import base64, binascii, os, hashlib
from http import cookies


""" Original: http/server.py@1098"""
def DecodeBase64(authHeader):
    """Decode Base64 hash"""
    if authHeader:
        authorization = authHeader.split()
        if len(authorization) == 2:
            if authorization[0].lower() == "basic":
                try:
                    authorization = authorization[1].encode('ascii')
                    authorization = base64.decodebytes(authorization).\
                                    decode('ascii')
                except (binascii.Error, UnicodeError):
                    pass
                else:
                    authorization = authorization.split(':')
                    if len(authorization) == 2:
                        return (authorization)

""" Original: https://www.vitoshacademy.com/hashing-passwords-in-python/"""
def HashPassword(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def VerifyPassword(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                provided_password.encode('utf-8'), 
                                salt.encode('ascii'), 
                                100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password