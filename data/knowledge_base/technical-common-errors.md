# Technical: Common Errors and Crashes

This article covers the most frequent technical support issues.

## "500 Internal Server Error" on checkout

Usually transient. Ask the customer to retry after clearing cache. If it
persists for more than 10 minutes across multiple customers, this is a
platform incident, not a one-off ticket — flag it.

## App crashes on startup

Almost always caused by an out-of-date app version on older OS versions.
Ask for app version and OS version, then point to the latest download link.

## Slow performance / timeouts

Usually related to large data exports. Ask what action was being performed
when the slowdown occurred. Exports over 50,000 rows should be done via the
async export tool, not the live UI.
