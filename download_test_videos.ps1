# Download Sample Videos with Speech
# Various test videos with clear audio/dialogue for testing

Write-Host "🎥 Downloading Sample Videos with Audio..." -ForegroundColor Cyan
Write-Host ""

# Check if yt-dlp is installed
$ytdlpInstalled = Get-Command yt-dlp -ErrorAction SilentlyContinue

if (-not $ytdlpInstalled) {
    Write-Host "⚠️  yt-dlp not found. Installing..." -ForegroundColor Yellow
    pip install yt-dlp
    Write-Host ""
}

# Create samples directory
$samplesDir = "sample_videos"
if (-not (Test-Path $samplesDir)) {
    New-Item -ItemType Directory -Path $samplesDir | Out-Null
}

Write-Host "📁 Downloading to: $samplesDir" -ForegroundColor Green
Write-Host ""

# Sample 1: TED Talk (short, clear speech)
Write-Host "1️⃣ Downloading: TED Talk Sample (1 minute)..." -ForegroundColor Cyan
yt-dlp -f "best[height<=480]" `
    --output "$samplesDir/ted_talk_sample.mp4" `
    --no-playlist `
    --download-sections "*0:00-1:00" `
    "https://www.youtube.com/watch?v=8jPQjjsBbIc"

# Sample 2: News Report (formal speech)
Write-Host ""
Write-Host "2️⃣ Downloading: News Report Sample (30 seconds)..." -ForegroundColor Cyan
yt-dlp -f "best[height<=480]" `
    --output "$samplesDir/news_sample.mp4" `
    --no-playlist `
    --download-sections "*0:00-0:30" `
    "https://www.youtube.com/watch?v=qp0HIF3SfI4"

# Sample 3: Interview/Conversation
Write-Host ""
Write-Host "3️⃣ Downloading: Interview Sample (1 minute)..." -ForegroundColor Cyan
yt-dlp -f "best[height<=480]" `
    --output "$samplesDir/interview_sample.mp4" `
    --no-playlist `
    --download-sections "*0:00-1:00" `
    "https://www.youtube.com/watch?v=n4RjJKxsamQ"

Write-Host ""
Write-Host "✅ Download Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📂 Files saved in: $samplesDir\" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎬 Test with:" -ForegroundColor Yellow
Write-Host "   python main_video.py $samplesDir\ted_talk_sample.mp4 --frames 15 --no-audio" -ForegroundColor White
Write-Host "   python main_video.py $samplesDir\news_sample.mp4 --frames 15 --no-audio" -ForegroundColor White
Write-Host "   python main_video.py $samplesDir\interview_sample.mp4 --frames 15 --no-audio" -ForegroundColor White
Write-Host ""
