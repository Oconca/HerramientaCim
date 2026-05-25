import zipfile
import xml.etree.ElementTree as ET
import json

def parse_xlsx(filepath):
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            shared_strings = []
            if 'xl/sharedStrings.xml' in z.namelist():
                xml_content = z.read('xl/sharedStrings.xml')
                root = ET.fromstring(xml_content)
                namespace = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
                if namespace:
                    for si in root.findall('ns:si', namespace):
                        texts = [t.text for t in si.findall('.//ns:t', namespace) if t.text]
                        shared_strings.append(''.join(texts))
                else:
                    for si in root.findall('.//si'):
                        texts = [t.text for t in si.findall('.//t') if t.text]
                        shared_strings.append(''.join(texts))
            
            sheet_path = 'xl/worksheets/sheet1.xml'
            if sheet_path not in z.namelist():
                sheets = [n for n in z.namelist() if n.startswith('xl/worksheets/')]
                if not sheets:
                    return None
                sheet_path = sheets[0]
                
            sheet_xml = z.read(sheet_path)
            root = ET.fromstring(sheet_xml)
            namespace = {'ns': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
            
            rows = []
            if namespace:
                sheetData = root.find('ns:sheetData', namespace)
                for row in sheetData.findall('ns:row', namespace):
                    row_data = []
                    for c in row.findall('ns:c', namespace):
                        t = c.get('t')
                        v = c.find('ns:v', namespace)
                        val = v.text if v is not None else ''
                        if t == 's' and val:
                            val = shared_strings[int(val)]
                        
                        # Only append if we haven't stripped too much, but let's just keep structure
                        row_data.append(val)
                    
                    # Trim empty trailing cells
                    while row_data and row_data[-1] == '':
                        row_data.pop()
                        
                    if any(row_data):
                        rows.append(row_data)
            else:
                sheetData = root.find('sheetData')
                for row in sheetData.findall('row'):
                    row_data = []
                    for c in row.findall('c'):
                        t = c.get('t')
                        v = c.find('v')
                        val = v.text if v is not None else ''
                        if t == 's' and val:
                            val = shared_strings[int(val)]
                        row_data.append(val)
                        
                    while row_data and row_data[-1] == '':
                        row_data.pop()
                        
                    if any(row_data):
                        rows.append(row_data)
                    
            return rows
    except Exception as e:
        return {"error": str(e)}

filepath = r'c:\Users\Javier\Desktop\Javier\Oconca\cimtra-oconca.xlsx'
data = parse_xlsx(filepath)
with open(r'c:\Users\Javier\Desktop\Javier\Oconca\cimtra_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("Done")
