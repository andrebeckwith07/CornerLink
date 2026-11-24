# Jab-Cross Cipher
# CYSE 250 Milestone 3


def encrypt(text, key):
    """Encrypts text using the Jab-Cross Cipher."""
    result = ""
    for i, char in enumerate(text):
        if char.isalpha():
            shift = key if i % 2 == 0 else key + 3
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result


def decrypt(text, key):
    """Decrypts text that was encrypted with the Jab-Cross Cipher."""
    result = ""
    for i, char in enumerate(text):
        if char.isalpha():
            shift = key if i % 2 == 0 else key + 3
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base - shift) % 26 + base)
        else:
            result += char
    return result
