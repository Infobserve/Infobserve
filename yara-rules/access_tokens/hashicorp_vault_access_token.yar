rule HashicorpVaultAccessTokenRule
{
    meta:
        name = "Hashicorp's Vault Access Token"
        author = "Infobserve team"
        date = "2020-02-24"

        /* Test Cases */
        test_match_1 = "s.OZZFOsivUeOMeDyFtRz7cOmE"

    strings:
        $ = /s.[0-9A-Za-z]{24}/ fullword

    condition:
        any of them
}
