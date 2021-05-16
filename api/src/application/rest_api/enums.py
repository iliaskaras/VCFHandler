from enum import Enum


class AcceptHeader(Enum):
    json = "application/json"
    xml = "application/xml"
    all = "*/*"
