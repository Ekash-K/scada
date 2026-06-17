from django.db import migrations


def update_workorder_schema(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        # Ensure task_template_id exists for WorkOrder FK
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'work_order' AND COLUMN_NAME = 'task_template_id'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE work_order ADD COLUMN task_template_id bigint(20) NULL")

        # Ensure parts_used exists
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'work_order' AND COLUMN_NAME = 'parts_used'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE work_order ADD COLUMN parts_used longtext NULL")

        # Change status to varchar(20) so new enum values can be stored
        cursor.execute("SELECT COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'work_order' AND COLUMN_NAME = 'status'")
        row = cursor.fetchone()
        if row:
            column_type = row[0]
            if column_type.startswith('enum('):
                cursor.execute("ALTER TABLE work_order MODIFY COLUMN status varchar(20) NOT NULL DEFAULT 'Draft'")
                cursor.execute(
                    "UPDATE work_order SET status = CASE "
                    "WHEN status = 'pending' THEN 'Pending' "
                    "WHEN status = 'in progress' THEN 'In Progress' "
                    "WHEN status = 'completed' THEN 'Resolved' "
                    "WHEN status = 'overdue' THEN 'Review Required' "
                    "ELSE status END"
                )


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('authentication', '0004_create_tasktemplate_table'),
    ]

    operations = [
        migrations.RunPython(update_workorder_schema),
    ]
