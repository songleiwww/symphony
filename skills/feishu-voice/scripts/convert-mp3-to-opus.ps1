#Requires -Version 5.1
<#
.SYNOPSIS
    Convert MP3 audio to Feishu-compliant OPUS format.

.DESCRIPTION
    Converts an MP3 file to OPUS format required by Feishu audio bubble messages.
    Requirements: mono channel (-ac 1), 16000 Hz sample rate (-ar 16000)

.PARAMETER InputFile
    Path to the source MP3 file

.PARAMETER OutputFile
    Path for the output OPUS file (default: replaces .mp3 extension with .opus)

.EXAMPLE
    .\convert-mp3-to-opus.ps1 -InputFile "voice.mp3"
    # Output: voice.opus in same directory

.EXAMPLE
    .\convert-mp3-to-opus.ps1 -InputFile "C:\temp\voice.mp3" -OutputFile "C:\temp\voice.opus"
#>
param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateScript({Test-Path $_ -PathType Leaf})]
    [string]$InputFile,

    [Parameter(Mandatory=$false, Position=1)]
    [string]$OutputFile
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "FFmpeg not found. Install FFmpeg and ensure it's in PATH."
}

if ([string]::IsNullOrWhiteSpace($OutputFile)) {
    $OutputFile = [IO.Path]::ChangeExtension($InputFile, '.opus')
}

$InputFile = (Resolve-Path $InputFile).Path
$OutputFile = (Resolve-Path (Split-Path $OutputFile -Parent) -ErrorAction SilentlyContinue).Path + '\' + (Split-Path $OutputFile -Leaf)

Write-Host "Converting: $InputFile"
Write-Host "Output:     $OutputFile"

& ffmpeg -i "$InputFile" -acodec libopus -ac 1 -ar 16000 "$OutputFile" -y 2>&1 | ForEach-Object {
    if ($_ -match 'error' -or $_ -match 'invalid') { Write-Host $_ -ForegroundColor Red }
}

if (Test-Path $OutputFile) {
    $size = (Get-Item $OutputFile).Length
    Write-Host "Success! Output size: $size bytes"
} else {
    Write-Error "Conversion failed - output file not found"
}
