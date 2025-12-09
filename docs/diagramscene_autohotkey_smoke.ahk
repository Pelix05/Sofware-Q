; AutoHotkey v1 smoke/regression script for the flowchart editor
; Adjust exe path/window title/coords as needed. ASCII-only (match by exe name).
; Env overrides:
;   AHK_EXE_PATH  -> path to diagramscene.exe
;   AHK_LOG_PATH  -> path to write PASS/FAIL log

#SingleInstance Force
#NoEnv
SetTitleMatchMode, 2
SetWorkingDir %A_ScriptDir%
SetDefaultMouseSpeed, 0

; --- CONFIG ---
EnvGet, exeOverride, AHK_EXE_PATH
EnvGet, logOverride, AHK_LOG_PATH

exePath := exeOverride
if (exePath = "")
{
    exePath := "D:\\flowchart_test\\diagramscene.exe"
}

logPath := logOverride
if (logPath = "")
{
    logPath := "D:\\flowchart_test\\workspace\\ahk_result.txt"
}

; clear previous log and start
FileDelete, %logPath%
FileAppend, START`r`n, %logPath%

; Match by process name (ASCII-safe). Change if your exe differs.
winTitle := "ahk_exe diagramscene.exe"

; Canvas coordinates to draw a few shapes (adjust to your screen)
ptRect := { x1: 300, y1: 300, x2: 500, y2: 450 }
ptEllipse := { x1: 600, y1: 300, x2: 750, y2: 430 }
ptArrowStart := { x: 400, y: 380 }
ptArrowEnd   := { x: 700, y: 380 }

; --- HELPERS ---
DrawDrag(x1, y1, x2, y2) {
    MouseMove, x1, y1
    Sleep, 80
    MouseClick, left, x1, y1, 1, 0, D
    Sleep, 80
    MouseMove, x2, y2
    Sleep, 80
    MouseClick, left, x2, y2, 1, 0, U
    Sleep, 120
}

; --- MAIN ---
if !FileExist(exePath) {
    FileAppend, FAIL: exe not found`r`n, %logPath%
    ExitApp, 1
}
FileAppend, PASS: exe exists`r`n, %logPath%

Run, %exePath%
WinWait, %winTitle%, , 15
if ErrorLevel {
    FileAppend, FAIL: window not found %winTitle%`r`n, %logPath%
    ExitApp, 1
}
FileAppend, PASS: window found %winTitle%`r`n, %logPath%
WinActivate, %winTitle%
Sleep, 500

; Smoke: new scene via Ctrl+N (if supported)
FileAppend, STEP: new scene (Ctrl+N)`r`n, %logPath%
Send, ^n
Sleep, 300
FileAppend, PASS: new scene`r`n, %logPath%

; Draw rectangle
FileAppend, STEP: draw rectangle`r`n, %logPath%
DrawDrag(ptRect.x1, ptRect.y1, ptRect.x2, ptRect.y2)
FileAppend, PASS: rectangle`r`n, %logPath%

; Draw ellipse/circle
FileAppend, STEP: draw ellipse`r`n, %logPath%
DrawDrag(ptEllipse.x1, ptEllipse.y1, ptEllipse.x2, ptEllipse.y2)
FileAppend, PASS: ellipse`r`n, %logPath%

; Draw a line/arrow (depends on current tool; ensure line/arrow tool is selected)
FileAppend, STEP: draw line/arrow`r`n, %logPath%
MouseMove, ptArrowStart.x, ptArrowStart.y
Sleep, 80
MouseClick, left, ptArrowStart.x, ptArrowStart.y, 1, 0, D
Sleep, 80
MouseMove, ptArrowEnd.x, ptArrowEnd.y
Sleep, 80
MouseClick, left, ptArrowEnd.x, ptArrowEnd.y, 1, 0, U
Sleep, 120
FileAppend, PASS: line/arrow`r`n, %logPath%

; Select all and copy/paste to test clipboard ops
FileAppend, STEP: select all and copy/paste`r`n, %logPath%
Send, ^a
Sleep, 120
Send, ^c
Sleep, 120
Send, ^v
Sleep, 200
FileAppend, PASS: copy/paste`r`n, %logPath%

; Undo / Redo
FileAppend, STEP: undo then redo`r`n, %logPath%
Send, ^z
Sleep, 150
Send, ^y
Sleep, 150
FileAppend, PASS: undo/redo`r`n, %logPath%

; Zoom shortcut (Ctrl + mouse wheel up/down) – adjust if your app uses other keys
FileAppend, STEP: zoom in/out`r`n, %logPath%
Send, ^{WheelUp 3}
Sleep, 200
Send, ^{WheelDown 3}
Sleep, 200
FileAppend, PASS: zoom`r`n, %logPath%

; Save as (Ctrl+S) – will prompt; you can confirm manually
FileAppend, STEP: save (Ctrl+S)`r`n, %logPath%
Send, ^s
Sleep, 500
FileAppend, PASS: save`r`n, %logPath%

; Close app
FileAppend, STEP: close app (Alt+F4)`r`n, %logPath%
Send, !{F4}
Sleep, 500
FileAppend, PASS: smoke completed`r`n, %logPath%
ExitApp, 0
