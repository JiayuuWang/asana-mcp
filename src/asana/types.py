from typing import Any, TypedDict


class Workspace(TypedDict):
    gid: str
    name: str
    resource_type: str


class User(TypedDict):
    gid: str
    name: str
    email: str
    resource_type: str


class Team(TypedDict):
    gid: str
    name: str
    resource_type: str


class Project(TypedDict):
    gid: str
    name: str
    resource_type: str


class Task(TypedDict):
    gid: str
    name: str
    completed: bool
    resource_type: str


class Story(TypedDict):
    gid: str
    resource_type: str


class ListResult(TypedDict):
    data: list[dict[str, Any]]
    next_page: dict[str, Any] | None


class GetResult(TypedDict):
    data: dict[str, Any]


class CreateResult(TypedDict):
    data: dict[str, Any]


class UpdateResult(TypedDict):
    data: dict[str, Any]