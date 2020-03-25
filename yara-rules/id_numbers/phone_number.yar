rule PhoneNumberRule
{
    meta:
        name = "Phone Number"
        author = "github.com/pseudo-security"
        date = "2020-01-01"

        /* Test Cases */
        test_match_1 = "Give them a call at 555-867-5309."
        test_match_2 = "Give them a call at +1 555-555-5555"
        test_match_3 = "Give them a call at +020 555-555-5555"

    strings:
        $1 = /(\+[0-9]{1,3}\s?)?[0-9]{3}-[0-9]{3}-[0-9]{4}/
        $2 = /(\+[0-9]{1,3}\s?)?\([0-9]{3}\) [0-9]{3}-[0-9]{4}/

    condition:
        any of them
}