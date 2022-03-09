from sqlalchemy.exc import OperationalError
from REST_API_Project.logger import Logger
from REST_API_Project.Customer import Customer


class DbRepo:

    def __init__(self, local_session):
        self.local_session = local_session
        self.logger = Logger.get_instance()

    def add_customer(self, customer):
        if not isinstance(customer, Customer):
            return False
        if not hasattr(customer, "email") or not hasattr(customer, "address"):
            return False
        try:
            self.local_session.add(customer)
            self.local_session.commit()
            self.logger.logger.debug(f'{customer} added to the DB.')
        except OperationalError as a:
            self.logger.logger.critical(a)

    def delete_customer_by_id(self, id):
        try:
            self.local_session.query(Customer).filter(Customer.id == id).delete(synchronize_session=False)
            self.local_session.commit()
            self.logger.logger.debug(f'{id} deleted from {Customer}')
            return True
        except OperationalError as a:
            self.logger.logger.critical(a)

    def get_all_customers(self):
        try:
            return self.local_session.query(Customer).all()
        except OperationalError as a:
            self.logger.logger.critical(a)

    def update_put_customer(self, id, values):
        updated_values = {}
        for key, value in values.items():
            if key == 'username' or key == 'password' or key == 'email' or key == 'address':
                updated_values[key] = value
        if len(list(updated_values.keys())) == 4:
            customer = Customer(username=updated_values["username"], password=updated_values["password"],
                                email=updated_values["email"], address=updated_values["address"])
            self.local_session.query(Customer).filter(Customer.id == id).update(customer)
            self.local_session.commit()
            return True
        else:
            return False

    def update_patch_customer(self, id, values):
        updated_values = {}
        for key, value in values.items():
            if key == 'username' or key == 'password' or key == 'email' or key == 'address':
                updated_values[key] = value
        if len(list(updated_values.keys())) == 4:
            customer = Customer(username=updated_values["username"], password=updated_values["password"],
                                email=updated_values["email"], address=updated_values["address"])
            try:
                self.local_session.query(Customer).filter(Customer.id == id).update(customer)
                self.local_session.commit()
            except OperationalError as a:
                self.logger.logger.critical(a)
        else:
            customer = self.local_session.query(Customer).get(id)
            if 'username' in updated_values:
                username = updated_values["username"]
            else:
                username = customer.username
            if 'password' in updated_values:
                password = updated_values["password"]
            else:
                password = customer.password
            if 'email' in updated_values:
                email = updated_values["email"]
            else:
                email = customer.email
            if 'address' in updated_values:
                address = updated_values["address"]
            else:
                address = customer.address
            new_customer = Customer(username=username, password=password, email=email, address=address)
            try:
                self.local_session.query(Customer).filter(Customer.id == id).update(new_customer)
                self.local_session.commit()
            except OperationalError as a:
                self.logger.logger.critical(a)

    def get_customer_by_id(self, id):
        try:
            return self.local_session.query(Customer).get(id)
        except OperationalError as a:
            self.logger.logger.critical(a)

    def get_customer_by_username(self, username):
        customer = self.local_session.query(Customer).filter(Customer.username == username).all()
        if customer:
            return customer[0]
        else:
            return False

