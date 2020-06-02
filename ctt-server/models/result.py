import uuid
import os
import requests
import shutil

from flask import current_app
from sqlalchemy import Column, String, ForeignKey

from db_orm.database import Base, db_session
from models.execution import Execution
from models.abstract_model import AbstractModel
from util.configuration import BasePath


class Result(Base, AbstractModel):
    __tablename__ = 'result'

    uuid: str
    storage_path: str
    execution_uuid: str
    results_file: str

    uuid = Column(String, primary_key=True)
    storage_path = Column(String, nullable=False)
    execution_uuid = Column(String, ForeignKey('execution.uuid'), nullable=False)
    results_file = Column(String)

    results_file_name = 'results.zip'

    def __init__(self, execution):
        self.uuid = str(uuid.uuid4())
        self.execution_uuid = execution.uuid
        self.storage_path = os.path.join(self.__tablename__, self.uuid)

        if execution:
            db_session.add(self)
            db_session.commit()
        else:
            raise Exception(f'Linked entities do not exist.')

        if not os.path.exists(self.fq_storage_path):
            os.makedirs(self.fq_storage_path)

    def __repr__(self):
        return '<Result UUID=%r, EX_UUID=%r, ST_PATH=%r>' % \
               (self.uuid, self.execution_uuid, self.storage_path)

    @property
    def fq_storage_path(self):
        return os.path.join(BasePath, self.storage_path)

    @property
    def fq_result_storage_path(self):
        return os.path.join(self.fq_storage_path, self.results_file_name)

    @property
    def result_storage_path(self):
        return os.path.join(self.storage_path, self.results_file_name)

    @classmethod
    def get_parent_type(cls):
        return Execution

    @classmethod
    def create(cls, execution_uuid):
        linked_execution = Execution.get_by_uuid(execution_uuid)
        result = Result(linked_execution)

        # Download results from test infrastructure
        with requests.get(
                f'http://{linked_execution.test_infrastructure_ip}:5000/jmeter/execution/{linked_execution.agent_execution_uuid}', stream=True) as req:
            with open(result.fq_result_storage_path, 'wb') as f:
                shutil.copyfileobj(req.raw, f)
        if os.path.isfile(result.fq_result_storage_path):
            result.results_file = result.fq_storage_path
            db_session.add(result)
            db_session.commit()

        return result

    @classmethod
    def get_all(cls):
        return Result.query.all()

    @classmethod
    def get_by_uuid(cls, get_uuid):
        return Result.query.filter_by(uuid=get_uuid).first()

    @classmethod
    def delete_by_uuid(cls, del_uuid):
        result = Result.query.filter_by(uuid=del_uuid)
        if result:
            result.delete()
            # rmtree(self.fq_storage_path)
            db_session.commit()

