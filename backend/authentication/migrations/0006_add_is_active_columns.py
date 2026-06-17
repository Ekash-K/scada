from django.db import migrations


def add_is_active_columns(apps, schema_editor):
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        # user table
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'user' AND COLUMN_NAME = 'is_active'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE `user` ADD COLUMN `is_active` tinyint(1) NOT NULL DEFAULT 1")
        # device table
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'device' AND COLUMN_NAME = 'is_active'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE `device` ADD COLUMN `is_active` tinyint(1) NOT NULL DEFAULT 1")
        # site table
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'site' AND COLUMN_NAME = 'is_active'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE `site` ADD COLUMN `is_active` tinyint(1) NOT NULL DEFAULT 1")


def remove_is_active_columns(apps, schema_editor):
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'user' AND COLUMN_NAME = 'is_active'")
        if cursor.fetchone()[0] == 1:
            cursor.execute("ALTER TABLE `user` DROP COLUMN `is_active`")
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'device' AND COLUMN_NAME = 'is_active'")
        if cursor.fetchone()[0] == 1:
            cursor.execute("ALTER TABLE `device` DROP COLUMN `is_active`")
        cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'site' AND COLUMN_NAME = 'is_active'")
        if cursor.fetchone()[0] == 1:
            cursor.execute("ALTER TABLE `site` DROP COLUMN `is_active`")


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('authentication', '0005_update_workorder_schema'),
    ]

    operations = [
        migrations.RunPython(add_is_active_columns, reverse_code=remove_is_active_columns),
    ]
