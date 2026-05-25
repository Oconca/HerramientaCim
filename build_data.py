import json

def procesar_datos(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Ignorar la primera fila (encabezados principales)
    filas = data[1:]
    
    campos = []
    campo_actual = None
    bloques_en_campo = []
    bloque_actual = None
    aspecto_actual = None
    
    ca_id = 0
    b_id = 0
    a_id = 0
    c_id = 0

    for fila in filas:
        if not fila:
            continue
            
        fila_str = [str(x).strip() if x is not None else "" for x in fila]
        
        if len(fila_str) > 3 and not fila_str[4] and fila_str[0] == "":
            continue
            
        if "Criterio" in fila_str and "No existe informacion" in fila_str:
            continue
            
        campo = fila_str[0] if len(fila_str) > 0 else ""
        bloque = fila_str[1] if len(fila_str) > 1 else ""
        aspecto = fila_str[2] if len(fila_str) > 2 else ""
        puntos = fila_str[3] if len(fila_str) > 3 else ""
        criterio = fila_str[4] if len(fila_str) > 4 else ""
        
        if "Total de Puntos" in aspecto or "Calificaci" in criterio:
            continue

        
        # Nuevo campo
        if campo and "Campo:" in campo:
            ca_id += 1
            if campo_actual:
                if bloque_actual:
                    bloques_en_campo.append(bloque_actual)
                if bloques_en_campo:
                    campo_actual['bloques'] = bloques_en_campo
                    campos.append(campo_actual)
            
            campo_actual = {
                "id": ca_id,
                "nombre": campo.replace("Campo:", "").strip(),
                "bloques": []
            }
            bloques_en_campo = []
            bloque_actual = None
            aspecto_actual = None
            
        # Si hay un nuevo bloque
        if bloque and "BLOQUE" in bloque.upper():
            b_id += 1
            if bloque_actual:
                 bloques_en_campo.append(bloque_actual)
                 
            bloque_actual = {
                "id": b_id,
                "nombre": bloque,
                "aspectos": []
            }
            aspecto_actual = None
            
        # Determinar nuevo aspecto
        if aspecto and len(aspecto) > 5 and aspecto[0].isdigit() and aspecto[1] == '.':
             a_id += 1
             aspecto_actual = {
                "id": a_id,
                "titulo": aspecto,
                "criterios": []
             }
             if not bloque_actual:
                 b_id += 1
                 bloque_actual = {
                     "id": b_id,
                     "nombre": "BLOQUE GENERAL",
                     "aspectos": []
                 }
             bloque_actual['aspectos'].append(aspecto_actual)
        
        elif aspecto and len(aspecto) > 5 and not (aspecto[0].isdigit() and aspecto[1] == '.'):
             a_id += 1
             aspecto_actual = {
                "id": a_id,
                "titulo": aspecto,
                "criterios": []
             }
             if not bloque_actual:
                 b_id += 1
                 bloque_actual = {
                     "id": b_id,
                     "nombre": "BLOQUE GENERAL",
                     "aspectos": []
                 }
             bloque_actual['aspectos'].append(aspecto_actual)
            
        # Si hay un criterio
        if criterio and len(criterio) > 2 and puntos.isdigit():
            c_id += 1
            nuevo_criterio = {
                "id": c_id,
                "puntos": puntos,
                "descripcion": criterio,
                "cumple": None,
                "errores": {
                    "no_existe": False,
                    "no_actualizada": False,
                    "no_corresponde": False,
                    "ilegible": False,
                    "enlace_roto": False
                },
                "comentario": ""
            }
            if not aspecto_actual and bloque_actual:
                if not bloque_actual['aspectos']:
                    bloque_actual['aspectos'].append({"id": 999, "titulo": "Criterios", "criterios": []})
                aspecto_actual = bloque_actual['aspectos'][-1]
                
            if aspecto_actual:
                aspecto_actual['criterios'].append(nuevo_criterio)

    # Limpiar lo sobrante
    if bloque_actual:
         bloques_en_campo.append(bloque_actual)
    if campo_actual and bloques_en_campo:
        campo_actual['bloques'] = bloques_en_campo
        campos.append(campo_actual)

    # Limpieza final de elementos vacios
    campos_limpios = []
    for c in campos:
        bloques_limpios = []
        for b in c['bloques']:
            aspectos_limpios = [a for a in b['aspectos'] if a['criterios']]
            if aspectos_limpios:
                b['aspectos'] = aspectos_limpios
                bloques_limpios.append(b)
        if bloques_limpios:
            c['bloques'] = bloques_limpios
            campos_limpios.append(c)

    js_content = f"const cimtraData = {json.dumps(campos_limpios, indent=2, ensure_ascii=False)};\n"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"Archivo {output_file} generado con {len(campos_limpios)} campos de evaluacion.")

if __name__ == "__main__":
    input_f = r'c:\Users\Javier\Desktop\Javier\Oconca\cimtra_data.json'
    output_f = r'c:\Users\Javier\Desktop\Javier\Oconca\sneat\assets\js\cimtra_data.js'
    procesar_datos(input_f, output_f)
