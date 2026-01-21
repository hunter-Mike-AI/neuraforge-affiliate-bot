production v1"
git push origin mainimport os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
COOLDOWN_SECONDS = 60 
[main 7259d3d] fix: remove psycopg2, use sqlite for production v1
 2 files changed, 27 insertions(+), 13 deletions(-)
Username for 'https://github.com': hunter-Mike-AI
Password for 'https://hunter-Mike-AI@github.com':
To https://github.com/hunter-Mike-AI/neuraforge-affiliate-bot.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'https://github.com/hunter-Mike-AI/neuraforge-affiliate-bot.git'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. This is usually caused by another repository pushing to
hint: the same ref. If you want to integrate the remote changes, use
hint: 'git pull' before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.
~/neuraforge-affiliate-bot $
