"""Verify repeat upgrades and the real legacy index collision, using disposable data."""
import os, shutil, sqlite3, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(env,*args,succeeds=True):
    r=subprocess.run([sys.executable,str(ROOT/'manage.py'),*args],cwd=ROOT,env=env,capture_output=True,text=True,timeout=60)
    if succeeds and r.returncode:raise AssertionError(r.stdout+r.stderr)
    if not succeeds and not r.returncode:raise AssertionError('Unfamiliar partial schema accepted.')
    return r
with tempfile.TemporaryDirectory(prefix='bare-metal-upgrade-') as folder:
    tmp=Path(folder);env=os.environ|{'DJANGO_SETTINGS_MODULE':'language.settings','DJANGO_DEBUG':'1','DJANGO_STATIC_ROOT':str(tmp/'staticfiles')}
    # Test private environment creation without touching the user's actual file.
    config_root=tmp/'config';(config_root/'tools').mkdir(parents=True)
    script=config_root/'tools/configure_tunnel.py';shutil.copy2(ROOT/'tools/configure_tunnel.py',script)
    command=[sys.executable,str(script),'https://vzgspgkx-8000.uks1.devtunnels.ms/']
    config_env=env|{'DJANGO_SECRET_KEY':'stable-qa-secret'}
    first=subprocess.run(command,env=config_env,capture_output=True,text=True)
    assert first.returncode==0,first.stderr
    private=config_root/'.env.deploy';saved=private.read_bytes()
    assert private.stat().st_mode & 0o777==0o600
    assert b"DJANGO_SECRET_KEY='stable-qa-secret'" in saved
    again=subprocess.run(command,env=config_env,capture_output=True,text=True)
    assert again.returncode!=0 and private.read_bytes()==saved
    invalid=subprocess.run([sys.executable,str(script),'https://foo.devtunnels.ms:bad/'],env=config_env,capture_output=True,text=True)
    assert invalid.returncode!=0 and private.read_bytes()==saved
    for scenario in ('fresh','legacy','renamed','partial'):
        db=tmp/(scenario+'.sqlite3');case=env|{'DJANGO_DB_PATH':str(db)}
        if scenario!='fresh':
            run(case,'migrate','core','0005','--noinput')
            with sqlite3.connect(db) as con:
                if scenario=='partial':con.execute('CREATE TABLE core_bootproject (id INTEGER PRIMARY KEY)')
                else:
                    con.execute("INSERT INTO auth_user (id,password,last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined) VALUES (1,'!','2026-10-01',0,'upgrade_learner','','','',0,1,'2026-10-01')")
                    con.execute("INSERT INTO core_language (id,name,description) VALUES (1,'C','Legacy track')")
                    con.execute("INSERT INTO core_lesson (id,language_id,title,content,\"order\",challenge,starter_code,example_output) VALUES (1,1,'Legacy lesson','Existing explanation',1,'Practice','','')")
                    table='core_lessoncompletion' if scenario=='legacy' else 'core_lessoncompletion_legacy'
                    con.execute(f'CREATE TABLE {table} (id INTEGER PRIMARY KEY AUTOINCREMENT,completed_at TEXT NOT NULL,lesson_id BIGINT NOT NULL REFERENCES core_lesson(id),user_id BIGINT NOT NULL REFERENCES auth_user(id))')
                    con.execute(f'CREATE INDEX core_lessoncompletion_lesson_id_b68633ad ON {table} (lesson_id)')
                    con.executemany(f'INSERT INTO {table} (completed_at,lesson_id,user_id) VALUES (?,?,?)',[('2026-09-30T10:00:00Z',1,1),('2026-10-01T10:00:00Z',1,1)])
            if scenario=='partial':
                result=run(case,'prepare_deployment','--backup-dir',str(tmp/scenario),succeeds=False)
                assert 'partial upgrade' in result.stderr
                with sqlite3.connect(db) as con:assert 'engine' not in [r[1] for r in con.execute('PRAGMA table_info(core_language)')]
                continue
        backups=tmp/scenario
        run(case,'prepare_deployment','--backup-dir',str(backups));run(case,'prepare_deployment','--backup-dir',str(backups))
        with sqlite3.connect(db) as con:
            assert con.execute('SELECT COUNT(*) FROM core_lesson').fetchone()[0]==33
            assert con.execute('SELECT COUNT(*) FROM core_hardwarechallenge').fetchone()[0]==13
            assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
            if scenario!='fresh':
                assert con.execute('SELECT completed_at,lesson_id,user_id FROM core_lessoncompletion').fetchone()==('2026-09-30T10:00:00Z',1,1)
                assert con.execute('SELECT COUNT(*) FROM core_lessoncompletion').fetchone()[0]==1
                assert con.execute('SELECT COUNT(*) FROM core_lessoncompletion_legacy').fetchone()[0]==2
                assert con.execute('SELECT COUNT(*) FROM auth_user').fetchone()[0]==1
        snapshots=list(backups.glob('*.sqlite3'));assert len(snapshots)==(1 if scenario=='fresh' else 2)
        for snapshot in snapshots:
            assert snapshot.stat().st_mode & 0o777==0o600
            with sqlite3.connect(snapshot) as con:assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    print('Deployment upgrade PASS: fresh/repeated installs, legacy/renamed FK-index collision, completion deduplication, retained audit rows, accounts, protected backups, partial-schema rejection, owner-only configuration, stable secret, overwrite refusal and malformed URL rejection.')
