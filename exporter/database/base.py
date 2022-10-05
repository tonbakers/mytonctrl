import typing as t

from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    id: t.Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:  # NOTE: Type reveal error
        return cls.__name__.lower()
    
    __mapper_args__ = dict(always_refresh=True, eager_defaults=True)
