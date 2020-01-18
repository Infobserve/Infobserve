
rule pass {
    strings:
        $pass = /pass(w(or)?d|:).*/ nocase

    condition:
        $pass
}