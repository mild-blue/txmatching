import gunicorn

# do not disclose what server we're running, recommendation from pen test
# https://stackoverflow.com/a/21294524/7169288
# and
# https://stackoverflow.com/a/56242881/7169288
gunicorn.SERVER_SOFTWARE = 'intentionally-undisclosed-TXM-server'
