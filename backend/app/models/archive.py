from typing import List, Optional
from pydantic import BaseModel

class MediaItem(BaseModel):
    id: int
    media_type: str
    original_url: str
    local_path: Optional[str] = None
    download_status: int

class TweetItem(BaseModel):
    tweet_id: str
    author_name: str
    author_handle: str
    author_avatar: Optional[str] = None
    content: Optional[str] = None
    post_type: str
    original_url: str
    posted_at: str
    archived_at: str
    media: List[MediaItem] = []

class PaginatedTweets(BaseModel):
    total: int
    page: int
    size: int
    data: List[TweetItem]

class SyncRequest(BaseModel):
    username: str