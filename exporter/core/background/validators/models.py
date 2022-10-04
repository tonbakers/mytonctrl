from sqlalchemy.orm import relationship
from sqlalchemy.sql import sqltypes
from sqlalchemy.sql.schema import Column, ForeignKey

from exporter.database.base import Base


class Validator(Base):
    __tablename__ = 'validator'

    id = Column(sqltypes.Integer, primary_key=True)
    wallet_address = Column(sqltypes.Unicode, nullable=False, index=True)
    adnl_address = Column(sqltypes.Unicode, nullable=False, index=True)
    public_key = Column(sqltypes.Unicode, nullable=False, index=True)
    statistics = relationship('ValidatorStatistic')


class ValidatorStatistic(Base):
    __tablename__ = 'validator_statistic'

    id = Column(sqltypes.Integer, primary_key=True)
    efficiency = Column(sqltypes.DECIMAL, nullable=False, index=True, default=0.0)
    online = Column(sqltypes.Boolean, nullable=False, index=True, default=False)
    validator_id = Column(sqltypes.Integer, ForeignKey('validator.id', ondelete='SET NULL'))
