import praw
from typing import Generator, Optional, Iterator
import os
from dotenv import load_dotenv
import praw


def get_reddit() -> praw.Reddit:
    return praw.Reddit(
        client_id=os.environ["REDDIT_CLIENT_ID"],
        client_secret=os.environ["REDDIT_CLIENT_SECRET"],
        user_agent=os.environ["REDDIT_USER_AGENT"],
    )


def load_subreddits(filename: str) -> list[str]:
    "Expects text file with each line like -> 'r/BetterEveryLoop'"
    with open(filename, "r", encoding="utf-8") as f:
        return [line.split('/')[-1].strip() for line in f if not line.startswith("#")]


def has_suitable_video(submission: praw.reddit.Submission) -> bool:
    if hasattr(submission, "is_video") and submission.is_video:
        return True
    if hasattr(submission, "url"):
        url = submission.url.lower()
        video_extensions = (".mp4", ".gifv", ".webm", ".mov")
        return url.endswith(video_extensions)
    return False


def is_duration_short(submission: praw.reddit.Submission, max_duration: int = 25) -> bool:
    if hasattr(submission, "media") and submission.media:
        media = submission.media.get("reddit_video")
        if media and "duration" in media:
            return media["duration"] <= max_duration
    return False


def is_upvoted(submission: praw.reddit.Submission) -> bool:
    return (
        submission.score > 0
        and submission.upvote_ratio >= 0.5
        and submission.score < 10000
    )


def get_new_hot(
    subreddit: praw.reddit.Subreddit, limit: int = 5
) -> Iterator[praw.reddit.Submission]:
    return subreddit.hot(limit=limit)


def is_post_suitable(submission: praw.reddit.Submission) -> bool:
    return (
        has_suitable_video(submission)
        and is_upvoted(submission)
        and is_duration_short(submission)
        and not submission.stickied
    )

if __name__ == "__main__":
    load_dotenv()
    reddit = get_reddit()
    subreddits = load_subreddits("subreddits.txt")

    for subreddit_name in subreddits:
        if not subreddit_name:
            continue
        subreddit = reddit.subreddit(subreddit_name)
        print(f"\nSearching in r/{subreddit_name}...\n")
        submissions = get_new_hot(subreddit, limit=2)
        for submission in submissions:
            if is_post_suitable(submission):
                print(f"Title: {submission.title}")
                print(f"URL  : {submission.url}")
                print(f"Score: {submission.score}")
                print(f"ID   : {submission.id}")
                print(f"Subreddit: {submission.subreddit.display_name}")
                print(
                    f"Author: {submission.author.name if submission.author else 'Anonymous'}\n"
                )
