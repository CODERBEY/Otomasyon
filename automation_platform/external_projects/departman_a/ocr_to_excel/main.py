import sys
import json
import os
import pandas as pd
import pytesseract
from PIL import Image
import PyPDF2
import pdf2image
import re
from datetime import datetime

def main(params_file):
    with open(params_file, 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    input_file = params.get('input_file')
    document_type = params.get('document_type', 'auto')  # invoice, receipt, table, auto
    language = params.get('language', 'tur+eng')  # Türkçe + İngilizce
    output_format = params.get('output_format', 'excel')  # excel, csv, json
    
    try:
        # Dosya tipini belirle
        file_extension = os.path.splitext(input_file)[1].lower()
        
        # OCR işlemi
        if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            text = process_image(input_file, language)
        elif file_extension == '.pdf':
            text = process_pdf(input_file, language)
        else:
            return {
                'status': 'error',
                'message': f'Desteklenmeyen dosya tipi: {file_extension}'
            }
        
        # Metni yapılandırılmış veriye dönüştür
        if document_type == 'invoice':
            structured_data = parse_invoice(text)
        elif document_type == 'receipt':
            structured_data = parse_receipt(text)
        elif document_type == 'table':
            structured_data = parse_table(text)
        else:
            structured_data = parse_general(text)
        
        # Excel'e dönüştür
        excel_file = create_excel(structured_data, output_format)
        
        return {
            'status': 'success',
            'extracted_text': text[:1000] + '...' if len(text) > 1000 else text,
            'structured_data': structured_data,
            'output_file': excel_file,
            'message': 'OCR işlemi başarıyla tamamlandı'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def process_image(image_path, language):
    """Resim dosyasını OCR ile oku"""
    try:
        # Tesseract'ın yolunu belirt (Windows için)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Resmi aç ve ön işleme yap
        image = Image.open(image_path)
        
        # Resmi gri tonlamaya çevir
        image = image.convert('L')
        
        # OCR işlemi
        text = pytesseract.image_to_string(image, lang=language)
        
        return text
    except Exception as e:
        raise Exception(f"Resim işleme hatası: {str(e)}")

def process_pdf(pdf_path, language):
    """PDF dosyasını OCR ile oku"""
    try:
        text = ""
        
        # PDF'i resimlere çevir
        images = pdf2image.convert_from_path(pdf_path)
        
        # Her sayfayı OCR ile oku
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image, lang=language)
            text += f"\n--- Sayfa {i+1} ---\n{page_text}\n"
        
        return text
    except Exception as e:
        raise Exception(f"PDF işleme hatası: {str(e)}")

def parse_invoice(text):
    """Fatura formatındaki metni parse et"""
    data = {
        'invoice_info': {},
        'items': [],
        'totals': {}
    }
    
    # Fatura numarası, tarih vb. bilgileri çıkar
    invoice_patterns = {
        'invoice_no': r'Fatura No[:\s]*([A-Z0-9]+)',
        'date': r'Tarih[:\s]*(\d{2}[./]\d{2}[./]\d{4})',
        'customer': r'Müşteri[:\s]*([^\n]+)',
        'total': r'Toplam[:\s]*([0-9.,]+)'
    }
    
    for key, pattern in invoice_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['invoice_info'][key] = match.group(1).strip()
    
    # Satır öğelerini çıkar (basit örnek)
    lines = text.split('\n')
    for line in lines:
        # Ürün satırlarını tanımla (örnek pattern)
        item_match = re.match(r'(.+?)\s+(\d+)\s+([0-9.,]+)\s+([0-9.,]+)', line)
        if item_match:
            data['items'].append({
                'description': item_match.group(1).strip(),
                'quantity': item_match.group(2),
                'unit_price': item_match.group(3),
                'total': item_match.group(4)
            })
    
    return data

def parse_receipt(text):
    """Fiş formatındaki metni parse et"""
    data = {
        'receipt_info': {},
        'items': [],
        'payment': {}
    }
    
    # Fiş bilgilerini çıkar
    receipt_patterns = {
        'date': r'(\d{2}[./]\d{2}[./]\d{4})',
        'time': r'(\d{2}:\d{2})',
        'receipt_no': r'Fiş No[:\s]*([0-9]+)',
        'total': r'TOPLAM[:\s]*([0-9.,]+)'
    }
    
    for key, pattern in receipt_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data['receipt_info'][key] = match.group(1).strip()
    
    return data

def parse_table(text):
    """Tablo formatındaki metni parse et"""
    lines = text.split('\n')
    table_data = []
    
    for line in lines:
        if line.strip():
            # Sekme veya birden fazla boşlukla ayrılmış kolonları tespit et
            columns = re.split(r'\s{2,}|\t', line.strip())
            if columns:
                table_data.append(columns)
    
    # İlk satırı başlık olarak kabul et
    if table_data:
        headers = table_data[0]
        rows = table_data[1:]
        
        # DataFrame oluştur
        df_data = []
        for row in rows:
            if len(row) == len(headers):
                df_data.append(dict(zip(headers, row)))
        
        return {'table': df_data, 'headers': headers}
    
    return {'table': [], 'headers': []}

def parse_general(text):
    """Genel metin formatını parse et"""
    # Basit satır satır ayrıştırma
    lines = text.split('\n')
    data = {
        'lines': [line.strip() for line in lines if line.strip()],
        'statistics': {
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'total_words': len(text.split()),
            'total_characters': len(text)
        }
    }
    
    return data

def create_excel(data, output_format):
    """Yapılandırılmış veriyi Excel'e dönüştür"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if output_format == 'excel':
        output_file = f'ocr_output_{timestamp}.xlsx'
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Farklı veri tiplerini farklı sayfalara yaz
            if 'invoice_info' in data:
                # Fatura bilgileri
                df_info = pd.DataFrame([data['invoice_info']])
                df_info.to_excel(writer, sheet_name='Fatura_Bilgi', index=False)
                
                # Fatura kalemleri
                if data['items']:
                    df_items = pd.DataFrame(data['items'])
                    df_items.to_excel(writer, sheet_name='Kalemler', index=False)
            
            elif 'table' in data:
                # Tablo verisi
                if data['table']:
                    df = pd.DataFrame(data['table'])
                    df.to_excel(writer, sheet_name='Tablo', index=False)
            
            else:
                # Genel veri
                df = pd.DataFrame(data.get('lines', []), columns=['Satır'])
                df.to_excel(writer, sheet_name='Metin', index=False)
                
                # İstatistikler
                if 'statistics' in data:
                    df_stats = pd.DataFrame([data['statistics']])
                    df_stats.to_excel(writer, sheet_name='İstatistikler', index=False)
    
    elif output_format == 'csv':
        output_file = f'ocr_output_{timestamp}.csv'
        
        # CSV için basit format
        if 'table' in data and data['table']:
            df = pd.DataFrame(data['table'])
        else:
            df = pd.DataFrame(data.get('lines', []), columns=['Satır'])
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    return output_file

if __name__ == '__main__':
    result = main(sys.argv[1])
    print(json.dumps(result, ensure_ascii=True))