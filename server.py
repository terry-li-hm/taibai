#!/usr/bin/env python3
"""
Taibai MCP Server - Dedao learning platform integration via dedao-dl
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Literal

from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialize MCP server
mcp = FastMCP("taibai", version="0.2.0")

# Configuration
HOME = Path.home()
TAIBAI_DIR = HOME / ".taibai"
DEFAULT_VAULT_DIR = Path(os.getenv(
    "DEDAO_DOWNLOAD_DIR",
    HOME / "ideaverse-zero-2" / "Atlas" / "Sources" / "Dedao" / "Courses"
))

# Ensure directories exist
TAIBAI_DIR.mkdir(exist_ok=True)
DEFAULT_VAULT_DIR.mkdir(parents=True, exist_ok=True)


# Pydantic models for validation
class LoginArgs(BaseModel):
    qrcode: bool | None = Field(False, description="Login via QR code")
    cookie: str | None = Field(None, description="Login via cookie string")


class ListCoursesArgs(BaseModel):
    include_details: bool | None = Field(
        False, description="Include detailed course information"
    )


class CourseDetailsArgs(BaseModel):
    course_id: str = Field(..., description="Course ID to get details for")


class DownloadCourseArgs(BaseModel):
    course_id: str = Field(..., description="Course ID to download")
    format: Literal["pdf", "markdown", "mp3"] | None = Field(
        "markdown", description="Output format"
    )
    output_dir: str | None = Field(None, description="Output directory path")


class ArticleDetailsArgs(BaseModel):
    article_id: str = Field(..., description="Article ID to get details for")


class DownloadArticleArgs(BaseModel):
    article_id: str = Field(..., description="Article ID to download")
    format: Literal["pdf", "markdown"] | None = Field(
        "markdown", description="Output format"
    )
    output_dir: str | None = Field(None, description="Output directory path")




# Helper functions
def check_dedao_dl() -> bool:
    """Check if dedao-dl is installed"""
    try:
        subprocess.run(["dedao-dl", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_dedao_auth() -> bool:
    """Check if authenticated with Dedao"""
    try:
        subprocess.run(
            ["dedao-dl", "who"],
            cwd=TAIBAI_DIR,
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def execute_dedao_dl(
    args: list[str],
    interactive: bool = False,
    cwd: Path | None = None
) -> str:
    """Execute dedao-dl command"""
    if not check_dedao_dl():
        raise RuntimeError(
            "dedao-dl is not installed. "
            "Please install it first: go install github.com/yann0917/dedao-dl@latest"
        )

    working_dir = cwd or TAIBAI_DIR

    if interactive:
        # Interactive mode for QR code login
        result = subprocess.run(
            ["dedao-dl"] + args,
            cwd=working_dir,
            text=True
        )
        return "Interactive command completed"
    else:
        result = subprocess.run(
            ["dedao-dl"] + args,
            cwd=working_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout


def move_downloaded_files(target_dir: Path) -> None:
    """Move files from ~/.taibai/output/ to target directory"""
    source_dir = TAIBAI_DIR / "output"

    if not source_dir.exists():
        return

    target_dir.mkdir(parents=True, exist_ok=True)

    # Move all items from output directory
    for item in source_dir.iterdir():
        target_path = target_dir / item.name

        # Remove target if it exists
        if target_path.exists():
            if target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                target_path.unlink()

        # Move item to target
        shutil.move(str(item), str(target_path))

    # Try to remove empty output directory
    try:
        source_dir.rmdir()
    except OSError:
        pass  # Directory not empty or doesn't exist


# MCP Tools
@mcp.tool()
def dedao_login(args: LoginArgs) -> str:
    """Login to Dedao platform via QR code or cookie"""
    cmd_args = ["login"]

    if args.qrcode:
        cmd_args.append("-q")
        execute_dedao_dl(cmd_args, interactive=True)
        return "QR code login completed. Please check if login was successful."

    if args.cookie:
        cmd_args.extend(["--cookie", args.cookie])

    result = execute_dedao_dl(cmd_args)
    return result or "Login successful"


@mcp.tool()
def dedao_list_courses(args: ListCoursesArgs) -> str:
    """List all purchased courses"""
    if not check_dedao_auth():
        raise RuntimeError("Not logged in to Dedao. Please use dedao_login first.")

    cmd_args = ["course"]
    if args.include_details:
        cmd_args.append("-d")

    return execute_dedao_dl(cmd_args)


@mcp.tool()
def dedao_course_details(args: CourseDetailsArgs) -> str:
    """Get detailed information about a specific course"""
    if not check_dedao_auth():
        raise RuntimeError("Not logged in to Dedao. Please use dedao_login first.")

    cmd_args = ["detail", args.course_id]
    return execute_dedao_dl(cmd_args)


@mcp.tool()
def dedao_download_course(args: DownloadCourseArgs) -> str:
    """Download a course in specified format"""
    if not check_dedao_auth():
        raise RuntimeError("Not logged in to Dedao. Please use dedao_login first.")

    cmd_args = ["dl", args.course_id]

    # Format mapping
    format_map = {"mp3": "1", "pdf": "2", "markdown": "3"}
    if args.format:
        cmd_args.extend(["-t", format_map[args.format]])

    # Include hot comments for community insights
    cmd_args.append("-c")

    # Execute download (always from ~/.taibai for authentication)
    execute_dedao_dl(cmd_args)

    # Move files to target directory
    target_dir = Path(args.output_dir) if args.output_dir else DEFAULT_VAULT_DIR
    move_downloaded_files(target_dir)

    return f"Course {args.course_id} downloaded successfully to {target_dir}"


@mcp.tool()
def dedao_article_details(args: ArticleDetailsArgs) -> str:
    """Get detailed information about a specific article"""
    if not check_dedao_auth():
        raise RuntimeError("Not logged in to Dedao. Please use dedao_login first.")

    cmd_args = ["article", "detail", args.article_id]
    return execute_dedao_dl(cmd_args)


@mcp.tool()
def dedao_download_article(args: DownloadArticleArgs) -> str:
    """Download an article in specified format"""
    if not check_dedao_auth():
        raise RuntimeError("Not logged in to Dedao. Please use dedao_login first.")

    cmd_args = ["article", "dl", args.article_id]

    # Format mapping
    format_map = {"pdf": "2", "markdown": "3"}
    if args.format:
        cmd_args.extend(["-t", format_map[args.format]])

    # Execute download
    execute_dedao_dl(cmd_args)

    # Move files to target directory
    target_dir = Path(args.output_dir) if args.output_dir else DEFAULT_VAULT_DIR
    move_downloaded_files(target_dir)

    return f"Article {args.article_id} downloaded successfully to {target_dir}"




if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
