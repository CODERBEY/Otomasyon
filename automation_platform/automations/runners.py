import subprocess
import sys
import json
import tempfile
import shutil
import os
from pathlib import Path
from django.conf import settings

class ProjectRunner:
    def __init__(self, automation, parameters, user_files=None):
        self.automation = automation
        self.parameters = parameters
        self.user_files = user_files or {}
        self.project_path = automation.project_path
        
    def run(self):
        """Projeyi çalıştır"""
        try:
            # Geçici çalışma dizini oluştur
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Kullanıcı dosyalarını kopyala
                for field_name, uploaded_file in self.user_files.items():
                    file_path = temp_path / uploaded_file.name
                    with open(file_path, 'wb') as f:
                        for chunk in uploaded_file.chunks():
                            f.write(chunk)
                    # Parametrelere dosya yolunu ekle
                    self.parameters[field_name] = str(file_path)
                
                # Parametreleri dosyaya yaz
                params_file = temp_path / 'params.json'
                with open(params_file, 'w', encoding='utf-8') as f:
                    json.dump(self.parameters, f, ensure_ascii=False)
                
                # Python path'e external_projects ve sistem site-packages'ı ekle
                env = os.environ.copy()
                python_paths = [
                    str(settings.EXTERNAL_PROJECTS_DIR),
                    r"C:\Users\Administrator\AppData\Local\Programs\Python\Python313\Lib\site-packages",
                    r"C:\Users\Administrator\AppData\Roaming\Python\Python313\site-packages",
                    r"C:\Python313\Lib\site-packages",
                    r"C:\Program Files\Python313\Lib\site-packages"
                ]
                
                # Var olan yolları ekle
                existing_paths = [path for path in python_paths if os.path.exists(path)]
                env['PYTHONPATH'] = ';'.join(existing_paths)
                
                # Sistem Python'unu kullan
                python_exe = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe"
                
                # Alternatif Python yolları
                if not os.path.exists(python_exe):
                    alternative_pythons = [
                        r"C:\Python313\python.exe",
                        r"C:\Program Files\Python313\python.exe",
                        r"C:\Program Files (x86)\Python313\python.exe",
                        sys.executable  # Fallback olarak mevcut Python
                    ]
                    
                    for alt_python in alternative_pythons:
                        if os.path.exists(alt_python):
                            python_exe = alt_python
                            break
                
                # Projeyi çalıştır
                entry_point = self.automation.entry_point  # Örn: "main"
                module_parts = self.project_path.split('.')
                full_module_path = '.'.join(module_parts + [entry_point])
                
                # Komutu oluştur
                command = [
                    python_exe,  # Sistem Python'unu kullan
                    '-m',
                    full_module_path,
                    str(params_file)
                ]
                
                # Debug için komut ve environment'ı yazdır
                print(f"Python yolu: {python_exe}", file=sys.stderr)
                print(f"PYTHONPATH: {env.get('PYTHONPATH', 'Yok')}", file=sys.stderr)
                print(f"Komut: {' '.join(command)}", file=sys.stderr)
                
                # Subprocess ile çalıştır
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    cwd=str(settings.EXTERNAL_PROJECTS_DIR),
                    env=env,
                    timeout=300  # 5 dakika timeout
                )
                
                # Sonucu parse et
                if result.returncode == 0:
                    try:
                        output = json.loads(result.stdout)
                        return {
                            'status': 'success',
                            'output': output,
                            'stdout': result.stdout,
                            'stderr': result.stderr
                        }
                    except json.JSONDecodeError:
                        return {
                            'status': 'success',
                            'output': result.stdout,
                            'stdout': result.stdout,
                            'stderr': result.stderr
                        }
                else:
                    return {
                        'status': 'error',
                        'error': result.stderr or result.stdout,
                        'stdout': result.stdout,
                        'stderr': result.stderr,
                        'return_code': result.returncode
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'error': 'İşlem zaman aşımına uğradı (5 dakika)',
                'timeout': True
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'exception_type': type(e).__name__
            }
    
    def _install_dependencies(self):
        """Proje bağımlılıklarını yükle"""
        # Proje klasörünü bul
        project_parts = self.project_path.split('.')
        project_dir = settings.EXTERNAL_PROJECTS_DIR
        
        for part in project_parts:
            project_dir = project_dir / part
        
        # requirements.txt dosyasını kontrol et
        requirements_file = project_dir / 'requirements.txt'
        
        if requirements_file.exists():
            # Sistem Python'unu kullan
            python_exe = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe"
            
            if not os.path.exists(python_exe):
                python_exe = sys.executable
            
            # Bağımlılıkları yükle
            try:
                subprocess.run([
                    python_exe,
                    '-m',
                    'pip',
                    'install',
                    '-r',
                    str(requirements_file)
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Bağımlılık yükleme hatası: {e}", file=sys.stderr)

class SafeProjectRunner(ProjectRunner):
    """Güvenlik önlemleri eklenmiş proje çalıştırıcı"""
    
    def __init__(self, automation, parameters, user_files=None):
        super().__init__(automation, parameters, user_files)
        self.timeout = 300  # 5 dakika
        self.memory_limit = 512 * 1024 * 1024  # 512 MB
        
    def run(self):
        """Projeyi güvenli bir şekilde çalıştır"""
        # Temel güvenlik kontrolleri
        if not self._validate_project_path():
            return {
                'status': 'error',
                'error': 'Geçersiz proje yolu'
            }
        
        # Dosya boyutu kontrolü
        for field_name, uploaded_file in self.user_files.items():
            if uploaded_file.size > 10 * 1024 * 1024:  # 10 MB limit
                return {
                    'status': 'error',
                    'error': f'{uploaded_file.name} dosyası çok büyük (max 10MB)'
                }
        
        # Normal çalıştırma
        return super().run()
    
    def _validate_project_path(self):
        """Proje yolunun güvenli olduğunu kontrol et"""
        # Path traversal kontrolü
        if '..' in self.project_path or '/' in self.project_path or '\\' in self.project_path:
            return False
        
        # İzin verilen klasörler
        allowed_prefixes = [
            'departman_a',
            'departman_b',
            'ortak_projeler'
        ]
        
        return any(self.project_path.startswith(prefix) for prefix in allowed_prefixes)