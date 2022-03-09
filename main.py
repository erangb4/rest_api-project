from db_config import local_session, create_all_entities
from db_repo import DbRepo

repo = DbRepo(local_session)
create_all_entities()
