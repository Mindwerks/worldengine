$URL = http://www.hdfgroup.org/ftp/HDF5/current/bin/windows/hdf5-1.8.15-patch1-win32-vs2013-shared.zip

function main () {
    $basedir = $pwd.Path + "\"
    $filename = "hdf5.zip"
    $filepath = $basedir + $filename
    Write-Host "Downloading" $filename "from" $URL
    $retry_attempts = 3
    for($i=0; $i -lt $retry_attempts; $i++){
        try {
            $webclient.DownloadFile($URL, $filepath)
            break
        }
        Catch [Exception]{
            Start-Sleep 1
        }
    }
    $outpath = $basedir + "\hdf5_unzipped"
    [System.IO.Compression.ZipFile]::ExtractToDirectory($filepath, $outpath)
    $msipath = $outpath + "\HDF5-1.8.15-win64.msi"
    Invoke-Command -ScriptBlock { & cmd /c "msiexec.exe /i $msipath" /qn ADVANCED_OPTIONS=1 CHANNEL=100}
}

main