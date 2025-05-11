import sys
import json
import os
import csv
from datetime import datetime

def read_excel_basic(file_path):
    """Excel dosyasini basit bir sekilde oku"""
    # Excel'i text olarak okumaya calis
    try:
        # Dosya uzantisini kontrol et
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            # CSV dosyasi ise
            data = []
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                for row in reader:
                    data.append(row)
            
            if data:
                return {
                    'columns': data[0] if data else [],
                    'row_count': len(data) - 1,
                    'sample_data': data[1:6] if len(data) > 1 else []
                }
        else:
            # Excel dosyasi ise sadece bilgi ver
            return {
                'file_type': 'Excel',
                'file_extension': file_ext,
                'note': 'Excel dosyasi okunamadi - pandas kurulu degil'
            }
    except Exception as e:
        return {'error': str(e)}

def process_excel(params_file):
    """Excel dosyasini isle ve ozet cikar"""
    
    # Parametreleri oku
    with open(params_file, 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    input_file = params.get('input_file')
    operation = params.get('operation', 'summary')
    
    try:
        # Dosya bilgilerini al
        file_stats = {
            'file_name': os.path.basename(input_file),
            'file_size': os.path.getsize(input_file),
            'file_extension': os.path.splitext(input_file)[1],
            'modified_time': datetime.fromtimestamp(os.path.getmtime(input_file)).isoformat(),
            'operation': operation
        }
        
        # Dosya icerigini okumaya calis
        content_info = read_excel_basic(input_file)
        
        result = {
            'status': 'success',
            'file_info': file_stats,
            'content_info': content_info,
            'message': 'Dosya basariyla islendi'
        }
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

if __name__ == '__main__':
    if len(sys.argv) != 2:
        output = {
            'status': 'error',
            'message': 'Parametre dosyasi belirtilmedi'
        }
        print(json.dumps(output))
        sys.exit(1)
    
    params_file = sys.argv[1]
    result = process_excel(params_file)
    
    # ASCII karakterler kullan
    print(json.dumps(result, ensure_ascii=True))