# Generated migration for user preferences

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0013_add_nome_completo_to_professor'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('theme_color', models.CharField(default='purple', max_length=50, help_text='Cor do tema (purple, blue, pink, green, orange)')),
                ('dashboard_emoji', models.CharField(default='📚', max_length=10, help_text='Emoji para o dashboard')),
                ('background_gradient_start', models.CharField(default='#667eea', max_length=7, help_text='Cor inicial do gradiente')),
                ('background_gradient_end', models.CharField(default='#764ba2', max_length=7, help_text='Cor final do gradiente')),
                ('custom_welcome_message', models.CharField(blank=True, max_length=200, help_text='Mensagem personalizada de boas-vindas')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferences', to='auth.user')),
            ],
            options={
                'verbose_name': 'Preferência do Usuário',
                'verbose_name_plural': 'Preferências dos Usuários',
            },
        ),
    ]
