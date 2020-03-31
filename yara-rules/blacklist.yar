rule BlacklistRule
{
    meta:
        name = "Blacklist"
        author = "infobserve-team"
        date = "2020-03-25"
        test_match_1 = "Technic Launcher is starting"

    strings:
        $a = "#EXTINF:" nocase // IPTV streams
        $b = "Technic Launcher is starting" // Minecraft mod dumps

    condition:
        any of them
}