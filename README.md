# MastoPostSched
Scripted batch operation for scheduling Mastodon posts. It takes a configuration file which includes:

- **access-token** : Mastodon access token with at least write:statuses permissions.
- **server** : Mastodon server domain, i.e. mastodon.social.
- **log-directory** : Path to a directory for logs.
- **log-level** : Specify the log level, either error, info, or debug.

The script also requires a comma-delimited CSV file containing columns with the following headers:

- **post_date** : The date that the status is meant to be posted, format: 2024-12-31.
- **status** : The text of the status / post.
- **sensitive** : Specifies whether the post should be marked as sensitive. If so, enter Y.
- **spoiler_text** : The text which appears if the post is marked as sensitive.
- **visibility** : Visibility of the post. Options are: public, unlisted, private, direct

For both the config file and the CSV a sample has been provided, though the values in the config file are non-functioning.

> py schedPost.py -c sample_config.json --file sample_file.csv

The script does require the use of (Requests)[https://pypi.org/project/requests/].

## Notes
The initial version of this is very basic, with lots of improvements that could be made. This mostly serves, right now, as an example of how this could be done.

Some improvements that could (and probably should) be made that come to mind:

- **Rate limit checking** : Right now it does not check against rate limits as it's posting, so if it is used to post too many items within 5 minutes it may begin to fail part-way through. Ideally it should check against rate limiting and delay itself.
- **Duplication checking** : This may be a little more difficult, but trying to avoid duplicates would be helpful. It's not entirely clear how it would work beyond a literal exact copy.
- **Validate posting date** : At time of writing the script does not validate that the date provided for a post is in the future at all. It probably should.
- **Validate posting time** : Mastodon has a weird thing with scheduling posts, requiring that a scheduled post be at least 5 minutes after the current datetime. This script does not check for that, but probably should.
- **Posting time parameter** : The script is currently written to post at 8:00 AM Mountain Standard Time for each day. Ideally this should either be parameterized or specified per-post in the csv file.
- **Support for media** : Right now this just doesn't do media at all.
- **Reporting** : It would probably be nice if it could write to a pair of CSVs the successful and failed post data. This would be useful for being able to re-try failed posts.
- **Additional functions** : Right now this is only setup to manage adding posts, but it would be nice to expand it into generating a CSV of already-scheduled posts, updating scheduled posts, and deleting scheduled posts.