#Requires AutoHotkey v2.0

; Map CapsLock to Shift for toggling Chinese/English in Microsoft Bopomofo
$CapsLock::
{
    Send("{Shift}")
}

; Use Shift + CapsLock to toggle the actual CapsLock state (uppercase/lowercase)
$+CapsLock::
{
    SetCapsLockState(!GetKeyState("CapsLock", "T"))
}