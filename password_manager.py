from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import declarative_base, Session, relationship

# Підключення до бази даних
engine = create_engine('sqlite:///password_manager.db', echo=False)
Base = declarative_base()

# Оголошення класів моделей
class Sites(Base):
    __tablename__ = 'sites'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)

class Clients(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

class Passwords(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    site_id = Column(Integer, ForeignKey('sites.id'))
    password = Column(String)

    client = relationship("Clients")
    site = relationship("Sites")

# Створення таблиць
Base.metadata.create_all(engine)

# Створення сесії
def create_session():
    return Session(engine) # Повертає сесію для взаємодії з базою

# Функція для створення нового сайту
def create_site(session, name, url):
    new_site = Sites(name=name, url=url)
    session.add(new_site)
    session.commit()

# Функція для додавання нового клієнта
def create_client(session, name, email):
    new_client = Clients(name=name, email=email)
    session.add(new_client)
    session.commit()

# Функція для додавання нового пароля
def create_password(session, client_id, site_id, password):
    new_password = Passwords(client_id=client_id, site_id=site_id, password=password)
    session.add(new_password)
    session.commit()

# Функція для отримання всіх паролів
def get_all_passwords(session):
    return session.query(Passwords).all()

# Функція для оновлення пароля
def update_password(session, password_id, new_password):
    password_to_update = session.query(Passwords).filter_by(id=password_id).first()
    if password_to_update:
        password_to_update.password = new_password
        session.commit()

# Функція для видалення пароля
def delete_password(session, password_id):
    password_to_delete = session.query(Passwords).filter_by(id=password_id).first()
    if password_to_delete:
        session.delete(password_to_delete)
        session.commit()

# Функція для отримання всіх паролів з відповідними даними про клієнтів і сайти
def get_password_details(session):
    return session.query(Clients.name, Sites.name, Passwords.password).\
        join(Passwords, Clients.id == Passwords.client_id).\
        join(Sites, Sites.id == Passwords.site_id).all()

# Функція для вибірки паролів за клієнтом
def get_passwords_for_client(session, client_name):
    return session.query(Sites.name, Passwords.password).\
        join(Passwords, Sites.id == Passwords.site_id).\
        join(Clients, Clients.id == Passwords.client_id).\
        filter(Clients.name == client_name).all()

# Закриття сесії
def close_session(session):
    session.close()

# Приклад використання:
session = create_session()

# CRUD операції

# Додавання сайтів
sites_to_add = [['Google', 'https://google.com'], ['Facebook', 'https://facebook.com'], ['Twitter', 'https://twitter.com']]
for site in sites_to_add:
    create_site(session, site[0], site[1])

# Додавання клієнтів
clients_to_add = [['John', 'john@mail.com'], ['Jane', 'jane@mail.com']]
for client in clients_to_add:
    create_client(session, client[0], client[1])

# Додавання паролів для клієнтів
passwords_to_add = [[1, 1, 'password123'], [1, 2, 'facebook123'], [2, 3, 'twitter123']]
for password in passwords_to_add:
    create_password(session, password[0], password[1], password[2])

# Виведення всіх паролів з деталями
password_details = get_password_details(session)
print("Деталі паролів:")
for detail in password_details:
    print(f"{detail[0]} | {detail[1]} | {detail[2]}")

# Виведення паролів для клієнта "John"
john_passwords = get_passwords_for_client(session, 'John')
print("\nПаролі для клієнта John:")
for password in john_passwords:
    print(f"{password[0]} | {password[1]}")

# Оновлення пароля для клієнта John на сайт Google
update_password(session, 1, 'newpassword123')
print("\nПаролі після оновлення:")
password_details = get_password_details(session)
for detail in password_details:
    print(f"{detail[0]} | {detail[1]} | {detail[2]}")

# Видалення пароля для клієнта Jane на сайт Twitter
delete_password(session, 3)

# Виведення паролів після видалення
print("\nПаролі після видалення:")
password_details = get_password_details(session)
for detail in password_details:
    print(f"{detail[0]} | {detail[1]} | {detail[2]}")

# Закриття сесії
close_session(session)