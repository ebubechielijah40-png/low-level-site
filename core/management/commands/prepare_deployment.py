"""Back up SQLite, reconcile the known completion/index collision and prepare a release."""
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.db.migrations.recorder import MigrationRecorder

MIGRATION='0006_alter_language_options_hardwarechallenge_component_and_more'
LEGACY='core_lessoncompletion_legacy'
COMPLETION_COLUMNS={'id','completed_at','lesson_id','user_id'}

def columns(table):
    with connection.cursor() as cursor:
        cursor.execute('SELECT name FROM pragma_table_info(%s)',[table])
        return {row[0] for row in cursor.fetchall()}

class Command(BaseCommand):
    help='Back up SQLite, migrate, restore known legacy completions, seed teaching and collect static files. Stop the server first.'
    requires_system_checks=[]  # Check after creating the configured DB directory.
    def add_arguments(self,parser):
        parser.add_argument('--backup-dir',type=Path,help='Default: backups beside the configured database.')
    def handle(self,*args,**options):
        if connection.vendor!='sqlite':raise CommandError('This upgrade command supports this project’s SQLite database only.')
        name=str(settings.DATABASES['default']['NAME'])
        if name==':memory:' or name.startswith('file:'):raise CommandError('Use file-backed SQLite for deployment backups.')
        path=Path(name).resolve();path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and path.stat().st_size:
            folder=options['backup_dir'] or path.parent/'backups';folder.mkdir(parents=True,exist_ok=True)
            stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            backup=folder/f'pre-deploy-{stamp}-{uuid.uuid4().hex[:8]}.sqlite3'
            backup.touch(mode=0o600,exist_ok=False)
            # A coherent SQLite snapshot includes WAL data, unlike a plain copy.
            with sqlite3.connect(str(path)) as source,sqlite3.connect(str(backup)) as target:source.backup(target)
            self.stdout.write(f'Database backup: {backup}')
        tables=set(connection.introspection.table_names())
        applied=MigrationRecorder(connection).applied_migrations() if 'django_migrations' in tables else {}
        if ('core',MIGRATION) not in applied and 'core_language' in tables:
            if 'engine' in columns('core_language') or tables & {'core_bootproject','core_codedraft'}:
                raise CommandError('Unrecorded partial upgrade detected. Keep the backup and inspect the schema before migration.')
            if ('core_hardwarechallenge' in tables and 'starter_code_asm' not in columns('core_hardwarechallenge')) or 'core_userprogress' not in tables:
                raise CommandError('Different legacy migration branch detected. Restore its matching migration history before this upgrade.')
            if 'example_output' in columns('core_lesson') and ('core','0005_lesson_example_output') not in applied:
                raise CommandError('The example_output column has no matching migration record. Reconcile the old branch before proceeding.')
            if 'core_lessoncompletion' in tables and LEGACY in tables:raise CommandError('Two completion tables exist before migration 0006. Inspect the backup first.')
            old='core_lessoncompletion' if 'core_lessoncompletion' in tables else LEGACY if LEGACY in tables else None
            if old:
                if columns(old)!=COMPLETION_COLUMNS:raise CommandError('Unfamiliar legacy completion schema; no table changed.')
                with transaction.atomic(),connection.cursor() as cursor:
                    if old!=LEGACY:cursor.execute(f'ALTER TABLE core_lessoncompletion RENAME TO {LEGACY}')
                    # Renaming keeps SQLite index names. Free named FK indexes
                    # before Django creates the replacement table/indexes.
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name=%s AND sql IS NOT NULL",[LEGACY])
                    indexes=[row[0] for row in cursor.fetchall()]
                    for index in indexes:cursor.execute('DROP INDEX '+connection.ops.quote_name(index))
                self.stdout.write('Preserved legacy rows; freed conflicting named indexes.')
        call_command('migrate',interactive=False,stdout=self.stdout)
        if LEGACY in connection.introspection.table_names():
            if columns(LEGACY)!=COMPLETION_COLUMNS:raise CommandError('Unfamiliar retained legacy schema; not imported.')
            with transaction.atomic(),connection.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) FROM core_lessoncompletion');before=cursor.fetchone()[0]
                cursor.execute(f'''INSERT OR IGNORE INTO core_lessoncompletion (completed_at,lesson_id,user_id)
                    SELECT old.completed_at,old.lesson_id,old.user_id FROM {LEGACY} old
                    INNER JOIN core_lesson lesson ON lesson.id=old.lesson_id
                    INNER JOIN auth_user account ON account.id=old.user_id ORDER BY old.id''')
                cursor.execute('SELECT COUNT(*) FROM core_lessoncompletion');restored=cursor.fetchone()[0]-before
            self.stdout.write(f'Restored {restored} valid completions. Legacy rows remain for review.')
        for command in ('seed_lessons','seed_hardware'):call_command(command,stdout=self.stdout)
        call_command('collectstatic',interactive=False,verbosity=0,stdout=self.stdout)
        call_command('check',stdout=self.stdout)
        self.stdout.write(self.style.SUCCESS('Release prepared. Start/restart the application server to activate it.'))
