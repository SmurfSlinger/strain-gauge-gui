import os
print(">>> __main__.py START <<<")


os.environ["PYVISA_LIBRARY"] = r"C:\Windows\System32\visa64.dll"
print("PYVISA_LIBRARY set to:", os.environ["PYVISA_LIBRARY"])


import sys
print("Python executable:", sys.executable)


from .app import main
print("Imported app.main successfully")


raise SystemExit(main())