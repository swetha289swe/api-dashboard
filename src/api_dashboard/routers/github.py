from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from api_dashboard.cache import async_ttl_cache

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
async def get_github_user(username: str):
    return await fetch_github_user(username)