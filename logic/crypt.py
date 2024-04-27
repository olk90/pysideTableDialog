from cryptography.fernet import Fernet, InvalidToken

from logic.config import properties
from logic.model import Person


def encrypt_string(key, string_to_encrypt):
    f = Fernet(key)
    encrypted_string = f.encrypt(string_to_encrypt.encode()).decode()
    return encrypted_string


def decrypt_string(key, encrypted_string):
    f = Fernet(key)
    try:
        decrypted_string = f.decrypt(encrypted_string).decode()
    except InvalidToken:
        decrypted_string = encrypted_string
    return decrypted_string


def generate_key():
    return Fernet.generate_key().decode()


def encrypt_persons(key):
    s = properties.open_session()
    persons = s.query(Person).all()
    for employee in persons:
        encrypt_person(key, employee)
    s.commit()
    s.close()


def encrypt_person(key, person: Person) -> Person:
    enc_fn = encrypt_string(key, person.firstname)
    enc_ln = encrypt_string(key, person.lastname)
    enc_em = encrypt_string(key, person.email)
    person.firstname = enc_fn
    person.lastname = enc_ln
    person.email = enc_em
    return person


def decrypt_persons(key):
    s = properties.open_session()
    persons = s.query(Person).all()
    for person in persons:
        decrypt_person(key, person)
    s.commit()
    s.close()


def decrypt_person(key, person: Person) -> Person:
    dec_fn = decrypt_string(key, person.firstname)
    dec_ln = decrypt_string(key, person.lastname)
    dec_em = decrypt_string(key, person.email)
    person.firstname = dec_fn
    person.lastname = dec_ln
    person.email = dec_em
    return person
