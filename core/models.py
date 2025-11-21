from django.db import models # type: ignore

from django.contrib.auth.models import User # Reutilizando o sistema de usuário do Django (Melhor Prática!) # type: ignore



# -----------------------------------------------------------

# Módulo de Usuários e Entidades Base

# -----------------------------------------------------------



class Professor(models.Model):

    """

    Extensão do usuário padrão do Django.

    Usamos o OneToOneField para vincular um usuário do Django

    a um perfil de Professor, garantindo login/senha robustos.

    """

    user = models.OneToOneField(User, on_delete=models.CASCADE) # Vincula ao usuário do Django

    nome_completo = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nome completo do professor para exibir nos boletins"
    )
    data_contratacao = models.DateField(null=True, blank=True)



    def __str__(self):

        # Prioriza: nome_completo > user.get_full_name() > username
        if self.nome_completo:
            return self.nome_completo
        return self.user.get_full_name() or self.user.username
    
    class Meta: 

        verbose_name_plural = "Professores"
        # Ordena pelo nome de usuário do User vinculado
        ordering = ['user__username']


class Competencia(models.Model):

    """Representa a competencia avaliada."""

    TIPO_NOTA_CHOICES = [

        ('NUM', 'Numérica (0-100)'),

        ('ABC', 'Conceitual (A, B, C, D)')

        #Para adicionar mais

    ]

    nome = models.CharField(max_length=100)

    tipo_nota = models.CharField(

        max_length=3,

        choices=TIPO_NOTA_CHOICES,

        default='NUM'

    )

    def __str__(self):

        return f"{self.nome} ({self.get_tipo_nota_display()})" # Exibe o nome e o tipo de nota #type:ignore

    class Meta:

        verbose_name_plural = "Competências"

        ordering = ['nome'] # Ordena por nome da competência



class TipoTurma(models.Model):
    """Representa um tipo de turma (Basic 1, Basic 2, HR4, etc.)"""
    nome = models.CharField(max_length=100, unique=True, help_text="Ex: Basic 1, Basic 2, High Resolution 4")
    descricao = models.TextField(blank=True, help_text="Descrição do tipo de turma")
    competencias = models.ManyToManyField(
        Competencia,
        related_name="tipos_turma",
        verbose_name="Competências do Tipo de Turma",
        blank=True,  # Torna opcional - competências virão do boletim_tipo
        help_text="(Opcional) Competências customizadas. Se vazio, usará as competências do tipo de boletim."
    )
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name_plural = "Tipos de Turma"
        ordering = ['nome']


class Turma(models.Model): # Representa uma turma

    tipo_turma = models.ForeignKey(
        TipoTurma,
        on_delete=models.CASCADE,
        related_name='turmas',
        verbose_name="Tipo de Turma",
        null=True,
        blank=True
    )

    BOLETIM_TIPOS = [
        ("adolescentes_adultos", "Adolescentes - adultos"),
        ("material_antigo", "Material antigo"),
        ("lion_stars", "Lion stars"),
        ("junior", "Junior"),
    ]
    
    # Mapeamento de tipos de boletim para competências necessárias
    COMPETENCIAS_POR_BOLETIM = {
        'adolescentes_adultos': [
            'Produção Oral',
            'Produção Escrita',
            'Avaliações de Progresso',
        ],
        'material_antigo': [
            'Produção Oral',
            'Produção Escrita',
            'Compreensão Oral',
            'Compreensão Escrita',
            'Writing Bit 01',
            'Writing Bit 02',
            'Checkpoints',
        ],
        'lion_stars': [
            'Comunicação Oral',
            'Compreensão Oral',
            'Interesse pela Aprendizagem',
            'Colaboração',
            'Engajamento',
        ],
        'junior': [
            'Comunicação Oral',
            'Compreensão Oral',
            'Comunicação Escrita',
            'Compreensão de Leitura',
            'Interesse pela Aprendizagem',
            'Colaboração',
            'Engajamento',
        ],
    }

    boletim_tipo = models.CharField(
        max_length=32,
        choices=BOLETIM_TIPOS,
        default="junior",
        verbose_name="Tipo de Boletim",
        help_text="Escolha o modelo de boletim para esta turma."
    )

    identificador_turma = models.CharField(
        max_length=100, 
        help_text="Ex: TT18 (Tuesday/Thursday 18h), MW20 (Monday/Wednesday 20h)"
    ) # Identificador único da turma

    professor_responsavel = models.ForeignKey(  # Relaciona a turma a um professor

        Professor,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name='turmas')

    # Removido: competencias ManyToManyField - agora vem do TipoTurma
    
    @property
    def nome(self):
        """Retorna o nome completo da turma baseado no tipo e identificador"""
        if self.tipo_turma:
            return f"{self.tipo_turma.nome} - {self.identificador_turma}"
        return self.identificador_turma
    
    @property
    def competencias(self):
        """Retorna as competências baseadas no tipo de boletim da turma"""
        # Busca os nomes das competências necessárias para este tipo de boletim
        nomes_competencias = self.COMPETENCIAS_POR_BOLETIM.get(self.boletim_tipo, [])
        
        # Busca os objetos Competencia do banco de dados
        from django.db.models import Q
        if nomes_competencias:
            query = Q()
            for nome in nomes_competencias:
                query |= Q(nome=nome)
            return Competencia.objects.filter(query)
        
        return Competencia.objects.none()

    def __str__(self):

        return self.nome # Exibe o nome da turma
    
    
    class Meta: # Define o nome plural correto no admin

        verbose_name_plural = "Turmas"

        ordering = ['tipo_turma__nome', 'identificador_turma'] # Ordena por tipo de turma e depois identificador

        unique_together = ('tipo_turma', 'identificador_turma') # Garante que o identificador seja único dentro do tipo



       

class Aluno(models.Model):

    """Representa um aluno."""

    nome_completo = models.CharField(max_length=200, db_index=True)

    turma = models.ForeignKey ( # Relaciona o aluno a uma turma

        Turma,

        on_delete=models.CASCADE,

        related_name='alunos')



    matricula = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True) # Número de matrícula único
    
    # Campos adicionais para melhor controle
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True, help_text="Indica se o aluno está ativo no sistema")
    observacoes = models.TextField(blank=True, help_text="Observações sobre o aluno")



    def __str__(self):

        return f"{self.nome_completo} - {self.turma.nome}" # Exibe o nome completo do aluno e a turma
    
    def get_progresso_completo(self):
        """Retorna o progresso completo do aluno em suas competências"""
        if not self.turma.competencias:
            return 0
        
        competencias_turma = self.turma.competencias.all()
        total_competencias = len(competencias_turma)
        
        if total_competencias == 0:
            return 0
        
        notas_lancadas = LancamentoDeNota.objects.filter(
            aluno=self,
            competencia__in=competencias_turma
        ).count()
        
        return int((notas_lancadas / total_competencias) * 100)
    
    def get_media_geral(self):
        """Calcula a média geral do aluno em competências numéricas"""
        notas_numericas = LancamentoDeNota.objects.filter(
            aluno=self,
            competencia__tipo_nota='NUM'
        )
        
        if not notas_numericas.exists():
            return None
        
        total = 0
        count = 0
        
        for nota in notas_numericas:
            try:
                valor = float(nota.nota_valor)
                total += valor
                count += 1
            except ValueError:
                continue
        
        return round(total / count, 1) if count > 0 else None

    def tem_notas_completas(self):
        """Verifica se o aluno tem todas as notas lançadas para as competências de sua turma"""
        if not self.turma.competencias:
            return False
        
        competencias_turma = self.turma.competencias.all()
        total_competencias = competencias_turma.count()
        
        if total_competencias == 0:
            return False
        
        notas_lancadas = LancamentoDeNota.objects.filter(
            aluno=self,
            competencia__in=competencias_turma
        ).count()
        
        return notas_lancadas == total_competencias
    
    def get_notas_boletim(self):
        """Retorna todas as notas do aluno organizadas para o boletim"""
        if not self.turma.competencias:
            return []
        
        competencias_turma = self.turma.competencias.all()
        notas_data = []
        
        for competencia in competencias_turma:
            try:
                nota = LancamentoDeNota.objects.get(
                    aluno=self,
                    competencia=competencia
                )
                notas_data.append({
                    'competencia': competencia,
                    'nota': nota.nota_valor,
                    'data_lancamento': nota.data_lancamento
                })
            except LancamentoDeNota.DoesNotExist:
                notas_data.append({
                    'competencia': competencia,
                    'nota': '-',
                    'data_lancamento': None
                })
        
        return notas_data

   

    class Meta:

        verbose_name_plural = "Alunos"

        ordering = ['nome_completo'] # Ordena por nome completo do aluno

        unique_together = ('nome_completo', 'turma') # Garante que o nome do aluno seja único dentro da turma
        indexes = [
            models.Index(fields=['nome_completo']),
            models.Index(fields=['matricula']),
            models.Index(fields=['turma', 'ativo']),
        ]



class LancamentoDeNota(models.Model):

    """Lançamento de nota para um aluno em uma competência."""

    aluno = models.ForeignKey(

        Aluno,

        on_delete=models.CASCADE,

        related_name='lancamentos_de_nota'

    )

    competencia = models.ForeignKey(

        Competencia,

        on_delete=models.CASCADE,

        related_name='lancamentos_de_nota'

    )

    nota_valor = models.CharField(max_length=10, help_text="Valor da nota (ex: 85 ou A)") # Armazena a nota como string para flexibilidade

    data_lancamento = models.DateField(auto_now_add=True)



    def __str__(self):

        return f"Nota {self.nota_valor} para {self.aluno.nome_completo} em {self.competencia.nome}"

       

    class Meta:

        verbose_name_plural = "Lançamentos de Notas"

        ordering = ['-data_lancamento'] # Ordena por data de lançamento, mais recente primeiro

        unique_together = ('aluno', 'competencia') # Garante que um aluno tenha apenas uma nota por competência


class ConfiguracaoSistema(models.Model):
    """
    Configurações gerais do sistema de notas.
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Configuração")
    valor = models.TextField(verbose_name="Valor")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    def __str__(self):
        return f"{self.nome}: {self.valor}"
    
    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"
        ordering = ['nome']
    
    @classmethod
    def get_data_limite_notas(cls):
        """
        Retorna a data limite para entrega de notas.
        Se não estiver configurada, retorna uma data padrão.
        """
        from datetime import date
        try:
            config = cls.objects.get(nome='data_limite_notas')
            return date.fromisoformat(config.valor)
        except (cls.DoesNotExist, ValueError):
            # Data padrão: 2 de novembro de 2025
            return date(2025, 11, 2)


class ProblemaRelatado(models.Model):
    """
    Modelo para armazenar problemas relatados pelos professores e detectados automaticamente
    """
    TIPO_PROBLEMA_CHOICES = [
        ('ALUNO_DUPLICADO', 'Aluno Duplicado'),
        ('ALUNO_FALTANDO', 'Aluno Faltando na Lista'),
        ('TURMA_ERRADA', 'Aluno na Turma Errada'),
        ('DADOS_INCORRETOS', 'Dados do Aluno Incorretos'),
        ('PROBLEMA_SISTEMA', 'Problema no Sistema'),
        ('TURMA_SEM_PROFESSOR', 'Turma sem Professor'),
        ('PROFESSOR_SEM_TURMA', 'Professor sem Turma'),
        ('OUTRO', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('EM_ANALISE', 'Em Análise'),
        ('RESOLVIDO', 'Resolvido'),
        ('REJEITADO', 'Rejeitado'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    ]
    
    ORIGEM_CHOICES = [
        ('PROFESSOR', 'Relatado por Professor'),
        ('SISTEMA', 'Detectado Automaticamente'),
    ]
    
    # Informações básicas
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, verbose_name="Professor", null=True, blank=True)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma", null=True, blank=True)
    aluno = models.ForeignKey(Aluno, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Aluno (se aplicável)")
    
    # Origem do problema
    origem = models.CharField(max_length=10, choices=ORIGEM_CHOICES, default='PROFESSOR', verbose_name="Origem")
    
    # Detalhes do problema
    tipo_problema = models.CharField(max_length=20, choices=TIPO_PROBLEMA_CHOICES, verbose_name="Tipo do Problema")
    titulo = models.CharField(max_length=200, verbose_name="Título do Problema")
    descricao = models.TextField(verbose_name="Descrição Detalhada")
    
    # Status e prioridade
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='MEDIA', verbose_name="Prioridade")
    
    # Timestamps
    data_relato = models.DateTimeField(auto_now_add=True, verbose_name="Data do Relato")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    data_resolucao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Resolução")
    
    # Resposta do admin
    resposta_admin = models.TextField(blank=True, null=True, verbose_name="Resposta do Administrador")
    resolvido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='problemas_resolvidos', verbose_name="Resolvido por")
    
    def __str__(self):
        tipo_display = dict(self.TIPO_PROBLEMA_CHOICES).get(self.tipo_problema, self.tipo_problema)
        origem_display = dict(self.ORIGEM_CHOICES).get(self.origem, self.origem)
        
        if self.professor:
            professor_nome = self.professor.user.get_full_name() or self.professor.user.username
        else:
            professor_nome = "Sistema"
            
        if self.turma:
            turma_nome = self.turma.nome
        else:
            turma_nome = "Geral"
            
        return f"[{origem_display}] {tipo_display} - {turma_nome} ({professor_nome})"
    
    class Meta:
        verbose_name = "Problema Relatado"
        verbose_name_plural = "Problemas Relatados"
        ordering = ['-data_relato']
        
    def get_prioridade_badge_class(self):
        """Retorna a classe CSS para o badge de prioridade"""
        classes = {
            'BAIXA': 'badge-info',
            'MEDIA': 'badge-warning', 
            'ALTA': 'badge-danger',
            'CRITICA': 'badge-critical'
        }
        return classes.get(self.prioridade, 'badge-secondary')
    
    def get_status_badge_class(self):
        """Retorna a classe CSS para o badge de status"""
        classes = {
            'PENDENTE': 'badge-warning',
            'EM_ANALISE': 'badge-info',
            'RESOLVIDO': 'badge-success',
            'REJEITADO': 'badge-secondary'
        }
        return classes.get(self.status, 'badge-secondary')


class AuditLog(models.Model):
    """
    Modelo para logs de auditoria do sistema
    """
    ACAO_CHOICES = [
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('IMPORT', 'Importação'),
        ('EXPORT', 'Exportação'),
        ('VIEW', 'Visualização'),
        ('ERROR', 'Erro'),
    ]
    
    SEVERIDADE_CHOICES = [
        ('LOW', 'Baixa'),
        ('MEDIUM', 'Média'),
        ('HIGH', 'Alta'),
        ('CRITICAL', 'Crítica'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acao = models.CharField(max_length=10, choices=ACAO_CHOICES)
    severidade = models.CharField(max_length=10, choices=SEVERIDADE_CHOICES, default='LOW')
    modelo_afetado = models.CharField(max_length=100, blank=True)
    objeto_id = models.PositiveIntegerField(blank=True, null=True)
    descricao = models.TextField()
    detalhes_json = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp', 'acao']),
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['severidade', 'timestamp']),
        ]
    
    def __str__(self):
        acao_display = dict(self.ACAO_CHOICES).get(self.acao, self.acao)
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {acao_display} - {self.descricao[:50]}"


class SystemMetrics(models.Model):
    """
    Métricas do sistema para monitoramento
    """
    METRIC_CHOICES = [
        ('USERS_ONLINE', 'Usuários Online'),
        ('TOTAL_LOGINS', 'Total de Logins'),
        ('IMPORT_SUCCESS', 'Importações Bem-sucedidas'),
        ('IMPORT_ERRORS', 'Erros de Importação'),
        ('NOTES_CREATED', 'Notas Criadas'),
        ('SYSTEM_ERRORS', 'Erros do Sistema'),
        ('DATABASE_SIZE', 'Tamanho do Banco'),
        ('RESPONSE_TIME', 'Tempo de Resposta'),
    ]
    
    metric_name = models.CharField(max_length=20, choices=METRIC_CHOICES)
    metric_value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_data = models.JSONField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Métrica do Sistema"
        verbose_name_plural = "Métricas do Sistema"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_name', 'timestamp']),
        ]
    
    def __str__(self):
        metric_display = dict(self.METRIC_CHOICES).get(self.metric_name, self.metric_name)
        return f"{metric_display}: {self.metric_value} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"


class UserPreference(models.Model):
    """
    Preferências de personalização do usuário para o dashboard
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    
    # Opções de tema
    theme_color = models.CharField(
        max_length=50,
        default='purple',
        help_text='Cor do tema (purple, blue, pink, green, orange)'
    )
    
    dashboard_emoji = models.CharField(
        max_length=10,
        default='📚',
        help_text='Emoji para o dashboard'
    )
    
    background_gradient_start = models.CharField(
        max_length=7,
        default='#667eea',
        help_text='Cor inicial do gradiente (formato hex)'
    )
    
    background_gradient_end = models.CharField(
        max_length=7,
        default='#764ba2',
        help_text='Cor final do gradiente (formato hex)'
    )
    
    custom_welcome_message = models.CharField(
        max_length=200,
        blank=True,
        help_text='Mensagem personalizada de boas-vindas'
    )
    
    class Meta:
        verbose_name = "Preferência do Usuário"
        verbose_name_plural = "Preferências dos Usuários"
    
    def __str__(self):
        return f"Preferências de {self.user.username}"