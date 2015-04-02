@echo '–∂‘ÿzkdm'

sc stop zonekey.service.dm
sc delete zonekey.service.dm

taskkill /f /im python.exe

rd /s /q c:\zkdm
