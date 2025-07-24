import math
from src.database.types import Range, DBResponse, DBMetadata, EndpointResponse

def page_to_range(page: int, page_size: int) -> Range:
  if page < 1:
    page = 1

  range_start = (page - 1) * page_size
  range_end = (page * page_size) - 1

  return Range(range_start, range_end)

def build_response(response: DBResponse, page: int, page_size: int):
  total_pages = math.ceil(response.count / page_size)

  return EndpointResponse(
    data=response.data,
    metadata=DBMetadata(
      page=page,
      total_pages=total_pages,
      total_records=response.count,
    )
  )
