##
## Uso:
##       python transformInitMem.py NOMBRE_ARCHIVO_VERILOG.v
##
##

import sys
import re

if (len(sys.argv)<2):
    print('Ingrese archivo a modificar')
    exit(0)
    
filename = sys.argv[1]
print(filename)
with open(filename,'r') as f:
    body = f.read()

listMem = re.findall('(  reg \[.*\] \S* \[.*\];\n)  initial begin\n((    \S*\[\S*\] = \S*;\n)*)  end\n',body)

#Reemplaza todas la ocurrencias de la secuencia anterior
#crea un archivo "memory dump" nuevo por cada ocurrencia
ocurrence = 0
for found in listMem:
    data= re.findall(r'mem\[.*\] = [0-9]+\'h(.*);',found[1])
    with open(f'memdump{ocurrence}.mem','w') as f:
        for d in data:
            f.write(d)
            f.write('\n')
    body = re.sub(r'(  reg \[.*\] \S* \[.*\];\n)  initial begin\n((    \S*\[\S*\] = \S*;\n)*)  end\n',f'\\1  $readmemh("memdump{ocurrence}.mem", mem);\n',body,1)
    ocurrence=ocurrence +1
fn = filename.split('.')
with open(fn[0]+'_edited.'+fn[1],'w') as f:
    f.write(body)


# A mejorar:
# Espacios alrededor de los '='. Puede que no estén siempre en ese lugar
# Espacios de identado. ¿Puede tener diferente cantidad?
# Nombre de memdump.mem relacionado al nombre de archivo verilog
