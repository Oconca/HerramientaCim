import openpyxl
import json
import os

wb = openpyxl.load_workbook("Congreso.xlsx", data_only=True)
ws = wb.active

campos_dict = {}
current_campo = "General"
current_bloque = "General"
current_aspecto = "Criterios"

for row in ws.iter_rows(min_row=2):
    campo_val = row[0].value
    bloque_val = row[1].value
    aspecto_val = row[2].value
    puntos_val = row[3].value
    criterio_val = row[4].value
    
    if campo_val and isinstance(campo_val, str) and str(campo_val).strip() != "":
        current_campo = str(campo_val).strip()
    if bloque_val and isinstance(bloque_val, str) and str(bloque_val).strip() != "":
        current_bloque = str(bloque_val).strip()
    if aspecto_val and isinstance(aspecto_val, str) and str(aspecto_val).strip() != "":
        current_aspecto = str(aspecto_val).strip()
        
    if "CALIFICACI" in str(criterio_val).upper() or "RESULTADO POR BLOQUES" in str(criterio_val).upper() or "TOTAL DE PUNTOS" in str(aspecto_val).upper():
        break
        
    if str(criterio_val).strip() == "None":
        continue
        
    criterio_desc = str(criterio_val).strip() if criterio_val is not None else ""
    
    if not criterio_desc or "None" == criterio_desc:
        continue
        
    puntos = str(puntos_val).strip() if puntos_val is not None else "1"
    if puntos == "None": puntos = "1"
    
    if current_campo not in campos_dict:
        campos_dict[current_campo] = {}
    if current_bloque not in campos_dict[current_campo]:
        campos_dict[current_campo][current_bloque] = {}
    if current_aspecto not in campos_dict[current_campo][current_bloque]:
        campos_dict[current_campo][current_bloque][current_aspecto] = []
        
    campos_dict[current_campo][current_bloque][current_aspecto].append({
        "descripcion": criterio_desc,
        "puntos": puntos,
        "cumple": None,
        "errores": {
            "no_existe": False,
            "no_actualizada": False,
            "no_corresponde": False,
            "ilegible": False,
            "enlace_roto": False
        }
    })

# Flatten dict
campos_list = []
c_id = 1000
b_id = 1000
a_id = 1000
crit_id = 1000

for c_name, bloques in campos_dict.items():
    campo_obj = {"id": c_id, "nombre": c_name, "bloques": []}
    c_id += 1
    for b_name, aspectos in bloques.items():
        bloque_obj = {"id": b_id, "nombre": b_name, "aspectos": []}
        b_id += 1
        for a_name, criterios in aspectos.items():
            aspecto_obj = {"id": a_id, "titulo": a_name, "criterios": []}
            a_id += 1
            for crit in criterios:
                crit_obj = crit.copy()
                crit_obj["id"] = crit_id
                crit_id += 1
                aspecto_obj["criterios"].append(crit_obj)
            bloque_obj["aspectos"].append(aspecto_obj)
        campo_obj["bloques"].append(bloque_obj)
    campos_list.append(campo_obj)

os.makedirs('sneat/assets/js', exist_ok=True)
with open('sneat/assets/js/cimtra_data_congreso.js', 'w', encoding='utf-8') as f:
    f.write('const cimtraDataCongreso = ')
    f.write(json.dumps(campos_list, ensure_ascii=False, indent=2))
    f.write(';\n')
print(f"Conversion complete! Processed {len(campos_list)} campos.")
