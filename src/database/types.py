from dataclasses import dataclass

@dataclass
class Range:
  start: int
  end: int

@dataclass
class DBResponse:
  data: list[dict]
  count: int

@dataclass
class DBMetadata:
  page: int
  total_pages: int
  total_records: int

@dataclass
class EndpointResponse:
  data: list[dict]
  metadata: DBMetadata
