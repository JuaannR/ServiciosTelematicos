Comandos de interés, así como ejemplo de ejecución:

PASAR ALGO DE LA MAQUINA VIRTUAL A LA MAQUINA FISICA:
scp usuarioMV@IP_MV:/ruta_de_lo_que_quieres_pasar ruta_en_tu_pc_fisico_donde_se_guarda

En caso de Juan:
scp alumno@192.168.56.102:/home/alumno/web_sstt_plantilla/servidor.log /c/Users/juani/Desktop/
 
---------------------------------------------------------------------------------------------

PASAR ALGO DE LA MAQUINA FISICA A LA MAQUINA VIRTUAL
scp ruta_en_tu_pc_fisico_de_lo_que_quieres_pasar usuarioMV@IP_MV:/ruta_MV_donde_se_guarda

En caso de Juan:
scp /c/Users/juani/Desktop/web_sstt_plantilla.zip alumno@192.168.56.102:/home/alumno

---------------------------------------------------------------------------------------------

Comando ejecución web_sstt.py desde la MV servidor:

Caso de Juan:
python3 web_sstt.py -p 8080 -ip 192.168.56.102 -wb ./

---------------------------------------------------------------------------------------------

Acceso a web_sstt.py desde Firefox MV cliente
http://192.168.56.102:8080/


