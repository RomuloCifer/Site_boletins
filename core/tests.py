"""
Testes Automatizados para o Sistema de Notas
Execute com: python manage.py test
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import io

from core.models import (
    Professor, TipoTurma, Turma, Competencia, 
    Aluno, LancamentoDeNota, ConfiguracaoSistema
)

class ModelTestCase(TestCase):
    """Testes para os modelos do sistema"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Criar usuário e professor
        self.user = User.objects.create_user(
            username='professor_teste',
            password='senha123',
            first_name='Professor',
            last_name='Teste'
        )
        self.professor = Professor.objects.create(user=self.user)
        
        # Criar competências
        self.competencia_num = Competencia.objects.create(
            nome='Speaking',
            tipo_nota='NUM'
        )
        self.competencia_abc = Competencia.objects.create(
            nome='Listening',
            tipo_nota='ABC'
        )
        
        # Criar tipo de turma
        self.tipo_turma = TipoTurma.objects.create(
            nome='Basic 1',
            descricao='Nível básico 1'
        )
        self.tipo_turma.competencias.set([self.competencia_num, self.competencia_abc])
        
        # Criar turma
        self.turma = Turma.objects.create(
            tipo_turma=self.tipo_turma,
            identificador_turma='TT18',
            professor_responsavel=self.professor
        )
        
        # Criar alunos
        self.aluno1 = Aluno.objects.create(
            nome_completo='Ana Silva Santos',
            turma=self.turma,
            matricula='2024001'
        )
        self.aluno2 = Aluno.objects.create(
            nome_completo='João Pedro Costa',
            turma=self.turma,
            matricula='2024002'
        )
    
    def test_criacao_professor(self):
        """Testa criação de professor"""
        self.assertEqual(str(self.professor), 'Professor Teste')
        self.assertTrue(self.professor.user.is_authenticated)
    
    def test_competencia_validation(self):
        """Testa validação de competências"""
        # Competência numérica
        self.assertEqual(self.competencia_num.tipo_nota, 'NUM')
        
        # Competência conceitual
        self.assertEqual(self.competencia_abc.tipo_nota, 'ABC')
    
    def test_turma_properties(self):
        """Testa propriedades da turma"""
        self.assertEqual(self.turma.nome, 'Basic 1 - TT18')
        self.assertEqual(self.turma.competencias.count(), 2)
        self.assertEqual(self.turma.alunos.count(), 2)
    
    def test_progresso_aluno(self):
        """Testa cálculo de progresso do aluno"""
        # Aluno sem notas
        self.assertEqual(self.aluno1.get_progresso_completo(), 0)
        
        # Adicionar uma nota
        LancamentoDeNota.objects.create(
            aluno=self.aluno1,
            competencia=self.competencia_num,
            nota_valor='85'
        )
        
        # Progresso deve ser 50% (1 de 2 competências)
        self.assertEqual(self.aluno1.get_progresso_completo(), 50)
        
        # Adicionar segunda nota
        LancamentoDeNota.objects.create(
            aluno=self.aluno1,
            competencia=self.competencia_abc,
            nota_valor='B'
        )
        
        # Progresso deve ser 100%
        self.assertEqual(self.aluno1.get_progresso_completo(), 100)
    
    def test_media_aluno(self):
        """Testa cálculo de média do aluno"""
        # Criar notas numéricas
        LancamentoDeNota.objects.create(
            aluno=self.aluno1,
            competencia=self.competencia_num,
            nota_valor='85'
        )
        
        # Criar competência numérica adicional
        comp_num_2 = Competencia.objects.create(
            nome='Reading',
            tipo_nota='NUM'
        )
        
        LancamentoDeNota.objects.create(
            aluno=self.aluno1,
            competencia=comp_num_2,
            nota_valor='75'
        )
        
        # Média deve ser 80.0
        self.assertEqual(self.aluno1.get_media_geral(), 80.0)

class ViewTestCase(TestCase):
    """Testes para as views do sistema"""
    
    def setUp(self):
        """Configuração inicial para os testes de views"""
        # Criar usuários para diferentes tipos
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@test.com'
        )
        
        self.professor_user = User.objects.create_user(
            username='professor',
            password='prof123'
        )
        self.professor = Professor.objects.create(user=self.professor_user)
        
        # Criar grupos
        Group.objects.create(name='Professores')
        Group.objects.create(name='Coordenadores')
        Group.objects.create(name='Administradores')
        
        self.client = Client()
        
        # Dados básicos
        self.competencia = Competencia.objects.create(
            nome='Speaking',
            tipo_nota='NUM'
        )
        
        self.tipo_turma = TipoTurma.objects.create(
            nome='Basic 1'
        )
        self.tipo_turma.competencias.set([self.competencia])
        
        self.turma = Turma.objects.create(
            tipo_turma=self.tipo_turma,
            identificador_turma='TT18',
            professor_responsavel=self.professor
        )
        
        self.aluno = Aluno.objects.create(
            nome_completo='Teste Aluno',
            turma=self.turma
        )
    
    def test_login_professor(self):
        """Testa login do professor"""
        response = self.client.post(reverse('teacher_portal:login'), {
            'username': 'professor',
            'password': 'prof123'
        })
        
        # Deve redirecionar para dashboard
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_professor(self):
        """Testa acesso ao dashboard do professor"""
        self.client.login(username='professor', password='prof123')
        
        response = self.client.get(reverse('teacher_portal:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.turma.nome)
    
    def test_lancamento_notas(self):
        """Testa lançamento de notas"""
        self.client.login(username='professor', password='prof123')
        
        # Acessar página de notas
        response = self.client.get(
            reverse('teacher_portal:lancamento_notas', args=[self.turma.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Testar POST de nota
        response = self.client.post(
            reverse('teacher_portal:lancamento_notas_aluno', 
                   args=[self.turma.id, self.aluno.id]),
            {
                f'nota_{self.competencia.id}': '85',
                'acao': 'salvar'
            }
        )
        
        # Verificar se nota foi criada
        self.assertTrue(
            LancamentoDeNota.objects.filter(
                aluno=self.aluno,
                competencia=self.competencia,
                nota_valor='85'
            ).exists()
        )
    
    def test_dashboard_admin_requires_permission(self):
        """Testa que dashboard admin requer permissões"""
        # Usuário comum não deve acessar
        self.client.login(username='professor', password='prof123')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Admin deve acessar
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 200)

class ImportTestCase(TestCase):
    """Testes para importação de alunos"""
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        
        # Criar grupos necessários
        Group.objects.create(name='Administradores')
        
        self.tipo_turma = TipoTurma.objects.create(nome='Basic 1')
        self.turma = Turma.objects.create(
            tipo_turma=self.tipo_turma,
            identificador_turma='TT18'
        )
        
        self.client = Client()
        self.client.login(username='admin', password='admin123')
    
    def test_import_csv_valid(self):
        """Testa importação de CSV válido"""
        # Criar arquivo CSV simulado
        csv_content = "nome_completo,matricula\nJoão Silva,2024001\nMaria Santos,2024002"
        csv_file = SimpleUploadedFile(
            "alunos.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(
            reverse('admin_panel:importar_alunos'),
            {
                'turma_id': self.turma.id,
                'arquivo_alunos': csv_file
            }
        )
        
        # Verificar redirecionamento (sucesso)
        self.assertEqual(response.status_code, 302)
        
        # Verificar se alunos foram criados
        self.assertEqual(Aluno.objects.filter(turma=self.turma).count(), 2)
        self.assertTrue(Aluno.objects.filter(nome_completo='João Silva').exists())
        self.assertTrue(Aluno.objects.filter(nome_completo='Maria Santos').exists())
    
    def test_import_csv_missing_column(self):
        """Testa importação com coluna obrigatória faltando"""
        csv_content = "nome,matricula\nJoão Silva,2024001"  # Coluna errada
        csv_file = SimpleUploadedFile(
            "alunos.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(
            reverse('admin_panel:importar_alunos'),
            {
                'turma_id': self.turma.id,
                'arquivo_alunos': csv_file
            }
        )
        
        # Deve redirecionar com erro
        self.assertEqual(response.status_code, 302)
        
        # Nenhum aluno deve ter sido criado
        self.assertEqual(Aluno.objects.filter(turma=self.turma).count(), 0)

class SecurityTestCase(TestCase):
    """Testes de segurança"""
    
    def setUp(self):
        self.professor_user = User.objects.create_user(
            username='professor',
            password='prof123'
        )
        self.professor = Professor.objects.create(user=self.professor_user)
        
        self.other_user = User.objects.create_user(
            username='other',
            password='other123'
        )
        self.other_professor = Professor.objects.create(user=self.other_user)
        
        # Criar turmas para cada professor
        self.tipo_turma = TipoTurma.objects.create(nome='Basic 1')
        
        self.turma_professor = Turma.objects.create(
            tipo_turma=self.tipo_turma,
            identificador_turma='TT18',
            professor_responsavel=self.professor
        )
        
        self.turma_other = Turma.objects.create(
            tipo_turma=self.tipo_turma,
            identificador_turma='MW20',
            professor_responsavel=self.other_professor
        )
        
        self.client = Client()
    
    def test_professor_access_only_own_turmas(self):
        """Testa que professor só acessa suas próprias turmas"""
        self.client.login(username='professor', password='prof123')
        
        # Deve acessar sua própria turma
        response = self.client.get(
            reverse('teacher_portal:lancamento_notas', args=[self.turma_professor.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Não deve acessar turma de outro professor
        response = self.client.get(
            reverse('teacher_portal:lancamento_notas', args=[self.turma_other.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect por falta de permissão
    
    def test_unauthenticated_access_blocked(self):
        """Testa que usuários não autenticados são bloqueados"""
        # Tentar acessar dashboard sem login
        response = self.client.get(reverse('teacher_portal:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect para login
        
        # Tentar acessar admin sem login
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect

class PerformanceTestCase(TestCase):
    """Testes de performance"""
    
    def setUp(self):
        # Criar dados em massa para testar performance
        self.user = User.objects.create_user(username='prof', password='123')
        self.professor = Professor.objects.create(user=self.user)
        
        self.competencia = Competencia.objects.create(nome='Speaking', tipo_nota='NUM')
        self.tipo_turma = TipoTurma.objects.create(nome='Basic 1')
        self.tipo_turma.competencias.set([self.competencia])
        
        # Criar múltiplas turmas e alunos
        for i in range(5):
            turma = Turma.objects.create(
                tipo_turma=self.tipo_turma,
                identificador_turma=f'T{i}',
                professor_responsavel=self.professor
            )
            
            # 20 alunos por turma
            for j in range(20):
                aluno = Aluno.objects.create(
                    nome_completo=f'Aluno {i}-{j}',
                    turma=turma,
                    matricula=f'202400{i}{j:02d}'
                )
                
                # Adicionar algumas notas
                if j % 2 == 0:  # 50% dos alunos com notas
                    LancamentoDeNota.objects.create(
                        aluno=aluno,
                        competencia=self.competencia,
                        nota_valor=str(70 + j)
                    )
    
    def test_dashboard_performance(self):
        """Testa performance do dashboard com muitos dados"""
        self.client = Client()
        self.client.login(username='prof', password='123')
        
        import time
        start_time = time.time()
        
        response = self.client.get(reverse('teacher_portal:dashboard'))
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Dashboard deve responder em menos de 2 segundos
        self.assertLess(processing_time, 2.0)
        self.assertEqual(response.status_code, 200)

class IntegrationTestCase(TestCase):
    """Testes de integração end-to-end"""
    
    def setUp(self):
        # Configurar cenário completo
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123'
        )
        
        self.professor_user = User.objects.create_user(
            username='professor',
            password='prof123'
        )
        self.professor = Professor.objects.create(user=self.professor_user)
        
        # Configurar grupos
        Group.objects.create(name='Administradores')
        Group.objects.create(name='Professores')
        
        self.client = Client()
    
    def test_complete_workflow(self):
        """Testa workflow completo: criação → importação → lançamento → consulta"""
        
        # 1. Admin cria estrutura básica
        self.client.login(username='admin', password='admin123')
        
        # Criar competência
        competencia = Competencia.objects.create(
            nome='Speaking Test',
            tipo_nota='NUM'
        )
        
        # Criar tipo de turma
        tipo_turma = TipoTurma.objects.create(
            nome='Integration Test'
        )
        tipo_turma.competencias.set([competencia])
        
        # Criar turma
        turma = Turma.objects.create(
            tipo_turma=tipo_turma,
            identificador_turma='INT01',
            professor_responsavel=self.professor
        )
        
        # 2. Importar alunos
        csv_content = "nome_completo\nTeste Integração 1\nTeste Integração 2"
        csv_file = SimpleUploadedFile(
            "test.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )
        
        response = self.client.post(
            reverse('admin_panel:importar_alunos'),
            {
                'turma_id': turma.id,
                'arquivo_alunos': csv_file
            }
        )
        self.assertEqual(response.status_code, 302)
        
        # 3. Professor lança notas
        self.client.login(username='professor', password='prof123')
        
        aluno = Aluno.objects.get(nome_completo='Teste Integração 1')
        
        response = self.client.post(
            reverse('teacher_portal:lancamento_notas_aluno', 
                   args=[turma.id, aluno.id]),
            {
                f'nota_{competencia.id}': '90',
                'acao': 'salvar'
            }
        )
        
        # 4. Verificar se tudo funcionou
        nota = LancamentoDeNota.objects.get(
            aluno=aluno,
            competencia=competencia
        )
        self.assertEqual(nota.nota_valor, '90')
        
        # 5. Verificar dashboard
        response = self.client.get(reverse('teacher_portal:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, turma.nome)