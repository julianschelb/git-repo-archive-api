# ---------------------------------------------------------------------------- #
#                      Language Model Service                 #
# ---------------------------------------------------------------------------- #
# This section contains API entpoints for generating responses from the model.

from fastapi import APIRouter, Body, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from fastapi import HTTPException, status
from app.schemas.userRequest import UserRequest, SystemResponse
from app.schemas.key import APIKey
from app.auth import get_api_key
import subprocess
import datetime
import shutil
import os

router = APIRouter(responses={404: {"description": "Not Found"}})

data_dir = "data"  # TODO: Move this to config file

# ---------------------------- Helpers --------------------------- #


def get_repo_url(repo_path):
    """Get the URL of a repository."""
    result = subprocess.run(
        ["git", "-C", repo_path, "config", "--get", "remote.origin.url"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        raise Exception(f"Failed to get repo URL: {result.stderr}")


@router.get("/hello")
async def hello_world():
    return {"message": "Hello World"}

# ---------------------------- Add Repo --------------------------- #


@router.post("/archives/")
async def archive_repo(repo_url: str, api_key: APIKey = Depends(get_api_key)):
    """Clone a repository from GitHub."""
    try:
        # Check if the repository URL is valid
        if not repo_url.startswith("https://"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL",
            )

        # Define the directory where you want to clone the repository
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Extract the repo name from the URL to use as the directory name
        repo_name = repo_url.rstrip("/").split("/")[-1]
        repo_dir = os.path.join(data_dir, repo_name)

        # Remove the existing repo if it exists
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)

        # Clone the repository
        result = subprocess.run(
            ["git", "clone", repo_url, repo_dir],
            capture_output=True,
            text=True,
        )

        # Check for errors in the cloning process
        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.stderr,
            )

        return {"message": f"Repository cloned successfully to {repo_dir}"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

# ---------------------------- Remove Repo --------------------------- #


@router.delete("/archives/")
async def remove_repo(repo_name: str, api_key: APIKey = Depends(get_api_key)):
    """Remove a repository from the local directory."""
    try:
        # Define the directory where you want to clone the repository
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Define the directory where the repository is located
        repo_dir = os.path.join(data_dir, repo_name)

        # Remove the existing directory if it exists
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)

        return {"message": f"Repository removed successfully from {repo_dir}"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

# ---------------------------- List Repo --------------------------- #


@router.get("/archives/")
async def list_repos(api_key: APIKey = Depends(get_api_key)):
    """List all repositories in the local directory."""
    try:
        # Define the directory where you want to clone the repository
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Define the directory where the repository is located
        repo_dir = os.path.join(data_dir)

        # List all repositories in the directory
        repo_list = os.listdir(repo_dir)

        return {"message": f"Repository removed successfully from {repo_dir}", "repo_list": repo_list}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/archives/size")
async def list_repos_sizes(api_key: APIKey = Depends(get_api_key)):
    """List all repositories in the local directory and calculate their sizes."""
    try:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        repo_dir = os.path.join(data_dir)
        repo_list = os.listdir(repo_dir)

        total_size_bytes = 0  # Total size in bytes
        repo_details = []  # List to hold details of each repository

        for repo_name in repo_list:
            repo_path = os.path.join(repo_dir, repo_name)
            if os.path.isdir(repo_path):  # Check if it's a directory
                dir_size_bytes = sum(
                    f.stat().st_size for f in os.scandir(repo_path) if f.is_file()
                )
                # Convert bytes to megabytes and round
                dir_size_megabytes = round(dir_size_bytes / (1024 * 1024), 2)
                last_modified_time = max(
                    f.stat().st_mtime for f in os.scandir(repo_path)
                )
                last_modified_time = datetime.datetime.fromtimestamp(
                    last_modified_time)  # Convert to datetime
                num_files = len(
                    [f for f in os.scandir(repo_path) if f.is_file()])
                num_subdirs = len(
                    [d for d in os.scandir(repo_path) if d.is_dir()])
                repo_url = get_repo_url(repo_path)  # Get the repo URL
                repo_details.append({
                    "name": repo_name,
                    "size_MB": dir_size_megabytes,
                    "last_modified": last_modified_time,
                    "num_files": num_files,
                    "num_subdirectories": num_subdirs,
                    "url": repo_url  # Include the repo URL
                })
                total_size_bytes += dir_size_bytes

        # Convert bytes to gigabytes and round
        total_size_gigabytes = round(
            total_size_bytes / (1024 * 1024 * 1024), 2)

        return {
            "message": f"Details retrieved successfully for repositories in {repo_dir}",
            "repo_details": repo_details,
            "total_size_gigabytes": total_size_gigabytes
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ---------------------------- Update all Repos --------------------------- #


@router.put("/archives/all/update")
def update_repos(api_key: APIKey = Depends(get_api_key)):
    """Update all repositories in the local directory."""
    try:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        repo_dir = os.path.join(data_dir)
        repo_list = os.listdir(repo_dir)

        update_summary = {}

        for repo_name in repo_list:
            repo_path = os.path.join(repo_dir, repo_name)

            # Fetch the latest changes without merging
            result = subprocess.run(
                ["git", "-C", repo_path, "fetch"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.stderr,
                )

            # Get the diff summary
            result = subprocess.run(
                ["git", "-C", repo_path, "diff", "--shortstat", "HEAD..FETCH_HEAD"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.stderr,
                )
            update_summary[repo_name] = result.stdout.strip()

            # Merge the fetched changes
            result = subprocess.run(
                ["git", "-C", repo_path, "merge", "FETCH_HEAD"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result.stderr,
                )

        return {"message": f"Repositories updated successfully in {repo_dir}", "update_summary": update_summary}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ---------------------------- Reclone all Repos --------------------------- #

def reclone_repos_internal():
    """Reclone all repositories in the local directory."""
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Define the directory where the repository is located
    repo_dir = os.path.join(data_dir)
    repo_list = os.listdir(repo_dir)

    # Reclone all repositories
    for repo_name in repo_list:
        repo_path = os.path.join(repo_dir, repo_name)

        # Get the original repository URL
        try:
            repo_url = get_repo_url(repo_path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

        # Delete the repository directory
        shutil.rmtree(repo_path)

        # Re-clone the repository
        result = subprocess.run(
            ["git", "clone", repo_url, repo_path],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.stderr,
            )

    return {"message": f"Repositories re-cloned successfully in {repo_dir}"}


@router.post("/archives/all/reclone")
def reclone_repos(api_key: APIKey = Depends(get_api_key)):
    """Reclone all repositories in the local directory."""
    try:
        return reclone_repos_internal()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
