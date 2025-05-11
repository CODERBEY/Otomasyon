import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, date
import base64
from io import BytesIO

def main(params_file):
    with open(params_file, 'r', encoding='utf-8') as f:
        params = json.load(f)
    
    # Parametreleri al
    old_file = params.get('old_file')  # Onceki hafta
    new_file = params.get('new_file')  # Bu hafta
    output_type = params.get('output_type', 'both')  # report, chart, both
    
    try:
        # Excel dosyalarini oku
        df_old = pd.read_excel(old_file)
        df_new = pd.read_excel(new_file)
        
        # Analiz yap
        analysis_result = analyze_user_changes(df_old, df_new)
        
        # Grafik olustur
        chart_data = None
        if output_type in ['chart', 'both']:
            chart_data = create_chart(analysis_result)
        
        # Sonuclari hazirla
        result = {
            'status': 'success',
            'analysis': analysis_result,
            'message': 'Kullanici analizi tamamlandi'
        }
        
        if chart_data:
            result['chart'] = chart_data
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def analyze_user_changes(df_old, df_new):
    """Iki Excel arasindaki kullanici degisikliklerini analiz et"""
    
    # Kullanici ID veya email'e gore karsilastirma (varsayim: 'user_id' sutunu var)
    old_users = set(df_old['user_id'].tolist())
    new_users = set(df_new['user_id'].tolist())
    
    # Yeni eklenen kullanicilar
    added_users = new_users - old_users
    
    # Silinen kullanicilar
    deleted_users = old_users - new_users
    
    # Devam eden kullanicilar
    continuing_users = old_users & new_users
    
    # Detayli bilgiler
    added_details = df_new[df_new['user_id'].isin(added_users)]
    deleted_details = df_old[df_old['user_id'].isin(deleted_users)]
    
    # Gunluk analiz (eger kayit tarihi varsa)
    daily_stats = None
    if 'registration_date' in df_new.columns:
        # Gunluk yeni kayitlari hesapla
        df_new['registration_date'] = pd.to_datetime(df_new['registration_date'])
        daily_registrations = df_new.groupby(df_new['registration_date'].dt.date).size()
        # Datetime objelerini string'e cevir
        daily_stats = {str(k): v for k, v in daily_registrations.to_dict().items()}
    
    # DataFrame'leri dictionary'e cevirirken tarih alanlarini string'e cevir
    added_dict = added_details.to_dict('records')
    deleted_dict = deleted_details.to_dict('records')
    
    # Tarih alanlarini string'e cevir
    for record in added_dict:
        for key, value in record.items():
            if isinstance(value, (datetime, date)):
                record[key] = value.isoformat()
            elif pd.isna(value):
                record[key] = None
    
    for record in deleted_dict:
        for key, value in record.items():
            if isinstance(value, (datetime, date)):
                record[key] = value.isoformat()
            elif pd.isna(value):
                record[key] = None
    
    return {
        'total_old_users': len(old_users),
        'total_new_users': len(new_users),
        'added_count': len(added_users),
        'deleted_count': len(deleted_users),
        'continuing_count': len(continuing_users),
        'growth_rate': round((len(new_users) - len(old_users)) / len(old_users) * 100, 2) if old_users else 0,
        'added_users': added_dict[:10],  # Ilk 10 kullanici
        'deleted_users': deleted_dict[:10],  # Ilk 10 kullanici
        'daily_stats': daily_stats
    }

def create_chart(analysis_result):
    """Kullanici degisim grafigi olustur"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 1. Genel Ozet Grafigi
    categories = ['Onceki Hafta', 'Bu Hafta']
    values = [analysis_result['total_old_users'], analysis_result['total_new_users']]
    
    ax1.bar(categories, values, color=['#3498db', '#2ecc71'])
    ax1.set_title('Toplam Kullanici Sayisi Karsilastirmasi')
    ax1.set_ylabel('Kullanici Sayisi')
    
    # Degerleri bar uzerine yaz
    for i, v in enumerate(values):
        ax1.text(i, v + 0.1, str(v), ha='center', va='bottom')
    
    # 2. Degisim Grafigi
    change_categories = ['Yeni Kayitlar', 'Silinen Hesaplar', 'Devam Eden']
    change_values = [
        analysis_result['added_count'],
        analysis_result['deleted_count'],
        analysis_result['continuing_count']
    ]
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']
    
    bars = ax2.bar(change_categories, change_values, color=colors)
    ax2.set_title('Kullanici Degisim Detaylari')
    ax2.set_ylabel('Kullanici Sayisi')
    
    # Degerleri bar uzerine yaz
    for bar, value in zip(bars, change_values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{value}',
                ha='center', va='bottom')
    
    # Buyume oranini goster
    growth_text = f'Buyume Orani: %{analysis_result["growth_rate"]}'
    fig.text(0.5, 0.02, growth_text, ha='center', fontsize=12, weight='bold')
    
    plt.tight_layout()
    
    # Grafigi base64 formatina cevir
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()
    
    return {
        'image_base64': image_base64,
        'filename': f'user_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    }

if __name__ == '__main__':
    if len(sys.argv) != 2:
        output = {
            'status': 'error',
            'message': 'Parametre dosyasi belirtilmedi'
        }
        print(json.dumps(output, ensure_ascii=True))
        sys.exit(1)
    
    params_file = sys.argv[1]
    result = main(params_file)
    
    # ASCII karakterler kullan
    print(json.dumps(result, ensure_ascii=True))