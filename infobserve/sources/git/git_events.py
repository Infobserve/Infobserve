class GitlabEvents:
    class Actions:
        created= None
        updated= None
        closed= None
        reopened= None
        pushed= None # We care about this
        commented= None
        merged= None
        joined= None
        left= None
        destroyed= None
        expired= None

    class TargetTypes:
        issue = None
        milestone = None
        merge_request = None
        note = None
        project = None
        snippet = None
        user = None