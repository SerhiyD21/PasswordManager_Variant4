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

# Головний блок із меню
if __name__ == '__main__':
    def main_menu():
        print("\nPassword Manager")
        print("1. Додати сайт")
        print("2. Додати клієнта")
        print("3. Додати пароль")
        print("4. Переглянути всі паролі")
        print("5. Переглянути паролі клієнта")
        print("6. Оновити пароль")
        print("7. Видалити пароль")
        print("8. Вийти")
    
    session = create_session()
    while True:
        main_menu()
        choice = input("Виберіть дію: ")
        
        if choice == '1':
            name = input("Назва сайту: ")
            url = input("URL сайту: ")
            create_site(session, name, url)
            print("Сайт додано.")
        
        elif choice == '2':
            name = input("Ім'я клієнта: ")
            email = input("Email клієнта: ")
            create_client(session, name, email)
            print("Клієнта додано.")
        
        elif choice == '3':
            client_id = int(input("ID клієнта: "))
            site_id = int(input("ID сайту: "))
            password = input("Пароль: ")
            create_password(session, client_id, site_id, password)
            print("Пароль додано.")
        
        elif choice == '4':
            passwords = get_password_details(session)
            print("\nДеталі паролів:")
            for detail in passwords:
                print(f"{detail[0]} | {detail[1]} | {detail[2]}")
        
        elif choice == '5':
            client_name = input("Ім'я клієнта: ")
            passwords = get_passwords_for_client(session, client_name)
            print(f"\nПаролі для клієнта {client_name}:")
            for password in passwords:
                print(f"{password[0]} | {password[1]}")
        
        elif choice == '6':
            password_id = int(input("ID пароля: "))
            new_password = input("Новий пароль: ")
            update_password(session, password_id, new_password)
            print("Пароль оновлено.")
        
        elif choice == '7':
            password_id = int(input("ID пароля: "))
            delete_password(session, password_id)
            print("Пароль видалено.")
        
        elif choice == '8':
            print("Завершення роботи.")
            break
        
        else:
            print("Невірний вибір. Спробуйте ще раз.")
    
    close_session(session)
