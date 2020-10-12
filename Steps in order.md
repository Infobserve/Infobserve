Steps in order:

* `https://gitlab.com/api/v4/user -H 'PRIVATE-TOKEN: <access token>'` -> Returns user id
* `https://gitlab.com/api/v4/projects?user_id=<user_id>` -> Returns list of projects. Grep/Regex/Find the one in the description -> Get project id
* `https://gitlab.com/api/v4/projects/<project_id>/repository/tree` -> walk it