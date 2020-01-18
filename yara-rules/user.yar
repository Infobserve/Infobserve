rule user {
    strings:
        $user = /user(name|:).*/ nocase
    condition:
        $user
}
