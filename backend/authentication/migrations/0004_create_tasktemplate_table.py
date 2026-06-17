from django.db import migrations


def create_task_template_table(apps, schema_editor):
    TaskTemplate = apps.get_model('authentication', 'TaskTemplate')
    table_name = TaskTemplate._meta.db_table
    existing_tables = schema_editor.connection.introspection.table_names()
    if table_name not in existing_tables:
        schema_editor.create_model(TaskTemplate)


def drop_task_template_table(apps, schema_editor):
    TaskTemplate = apps.get_model('authentication', 'TaskTemplate')
    table_name = TaskTemplate._meta.db_table
    existing_tables = schema_editor.connection.introspection.table_names()
    if table_name in existing_tables:
        schema_editor.delete_model(TaskTemplate)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('authentication', '0003_alter_scadaalert_options_alter_tasktemplate_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_task_template_table, reverse_code=drop_task_template_table),
    ]
