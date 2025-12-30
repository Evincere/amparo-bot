Write-Host "--- DETENIENDO PROCESOS EN PUERTO 8000 ---"
$p = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($p) { 
    Write-Host "Matando proceso PID: " $p.OwningProcess
    Stop-Process -Id $p.OwningProcess -Force 
} else {
    Write-Host "Puerto 8000 libre."
}

Write-Host "--- ESPERANDO 2 SEGUNDOS ---"
Start-Sleep -Seconds 2

Write-Host "--- INICIANDO SERVIDOR ---"
uvicorn app.main:app --reload --port 8000
