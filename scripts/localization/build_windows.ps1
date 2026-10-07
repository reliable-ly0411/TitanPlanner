# Build the Windows application using an independent .NET 8 SDK (no Visual Studio IDE).
param([string]$DotNet = 'dotnet', [string]$Configuration = 'Release', [string]$OutputDirectory = '')
$ErrorActionPreference = 'Continue'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Push-Location $root
try {
    & $DotNet build ExtLibs\DriverCleanup\DriverCleanup.csproj -c $Configuration
    if ($LASTEXITCODE -ne 0) { throw "DriverCleanup build failed ($LASTEXITCODE)" }
    $outputArgs = @()
    if ($OutputDirectory) { $outputArgs = @("-p:TitanPlannerOutputDirectory=$($OutputDirectory.TrimEnd('\'))\") }
    & $DotNet build MissionPlanner.csproj -c $Configuration -m:2 `
        -p:GenerateResourceUsePreserializedResources=true -p:GenerateSerializationAssemblies=Off @outputArgs
    if ($LASTEXITCODE -ne 0) { throw "MissionPlanner build failed ($LASTEXITCODE)" }
} finally {
    Pop-Location
}
