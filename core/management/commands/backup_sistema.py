"""
Sistema de Backup Automático para o Sistema de Notas
Execute via: python manage.py backup_sistema
"""

import os
import shutil
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core import serializers
from core.models import *

class Command(BaseCommand):
    help = 'Cria backup completo do sistema de notas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            choices=['completo', 'dados', 'arquivos'],
            default='completo',
            help='Tipo de backup a ser realizado'
        )
        parser.add_argument(
            '--destino',
            type=str,
            help='Diretório de destino do backup'
        )
        parser.add_argument(
            '--limpar-antigos',
            action='store_true',
            help='Remove backups com mais de 30 dias'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Iniciando backup do sistema...'))
        
        tipo_backup = options['tipo']
        destino = options['destino'] or self.get_backup_dir()
        
        # Criar diretório de backup se não existir
        Path(destino).mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'backup_sistema_{timestamp}'
        backup_path = Path(destino) / backup_name
        
        try:
            if tipo_backup in ['completo', 'dados']:
                self.backup_database(backup_path)
                self.backup_fixtures(backup_path)
            
            if tipo_backup in ['completo', 'arquivos']:
                self.backup_media_files(backup_path)
                self.backup_static_files(backup_path)
            
            # Criar arquivo ZIP final
            zip_path = self.create_zip_backup(backup_path, destino, backup_name)
            
            # Limpeza
            if backup_path.exists():
                shutil.rmtree(backup_path)
            
            if options['limpar_antigos']:
                self.cleanup_old_backups(destino)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Backup criado com sucesso: {zip_path}'
                )
            )
            
            # Estatísticas do backup
            self.show_backup_stats(zip_path)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro durante o backup: {str(e)}')
            )
    
    def get_backup_dir(self):
        """Retorna o diretório padrão de backup"""
        return Path(settings.BASE_DIR) / 'backups'
    
    def backup_database(self, backup_path):
        """Faz backup do banco de dados"""
        self.stdout.write('📊 Fazendo backup do banco de dados...')
        
        backup_path.mkdir(parents=True, exist_ok=True)
        db_backup_dir = backup_path / 'database'
        db_backup_dir.mkdir(exist_ok=True)
        
        # Backup do SQLite
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            source_db = Path(settings.DATABASES['default']['NAME'])
            dest_db = db_backup_dir / 'db.sqlite3'
            
            if source_db.exists():
                # Fazer backup usando SQLite
                with sqlite3.connect(str(source_db)) as source:
                    with sqlite3.connect(str(dest_db)) as dest:
                        source.backup(dest)
                
                self.stdout.write(f'  ✓ SQLite backup criado: {dest_db}')
        
        # Backup das configurações
        settings_backup = db_backup_dir / 'settings_backup.py'
        settings_source = Path(settings.BASE_DIR) / 'SistemaNotas' / 'settings.py'
        
        if settings_source.exists():
            shutil.copy2(settings_source, settings_backup)
            self.stdout.write(f'  ✓ Settings backup criado: {settings_backup}')
    
    def backup_fixtures(self, backup_path):
        """Cria fixtures dos dados principais"""
        self.stdout.write('📋 Criando fixtures dos dados...')
        
        fixtures_dir = backup_path / 'fixtures'
        fixtures_dir.mkdir(exist_ok=True)
        
        models_to_backup = [
            (TipoTurma, 'tipos_turma.json'),
            (Competencia, 'competencias.json'),
            (Professor, 'professores.json'),
            (Turma, 'turmas.json'),
            (Aluno, 'alunos.json'),
            (LancamentoDeNota, 'notas.json'),
            (ConfiguracaoSistema, 'configuracoes.json'),
            (ProblemaRelatado, 'problemas.json'),
        ]
        
        for model, filename in models_to_backup:
            try:
                data = serializers.serialize('json', model.objects.all(), indent=2)
                fixture_path = fixtures_dir / filename
                
                with open(fixture_path, 'w', encoding='utf-8') as f:
                    f.write(data)
                
                count = model.objects.count()
                self.stdout.write(f'  ✓ {filename}: {count} registros')
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Erro no backup de {filename}: {e}')
                )
    
    def backup_media_files(self, backup_path):
        """Faz backup dos arquivos de mídia"""
        self.stdout.write('📁 Fazendo backup dos arquivos de mídia...')
        
        media_source = Path(settings.MEDIA_ROOT) if hasattr(settings, 'MEDIA_ROOT') else None
        
        if media_source and media_source.exists():
            media_backup = backup_path / 'media'
            shutil.copytree(media_source, media_backup, dirs_exist_ok=True)
            
            file_count = sum(1 for _ in media_backup.rglob('*') if _.is_file())
            self.stdout.write(f'  ✓ {file_count} arquivos de mídia copiados')
        else:
            self.stdout.write('  ℹ Nenhum arquivo de mídia encontrado')
    
    def backup_static_files(self, backup_path):
        """Faz backup dos arquivos estáticos customizados"""
        self.stdout.write('🎨 Fazendo backup dos arquivos estáticos...')
        
        static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        
        if static_dirs:
            static_backup = backup_path / 'static'
            
            for static_dir in static_dirs:
                static_source = Path(static_dir)
                
                if static_source.exists():
                    shutil.copytree(
                        static_source, 
                        static_backup / static_source.name, 
                        dirs_exist_ok=True
                    )
            
            file_count = sum(1 for _ in static_backup.rglob('*') if _.is_file())
            self.stdout.write(f'  ✓ {file_count} arquivos estáticos copiados')
        else:
            self.stdout.write('  ℹ Nenhum arquivo estático customizado encontrado')
    
    def create_zip_backup(self, backup_path, destino, backup_name):
        """Cria arquivo ZIP com o backup"""
        self.stdout.write('🗜 Compactando backup...')
        
        zip_path = Path(destino) / f'{backup_name}.zip'
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_path)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    def cleanup_old_backups(self, backup_dir):
        """Remove backups antigos (>30 dias)"""
        self.stdout.write('🧹 Limpando backups antigos...')
        
        cutoff_date = datetime.now() - timedelta(days=30)
        backup_path = Path(backup_dir)
        
        removed_count = 0
        
        for backup_file in backup_path.glob('backup_sistema_*.zip'):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                removed_count += 1
                self.stdout.write(f'  🗑 Removido: {backup_file.name}')
        
        if removed_count == 0:
            self.stdout.write('  ℹ Nenhum backup antigo encontrado')
        else:
            self.stdout.write(f'  ✓ {removed_count} backups antigos removidos')
    
    def show_backup_stats(self, zip_path):
        """Mostra estatísticas do backup criado"""
        zip_file = Path(zip_path)
        file_size = zip_file.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        self.stdout.write('\n📊 Estatísticas do Backup:')
        self.stdout.write(f'  📁 Arquivo: {zip_file.name}')
        self.stdout.write(f'  📏 Tamanho: {size_mb:.2f} MB')
        self.stdout.write(f'  📅 Data: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        
        # Contar registros no banco
        stats = {
            'Tipos de Turma': TipoTurma.objects.count(),
            'Competências': Competencia.objects.count(),
            'Professores': Professor.objects.count(),
            'Turmas': Turma.objects.count(),
            'Alunos': Aluno.objects.count(),
            'Notas': LancamentoDeNota.objects.count(),
        }
        
        self.stdout.write('  📋 Dados incluídos:')
        for model_name, count in stats.items():
            self.stdout.write(f'    • {model_name}: {count}')