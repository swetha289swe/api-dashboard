import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session

from api_dashboard.cache import async_ttl_cache
from api_dashboard.database import get_session
from api_dashboard.models import SearchLog, User
from api_dashboard.security import get_current_user

router = APIRouter(prefix="/github", tags=["github"])


class GithubUserResponse(BaseModel):
    username: str
    name: str | None
    public_repos: int
    followers: int
    bio: str | None

@async_ttl_cache(ttl_seconds=30)
async def fetch_github_user(username: str) -> dict:
    print('HITTING GIT')
    async with httpx.AsyncClient() as client:
        url = f"https://api.github.com/users/{username}"
        response = await client.get(url)

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"GitHub user '{username}' not found")

        data = response.json()

        return {
            "username": data["login"],
            "name": data.get("name"),
            "public_repos": data["public_repos"],
            "followers": data["followers"],
            "bio": data.get("bio"),
        }


@router.get("/{username}", response_model=GithubUserResponse)
async def get_github_user(username: str, session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    result = await fetch_github_user(username)

    log = SearchLog(
        endpoint="github",
        query=username,
        result_summary=f"{result['username']}: {result['public_repos']} repos, {result['followers']} followers",
        user_id=current_user.id
    )
    session.add(log)
    session.commit()

    return result