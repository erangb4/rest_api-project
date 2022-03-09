from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import Flask, request, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from REST_API_Project.db_repo import DbRepo
from REST_API_Project.db_config import local_session
from REST_API_Project.Customer import Customer
from REST_API_Project.logger import Logger

app = Flask(__name__)
app.config['SECRET_KEY'] = 'woohoo'
repo = DbRepo(local_session)
logger = Logger.get_instance()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            token = token.removeprefix('Bearer ')
        if not token:
            logger.logger.info('A user tried to used a function that requires token but token is missing.')
            return jsonify({'message': 'Token is missing'}), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'])
        except:
            logger.logger.warning('A user tried to used a function that requires token but token is not valid.')
            return jsonify({'message': 'Token is not valid'}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def home():
    return '''
        <html>
            We Are Ready!
        </html>
    '''


@app.route('/customers', methods=['GET', 'POST'])
@token_required
def get_or_post_customer():
    if request.method == 'GET':
        customers = repo.get_all_customers()
        output = []
        for customer in customers:
            output.append({'id': customer.id, 'username': customer.username, 'password': customer.password,
                           'email': customer.email, 'address': customer.address})
        return jsonify({'customers': output})
    if request.method == 'POST':
        new_customer = request.get_json()
        insert_customer = Customer(username=new_customer["username"], password=new_customer["password"],
                                   email=new_customer["email"], address=new_customer["address"])
        repo.add_customer(insert_customer)
        logger.logger.info(f'New customer: {insert_customer} has been created!')
        return make_response('Customer Created!', 201)


@app.route('/customers/<int:id>', methods=['GET', 'PUT', 'DELETE', 'PATCH'])
@token_required
def get_customer_by_id(id):
    if request.method == 'GET':
        customer = repo.get_customer_by_id(id)
        return jsonify({'id': customer.id, 'username': customer.username, 'password': customer.password,
                        'email': customer.email, 'address': customer.address})
    if request.method == 'PUT':
        new_customer = request.get_json()
        back = repo.update_put_customer(id, new_customer)
        if back:
            logger.logger.info(f'The customer with the id: {id} has been updated!')
            return make_response('Put done!', 201)
        else:
            logger.logger.error(f'Could not update the customer with the id: {id}')
            return jsonify({'answer': 'failed'})
    if request.method == 'PATCH':
        new_customer = request.get_json()
        back = repo.update_patch_customer(id, new_customer)
        if back:
            logger.logger.info(f'The customer with the id: {id} has been updated!')
            return make_response('Patch done!', 201)
        else:
            logger.logger.error(f'Could not update the customer with the id: {id}')
            return jsonify({'answer': 'failed'})
    if request.method == 'DELETE':
        back = repo.delete_customer_by_id(id)
        if back:
            logger.logger.info(f'The customer with the id: {id} has been deleted!')
            return make_response('Delete done!', 201)
        else:
            logger.logger.error(f'Could not delete a customer with the id: {id}')
            return jsonify({'answer': 'failed'})


@app.route('/signup', methods=['POST'])
def signup():
    form_data = request.form
    username = form_data.get('username')
    password = form_data.get('password')
    email = form_data.get('email')
    address = form_data.get('address')
    customer = repo.get_customer_by_username(username)
    if customer:
        logger.logger.error(f'An anonymous tried to sign up with the username:{username} but this username already '
                            f'exists in the db')
        return make_response('Customer already exists. Please Log in.', 202)
    else:
        insert_customer = Customer(username=username, password=generate_password_hash(password), email=email,
                                   address=address)
        if insert_customer:
            repo.add_customer(insert_customer)
            logger.logger.info(f'New customer: {insert_customer} has been created!')
            return make_response('Customer Created!', 201)
        else:
            logger.logger.error('To insert new customer must sent "username", "password", "email", "address".')
            return jsonify({'answer': 'failed'})


@app.route('/login', methods=['POST'])
def login():
    form_data = request.form
    if not form_data or not form_data.get("username") or not form_data.get("password"):
        logger.logger.info('A customer tried to login without sending the required data(username, password)')
        return make_response('1-Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})
    customer = repo.get_customer_by_username(form_data.get('username'))
    if not customer:
        logger.logger.warning(f'A customer tried to login but the username:{form_data.get("username")} '
                              f'does not exist in the db')
        return make_response('2-Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})
    if not check_password_hash(customer.password, form_data.get("password")):
        logger.logger.error(f'The user: {form_data.get("username")} tried to login with a wrong password.')
        return make_response('3-Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required."'})
    logger.logger.debug(f'The user: {form_data.get("username")} logged in successfully!')
    # token = jwt.encode({'id': customer.id, 'exp': datetime.now() + timedelta(minutes=30)}, app.config['SECRET_KEY'])
    # return make_response(jsonify({'token': token.decode('UTF-8')}), 201)
    # ok?
    # it needs 1.7.
    # that's why i gave a requirements.txt file ... :)
    # ata po ?
    token = jwt.encode({'public_id': customer.id, 'exp': datetime.utcnow() + timedelta(minutes=30)},
                       app.config['SECRET_KEY'])
    print('--------------', token)
    print(type(token))
    return make_response(jsonify({'token': token.decode('UTF-8')}), 201)


app.run()
