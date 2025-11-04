# Download sample video for testing
# This script downloads a sample video file for testing the AI Director system

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Sample Video Downloader" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$sampleVideos = @(
    @{
        Name = "Big Buck Bunny (720p, 1MB)"
        Url = "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
        File = "sample_bigbuck_1mb.mp4"
        Size = "1MB"
    },
    @{
        Name = "Big Buck Bunny (720p, 10MB)"
        Url = "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_10mb.mp4"
        File = "sample_bigbuck_10mb.mp4"
        Size = "10MB"
    },
    @{
        Name = "Sample Video with Speech"
        Url = "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4"
        File = "sample_speech.mp4"
        Size = "~1MB"
    }
)

Write-Host "Available sample videos:" -ForegroundColor Yellow
for ($i = 0; $i -lt $sampleVideos.Count; $i++) {
    Write-Host "$($i + 1)) $($sampleVideos[$i].Name) - $($sampleVideos[$i].Size)" -ForegroundColor White
}
Write-Host ""

$choice = Read-Host "Select a video to download (1-$($sampleVideos.Count))"

if ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le $sampleVideos.Count) {
    $selected = $sampleVideos[[int]$choice - 1]
    
    Write-Host ""
    Write-Host "Downloading: $($selected.Name)" -ForegroundColor Green
    Write-Host "URL: $($selected.Url)" -ForegroundColor Gray
    Write-Host "Output: $($selected.File)" -ForegroundColor Gray
    Write-Host ""
    
    try {
        # Use curl (available in Windows 10+)
        & curl.exe -o $selected.File -L $selected.Url --progress-bar
        
        if (Test-Path $selected.File) {
            $fileSize = (Get-Item $selected.File).Length / 1MB
            Write-Host ""
            Write-Host "Download complete!" -ForegroundColor Green
            Write-Host "File: $($selected.File)" -ForegroundColor Green
            Write-Host "Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
            Write-Host ""
            Write-Host "You can now use this video with:" -ForegroundColor Yellow
            Write-Host "  python main_video.py $($selected.File)" -ForegroundColor White
            Write-Host ""
            Write-Host "Or run:" -ForegroundColor Yellow
            Write-Host "  .\start.ps1" -ForegroundColor White
            Write-Host "  and select option 2" -ForegroundColor White
        } else {
            Write-Host "Download failed." -ForegroundColor Red
        }
    } catch {
        Write-Host "Error downloading video: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Alternative: Download manually from:" -ForegroundColor Yellow
        Write-Host $selected.Url -ForegroundColor White
    }
} else {
    Write-Host "Invalid selection." -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"
