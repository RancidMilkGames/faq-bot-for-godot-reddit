import praw  # Reddit API Wrapper
import re  # Regular Expressions
import logging  # Logging
from dotenv import dotenv_values  # Environment variables

# Import "environment" variables
config: dict = dotenv_values(".env")
# Set up logging. It's currently a very simple single file, but that's likely to change to a more sophisticated system.
logging.basicConfig(filename='bot.log', encoding='utf-8', level=logging.getLevelName(config["LOG_LEVEL"]))

# Initialize Reddit instance(PRAW)
reddit: praw.reddit.Reddit = praw.Reddit(
    client_id=config["CLIENT_ID"],
    client_secret=config["CLIENT_SECRET"],
    user_agent=config["USER_AGENT"],
    username=config["USERNAME"],
    password=config["PASSWORD"]
)

# Subreddit to monitor
subreddit: praw.reddit.Subreddit = reddit.subreddit(config["MONITOR_SUBREDDIT"])
# Regex pattern for GDScript vs C# check
gd_vs_cs_pattern: str = r"(?=.*gdscript)(?=.*c#)(difference|different|vs)"
# Amount of posts to skip initially. The stream gives us the last 100 posts, so might want to skip those
skip_initial_count: int = 0

# If in production, skip the first 100 posts
if config["ENVIRONMENT"] == "production":
    skip_initial_count = 100


# Main loop
def main() -> None:
    global skip_initial_count
    try:
        # Iterate through all new posts in the subreddit
        for submission in subreddit.stream.submissions():
            # Skip the first 100 posts if we are in production
            if skip_initial_count > 0:
                skip_initial_count -= 1
                continue

            # Functions to check for question patterns and respond if found
            gdscript_vs_cs(submission)

    except Exception as e:
        logging.error("Exception occurred in main loop: %s", e)


# Function to check if a post is about GDScript vs C# and respond
def gdscript_vs_cs(submission: praw.Reddit.submission) -> None:
    global gd_vs_cs_pattern
    try:
        # Check if the post title matches the GDScript vs C# pattern
        title_matched = re.search(pattern=gd_vs_cs_pattern, string=submission.title, flags=re.IGNORECASE)
        if not title_matched:
            logging.debug("Post did not match search criteria: %s", submission.title)
            # Post doesn't match the search criteria, so we don't want to comment on it
            return

        # Check if the bot has already commented on the post to avoid spam
        top_level_comments: list = list(submission.comments)
        for comment in top_level_comments:
            if comment.author == reddit.user.me():
                logging.debug("Bot already commented on post: %s", submission.title)
                # Bot already commented so no need to comment again
                return

        # The bot hasn't commented on the post and the post matches the search criteria
        # Get our message(Currently Static). In the future I was thinking it might be nice to have dynamic components.
        message: str = open('answers/gd_vs_cs.md', 'r').read()
        # Comment on the post
        submission.reply(message)
        logging.info("Bot commented on post: %s", submission.title)

    except Exception as e:
        logging.warning("Error occurred in GDScript vs C#. Title: %s. Error: %s", submission.title, e)


if __name__ == "__main__":
    main()
