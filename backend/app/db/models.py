from sqlalchemy.orm import registry, relationship
from schema import metadata, users_table, projects_table


class User:
    pass


class Project:
    pass


mapper_reg = registry(metadata=metadata)
mapper_reg.map_imperatively(User, users_table, properties={
    "projects": relationship(Project, back_populates="author")
})
mapper_reg.map_imperatively(Project, projects_table, properties={
    "author": relationship(User, back_populates="projects")
})