import pyvisa

print(pyvisa.__version__)

rm = pyvisa.ResourceManager('@ni')
print(rm.list_resources())