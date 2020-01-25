rule mail {
    strings:
        $mail = /\w*@\w*\.\w*/

    condition:
        $mail
}