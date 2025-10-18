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

    data_contratacao = models.DateField(null=True, blank=True)



    def __str__(self):

        return self.user.get_full_name() or self.user.username  # Exibe o nome completo ou o nome de usuário
    
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



class Turma(models.Model): # Representa uma turma

    nome = models.CharField(max_length=100)

    identificador_turma = models.CharField(max_length=100, help_text="Ex: A2, 2025/1 Tarde, 2a e 4a") # Identificador único da turma

    professor_responsavel = models.ForeignKey(  # Relaciona a turma a um professor

        Professor,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name='turmas')

    competencias = models.ManyToManyField(

        Competencia,

        related_name="turmas",

        verbose_name="Competências da Turma",

        blank=True # Permite que uma turma seja criada sem nenhuma competência

    )

    def __str__(self):

        return self.nome # Exibe o nome da turma
    
    
    class Meta: # Define o nome plural correto no admin

        verbose_name_plural = "Turmas"

        ordering = ['nome'] # Ordena por nome da turma

        unique_together = ('nome', 'identificador_turma') # Garante que o nome da turma seja único



       

class Aluno(models.Model):

    """Representa um aluno."""

    nome_completo = models.CharField(max_length=200)

    turma = models.ForeignKey ( # Relaciona o aluno a uma turma

        Turma,

        on_delete=models.CASCADE,

        related_name='alunos')



    matricula = models.CharField(max_length=20, unique=True, null=True, blank=True) # Número de matrícula único



    def __str__(self):

        return f"{self.nome_completo} {self.turma.nome}" # Exibe o nome completo do aluno e a turma

   

    class Meta:

        verbose_name_plural = "Alunos"

        ordering = ['nome_completo'] # Ordena por nome completo do aluno

        unique_together = ('nome_completo', 'turma') # Garante que o nome do aluno seja único dentro da turma



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