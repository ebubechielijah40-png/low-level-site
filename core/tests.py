"""Behaviour, boundary, integration, and authored-reference tests."""
import json
from pathlib import Path
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, SimpleTestCase, TestCase
from django.contrib.auth.models import User
from core.code_runner import execute
from core.models import Language, Lesson, LessonCompletion, HardwareChallenge, HardwareProgress, BootProject, CodeDraft
from core.runtime.boot_vm import DEFAULT_BOOT, build_boot, BootVM
from core.runtime.riscv import assemble
from core.runtime.common import RunError
from core.templatetags.learning import prose
from core.views import state_checks
from core.hardware_sim import effects
CONTENT=Path(__file__).parent/'content'
CATALOG=json.loads((CONTENT/'catalog.json').read_text())
HARDWARE=json.loads((CONTENT/'hardware.json').read_text())
PASSWORD='Testing#4920_Account'

class RunnerTests(SimpleTestCase):
    def ok(self,code,engine='c',output=None):
        r=execute(code,engine);self.assertEqual(r['errors'],[],r['errors'])
        if output is not None:self.assertEqual(r['output'],output)
        return r
    def fail(self,code,engine='c',contains=None):
        r=execute(code,engine);self.assertTrue(r['errors'])
        if contains:self.assertIn(contains.lower(),' '.join(r['errors']).lower())
    def test_c_multiple_prints_and_arguments(self):self.ok('int main(void){int x=3;x+=2;printf("x=%d %d\\n",x,9);printf("done");return 0;}',output='x=5 9\ndone')
    def test_c_main_implicit_return_is_valid(self):self.ok('int main(void){printf("hi");}',output='hi')
    def test_c_parameters_do_not_leak_caller_names(self):self.fail('int f(void){return secret;} int main(void){int secret=2;return f();}',contains='Unknown variable')
    def test_c_globals_are_visible(self):self.ok('int x=7;int f(void){return x;}int main(void){printf("%d",f());}',output='7')
    def test_c_short_circuit(self):self.ok('int main(void){if(0 && 1/0)printf("bad");if(1 || 1/0)printf("ok");}',output='ok')
    def test_c_pointer_write_and_array_pointer_arithmetic(self):self.ok('int main(void){int a[3]={1,2,3};int *p=&a[0];p++;*p=7;printf("%d",a[1]);}',output='7')
    def test_c_pointer_parameter(self):self.ok('void update(int*p){*p=42;}int main(void){int x=1;update(&x);printf("%d",x);}',output='42')
    def test_c_pointer_after_lifetime_is_rejected(self):self.fail('int *bad(void){int x=5;return &x;}int main(void){int*p=bad();printf("%d",*p);}',contains='lifetime')
    def test_c_structure_fields(self):self.ok('struct S{int x;};int main(void){struct S s;s.x=42;printf("%d",s.x);}',output='42')
    def test_c_while_break_continue(self):self.ok('int main(void){int i=0;int s=0;while(1){i++;if(i==2)continue;if(i>3)break;s+=i;}printf("%d",s);}',output='4')
    def test_c_negative_division_truncates_toward_zero(self):self.ok('int main(void){printf("%d %d",-7/3,-7%3);}',output='-2 -1')
    def test_c_unsigned_wrap(self):self.ok('int main(void){unsigned int n=0xffffffffU;n+=1U;printf("%u",n);}',output='0')
    def test_c_signed_overflow_is_reported(self):self.fail('int main(void){int n=2147483647;n++;}',contains='overflow')
    def test_c_division_by_zero(self):self.fail('int main(void){int n=1/0;}',contains='zero')
    def test_c_bad_shift_count(self):self.fail('int main(void){int n=1<<32;}',contains='Shift count')
    def test_c_array_bounds(self):self.fail('int main(void){int a[2]={1,2};printf("%d",a[2]);}',contains='bounds')
    def test_c_uninitialised_local(self):self.fail('int main(void){int x;printf("%d",x);}',contains='uninitialised')
    def test_c_uninitialised_array(self):self.fail('int main(void){int a[2];printf("%d",a[0]);}',contains='uninitialised')
    def test_c_array_size_limit(self):self.fail('int main(void){int a[20000];}',contains='1024')
    def test_c_loop_limit(self):self.fail('int main(void){while(1){}}',contains='limit')
    def test_c_recursive_call_limit(self):self.fail('int f(void){return f();}int main(void){return f();}',contains='depth')
    def test_c_output_limit(self):self.fail('int main(void){while(1){printf("abcdefghijklmnopqrstuvwxyz0123456789");}}',contains='Output limit')
    def test_c_host_calls_are_not_exposed(self):self.fail('int main(void){system("id");}',contains='unavailable')
    def test_c_unknown_headers_are_rejected(self):self.fail('#include <unistd.h>\nint main(void){}',contains='Header')
    def test_c_raw_host_pointer_is_rejected(self):self.fail('int main(void){int *p=(int*)1234;}',contains='Raw host')
    def test_c_unsupported_printf_format(self):self.fail('int main(void){printf("%d %f",1,2);}',contains='format')
    def test_c_macro_does_not_rewrite_string(self):self.ok('#define N 7\nint main(void){printf("N=%d",N);}',output='N=7')
    def test_c_mmio_readback(self):self.ok('int main(void){mmio_write(0xf000,42);printf("%u",mmio_read(0xf000));}',output='42')
    def test_c_mmio_misalignment(self):self.fail('int main(void){mmio_write(0xf001,1);}',contains='aligned')
    def test_c_no_native_struct_layout_claim(self):self.fail('struct S{int x;};int main(void){struct S s;printf("%d",sizeof(s));}',contains='layout')
    def test_rv_known_addi_encoding(self):self.assertEqual(assemble('addi x5,x0,5')[0],[0x00500293])
    def test_rv_assembly_and_machine_agree(self):
        source='li t0,9\nli t1,4\nsub a0,t0,t1\nli a7,1\necall\nli a7,10\necall';words=assemble(source)[0]
        a=self.ok(source,'assembly','5');b=self.ok('\n'.join(f'{w:08x}' for w in words),'machine','5');self.assertEqual(a['state'],b['state'])
    def test_rv_zero_register_cannot_change(self):self.assertEqual(self.ok('addi zero,zero,7\necall','assembly')['state']['registers']['x0'],0)
    def test_rv_signed_unsigned_comparison(self):
        r=self.ok('li t0,-1\nslt t1,t0,zero\nsltu t2,t0,zero\necall','assembly');self.assertEqual(r['state']['registers']['x6'],1);self.assertEqual(r['state']['registers']['x7'],0)
    def test_rv_arithmetic_shift(self):self.assertEqual(self.ok('li t0,-8\nsrai t1,t0,1\necall','assembly')['state']['registers']['x6'],0xfffffffc)
    def test_rv_load_store_and_little_endian(self):
        r=self.ok('lui t0,2\nli t1,42\nsw t1,0(t0)\nlw a0,0(t0)\necall','assembly');self.assertEqual(r['state']['registers']['x10'],42);self.assertTrue(r['state']['memory'][0]['hex'].startswith('2a 00 00 00'))
    def test_rv_misaligned_word(self):self.fail('li t0,1\nlw a0,0(t0)','assembly','Misaligned')
    def test_rv_immediate_range(self):self.fail('addi t0,zero,2048','assembly','12-bit')
    def test_rv_unknown_register(self):self.fail('mov rax,2','assembly')
    def test_rv_duplicate_label(self):self.fail('a: nop\na: nop','assembly','duplicate')
    def test_rv_infinite_branch(self):self.fail('again: j again','assembly','limit')
    def test_machine_invalid_word(self):self.fail('not a machine word','machine','8 hex')
    def test_machine_invalid_opcode(self):self.fail('ffffffff','machine','Unsupported instruction')
    def test_rust_immutable_binding(self):self.fail('fn main(){let x: i32=1;x=2;}','rust','immutable')
    def test_rust_immutable_borrow(self):self.fail('fn main(){let x: i32=1;let p=&mut x;}','rust','immutable')
    def test_rust_two_mutable_borrows(self):self.fail('fn main(){let mut x:i32=1;let p=&mut x;let q=&mut x;}','rust','Aliasing')
    def test_rust_shared_reference_write(self):self.fail('fn main(){let x:i32=1;let p=&x;*p=2;}','rust','&mut')
    def test_rust_owner_read_during_mutable_borrow(self):self.fail('fn main(){let mut x:i32=1;let p=&mut x;println!("{}",x);}','rust','borrowed')
    def test_rust_owner_write_during_borrow(self):self.fail('fn main(){let mut x:i32=1;let p=&mut x;x=2;}','rust','borrowed')
    def test_rust_borrow_expires_at_block(self):self.ok('fn main(){let mut x:i32=1;{let p=&mut x;*p=2;}x=3;println!("{}",x);}','rust','3\n')
    def test_rust_array_bounds(self):self.fail('fn main(){let a=[1,2];println!("{}",a[2]);}','rust','bounds')
    def test_verilog_half_adder(self):self.assertEqual(self.ok('module a(input x,input y,output s,output c);assign s=x^y;assign c=x&y;endmodule','verilog')['state']['truth_table'][-1],{'x':1,'y':1,'s':0,'c':1})
    def test_verilog_input_budget(self):self.fail('module a(input [3:0] x,input [3:0] y,input z,output q);assign q=z;endmodule','verilog','8 total')
    def test_verilog_sequential_not_faked(self):self.fail('module a(input x,output q);always @(posedge x) q=1;endmodule','verilog','continuous')
    def test_verilog_missing_output(self):self.fail('module a(input x,output q);endmodule','verilog','exactly one')
    def test_boot_image_signature_and_length(self):
        image=build_boot(DEFAULT_BOOT);self.assertEqual(len(image),512);self.assertEqual(image[-2:],b'\x55\xaa');self.assertIn('BARE METAL OS',BootVM(image).run()['screen'])
    def test_boot_invalid_signature(self):
        with self.assertRaises(RunError):BootVM(b'\0'*512)
    def test_boot_program_size(self):self.fail('db "'+'x'*511+'"','boot','510')
    def test_boot_unsupported_interrupt(self):self.fail('mov ah,0x0e\nint 0x13\nhlt','boot','INT 10')
    def test_boot_infinite_loop(self):self.fail('again: jmp again','boot','limit')
    def test_empty_source(self):self.fail('')
    def test_non_string_source(self):self.assertTrue(execute(123)['errors'])
    def test_source_budget(self):self.fail('x'*24001,contains='24 KB')
    def test_unknown_engine(self):self.fail('x','python','Unknown')
    def test_markdown_escapes_script_and_html(self):
        text=str(prose('## Hi\n<script>alert(1)</script>\n```\n<img src=x onerror=alert(1)>\n```'));self.assertNotIn('<script>',text);self.assertNotIn('<img ',text);self.assertIn('&lt;script&gt;',text)

class AuthTests(TestCase):
    def test_register_logs_in_and_hashes_password(self):
        r=self.client.post('/register/',{'username':'learner','email':'a@example.invalid','password':PASSWORD,'confirm_password':PASSWORD});self.assertRedirects(r,'/dashboard/');u=User.objects.get(username='learner');self.assertTrue(u.check_password(PASSWORD));self.assertNotEqual(u.password,PASSWORD)
    def test_common_password_rejected(self):
        self.client.post('/register/',{'username':'learner','email':'a@example.invalid','password':'password','confirm_password':'password'});self.assertEqual(User.objects.count(),0)
    def test_password_mismatch_rejected(self):
        self.client.post('/register/',{'username':'learner','email':'a@example.invalid','password':PASSWORD,'confirm_password':'different'});self.assertEqual(User.objects.count(),0)
    def test_duplicate_username_case_insensitive(self):
        User.objects.create_user('Learner',password=PASSWORD);r=self.client.post('/register/',{'username':'learner','email':'a@example.invalid','password':PASSWORD,'confirm_password':PASSWORD});self.assertEqual(User.objects.count(),1);self.assertContains(r,'already taken')
    def test_password_eyes_both_pages(self):self.assertEqual(self.client.get('/register/').content.count(b'class="password-toggle"'),2);self.assertEqual(self.client.get('/login/').content.count(b'class="password-toggle"'),1)
    def test_bad_login_shows_error(self):self.assertContains(self.client.post('/login/',{'username':'missing','password':PASSWORD}),'correct username and password')
    def test_safe_next_redirect(self):
        User.objects.create_user('learner',password=PASSWORD);r=self.client.post('/login/',{'username':'learner','password':PASSWORD,'next':'/languages/'});self.assertRedirects(r,'/languages/')
    def test_external_next_is_rejected(self):
        User.objects.create_user('learner',password=PASSWORD);r=self.client.post('/login/',{'username':'learner','password':PASSWORD,'next':'https://evil.invalid/'});self.assertRedirects(r,'/dashboard/')
    def test_logout_is_post_only(self):
        u=User.objects.create_user('learner',password=PASSWORD);self.client.force_login(u);self.assertEqual(self.client.get('/logout/').status_code,405);self.assertRedirects(self.client.post('/logout/'),'/')

class WorkspaceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_lessons',verbosity=0);call_command('seed_hardware',verbosity=0)
        cls.user=User.objects.create_user('learner',password=PASSWORD);cls.other=User.objects.create_user('other',password=PASSWORD)
    def setUp(self):cache.clear();self.client.force_login(self.user)
    def post_json(self,path,data):return self.client.post(path,json.dumps(data),content_type='application/json')
    def test_seeds_are_idempotent(self):
        before=(Language.objects.count(),Lesson.objects.count(),HardwareChallenge.objects.count());call_command('seed_lessons',verbosity=0);call_command('seed_hardware',verbosity=0);self.assertEqual(before,(6,33,13));self.assertEqual(before,(Language.objects.count(),Lesson.objects.count(),HardwareChallenge.objects.count()))
    def test_all_pages_render(self):
        paths=['/','/dashboard/','/languages/','/hardware/','/os/']+[f'/playground/?lang={x}' for x in ('c','assembly','machine','rust','verilog','boot')]
        paths += [f'/languages/{l.pk}/' for l in Language.objects.all()]+[f'/lessons/{l.pk}/' for l in Lesson.objects.all()]
        paths += [f'/hardware/{s.slug}/' for s in __import__('core.models',fromlist=['HardwareSystem']).HardwareSystem.objects.all()]
        paths += [f'/hardware/{l.system.slug}/{l.pk}/?lang={engine}' for l in HardwareChallenge.objects.select_related('system') for engine in ('c','assembly')]
        for path in paths:
            with self.subTest(path=path):self.assertEqual(self.client.get(path).status_code,200)
    def test_hardware_no_lesson_lock(self):
        self.assertFalse(LessonCompletion.objects.exists());r=self.client.get('/hardware/');self.assertContains(r,'Every lab is open');self.assertNotContains(r,'LOCKED')
    def test_old_try_route_redirects_to_same_workspace(self):
        l=Lesson.objects.first();self.assertRedirects(self.client.get(f'/lessons/{l.pk}/try/'),f'/lessons/{l.pk}/')
    def test_progress_counts_individual_lessons(self):
        lessons=list(Lesson.objects.filter(language__engine='c')[:2])
        for l in lessons:self.client.post(f'/lessons/{l.pk}/complete/')
        self.client.post(f'/lessons/{lessons[0].pk}/complete/');self.assertEqual(LessonCompletion.objects.filter(user=self.user).count(),2);self.assertEqual(self.client.get('/dashboard/').context['done_count'],2)
    def test_progress_is_private(self):
        l=Lesson.objects.first();LessonCompletion.objects.create(user=self.other,lesson=l);self.assertEqual(self.client.get('/dashboard/').context['done_count'],0)
    def test_api_requires_auth(self):self.client.logout();self.assertEqual(self.post_json('/api/execute/',{'code':'x'}).status_code,401)
    def test_api_requires_post(self):self.assertEqual(self.client.get('/api/execute/').status_code,405)
    def test_api_requires_csrf(self):
        c=Client(enforce_csrf_checks=True);c.force_login(self.user);self.assertEqual(c.post('/api/execute/',json.dumps({'code':'x'}),content_type='application/json').status_code,403)
    def test_api_invalid_json(self):self.assertEqual(self.client.post('/api/execute/','{',content_type='application/json').status_code,400)
    def test_api_invalid_context_id(self):self.assertEqual(self.post_json('/api/execute/',{'code':'x','context_kind':'lesson','context_id':[]}).status_code,400)
    def test_api_invalid_engine_type(self):self.assertEqual(self.post_json('/api/execute/',{'code':'x','language':[]}).status_code,400)
    def test_api_language_matches_lesson(self):
        l=Lesson.objects.filter(language__engine='c').first();self.assertEqual(self.post_json('/api/execute/',{'code':l.starter_code,'language':'assembly','context_kind':'lesson','context_id':l.pk}).status_code,400)
    def test_api_reference_check(self):
        l=Lesson.objects.filter(language__engine='c').first();r=self.post_json('/api/execute/',{'code':l.starter_code,'language':'c','context_kind':'lesson','context_id':l.pk}).json();self.assertTrue(r['passed']);self.assertEqual(r['errors'],[])
    def test_api_rate_limit(self):
        cache.set('run:'+str(self.user.pk),60,60);self.assertEqual(self.post_json('/api/execute/',{'code':'int main(void){}'}).status_code,429)
    def test_lab_cannot_be_marked_without_checks(self):
        l=HardwareChallenge.objects.select_related('system').first();self.client.post(f'/hardware/{l.system.slug}/{l.pk}/complete/');self.assertFalse(HardwareProgress.objects.exists())
    def test_lab_pass_records_completion(self):
        l=HardwareChallenge.objects.get(system__slug='pc',order=1);code=HARDWARE[0]['labs'][0]['reference_c'];r=self.post_json('/api/execute/',{'code':code,'language':'c','context_kind':'lab','context_id':l.pk}).json();self.assertTrue(r['passed']);self.assertTrue(HardwareProgress.objects.get(user=self.user,challenge=l).completed)
    def test_lab_failure_does_not_record_completion(self):
        l=HardwareChallenge.objects.get(system__slug='pc',order=1);r=self.post_json('/api/execute/',{'code':l.starter_code_c,'language':'c','context_kind':'lab','context_id':l.pk}).json();self.assertFalse(r['passed']);self.assertFalse(HardwareProgress.objects.exists())
    def test_drafts_save_and_reload(self):
        l=Lesson.objects.first();self.post_json('/api/draft/',{'key':f'lesson:{l.pk}','code':'a private draft'});self.assertContains(self.client.get(f'/lessons/{l.pk}/'),'a private draft');self.assertEqual(CodeDraft.objects.count(),1)
    def test_drafts_are_private(self):
        l=Lesson.objects.first();CodeDraft.objects.create(user=self.other,key=f'lesson:{l.pk}',code='other secret');self.assertNotContains(self.client.get(f'/lessons/{l.pk}/'),'other secret')
    def test_draft_key_validation(self):self.assertEqual(self.post_json('/api/draft/',{'key':'../../bad','code':'x'}).status_code,400)
    def test_save_download_and_boot(self):
        r=self.post_json('/api/boot/save/',{'name':'My OS','code':DEFAULT_BOOT});self.assertEqual(r.status_code,200);pk=r.json()['id'];download=self.client.get(f'/os/{pk}/download/');self.assertEqual(len(download.content),512);self.assertEqual(download.content[-2:],b'\x55\xaa');boot=self.client.post(f'/os/{pk}/boot/').json();self.assertIn('BARE METAL OS',boot['output'])
    def test_boot_projects_are_private(self):
        p=BootProject.objects.create(user=self.other,name='private',image_hex=build_boot(DEFAULT_BOOT).hex());self.assertEqual(self.client.get(f'/os/{p.pk}/').status_code,404);self.assertEqual(self.client.get(f'/os/{p.pk}/download/').status_code,404);self.assertEqual(self.client.post(f'/os/{p.pk}/boot/').status_code,404);self.assertEqual(self.client.post(f'/os/{p.pk}/delete/').status_code,404)
    def test_boot_save_rejects_invalid_source(self):self.assertEqual(self.post_json('/api/boot/save/',{'name':'bad','code':'mov rax,1'}).status_code,400);self.assertFalse(BootProject.objects.exists())
    def test_boot_upload_valid(self):
        f=SimpleUploadedFile('boot.img',build_boot(DEFAULT_BOOT));r=self.client.post('/os/upload/',{'name':'Import','image':f});self.assertEqual(r.status_code,302);self.assertEqual(BootProject.objects.get().source,'')
    def test_boot_upload_size_and_signature(self):
        for data in (b'x'*513,b'x'*512):
            self.client.post('/os/upload/',{'image':SimpleUploadedFile('bad.img',data)});self.assertFalse(BootProject.objects.exists())
    def test_boot_name_is_escaped(self):
        p=BootProject.objects.create(user=self.user,name='<script>alert(1)</script>',image_hex=build_boot(DEFAULT_BOOT).hex());r=self.client.get(f'/os/{p.pk}/');self.assertNotContains(r,'<script>alert(1)</script>');self.assertContains(r,'&lt;script&gt;')
    def test_all_lessons_have_actual_teaching_and_practice(self):
        for l in Lesson.objects.all():
            with self.subTest(lesson=l.title):self.assertGreater(len(l.content.split()),300);self.assertTrue(l.challenge);self.assertTrue(l.expected_state)
    def test_no_external_runner_or_cdn(self):
        for p in (Path(__file__).parent/'templates').rglob('*.html'):
            s=p.read_text();self.assertNotIn('emkc.org',s);self.assertNotIn('cdnjs',s);self.assertNotIn('target="_blank"',s)
    def test_quantum_probabilities_are_normalised(self):
        l=HardwareChallenge.objects.get(system__slug='quantum',order=2);state=execute(HARDWARE[-1]['labs'][1]['reference_c'],'c')['state'];model=effects(l,state);self.assertEqual(model['probabilities'],{'00':.5,'01':0.0,'10':0.0,'11':.5});self.assertAlmostEqual(sum(model['probabilities'].values()),1.0)

class AuthoredExamples(SimpleTestCase):pass
# Each authored example is a distinct discoverable test, with its independently
# stated reference result. References are not generated from the runner under test.
def lesson_test(engine,l):
    def test(self):
        r=execute(l['starter_code'],engine);self.assertEqual(r['errors'],[],r['errors']);checks=state_checks(r,l['expected_state']);self.assertTrue(checks);self.assertTrue(all(c['passed'] for c in checks),checks)
    return test
for t in CATALOG:
    for i,l in enumerate(t['lessons'],1):setattr(AuthoredExamples,f'test_{t["slug"]}_{i:02}',lesson_test(t['engine'],l))
def lab_test(l,engine):
    def test(self):
        r=execute(l['reference_'+engine],engine);self.assertEqual(r['errors'],[],r['errors']);checks=state_checks(r,l['expected_state']);self.assertTrue(all(c['passed'] for c in checks),checks)
        bad=execute(l['starter_code_c'] if engine=='c' else l['starter_code_asm'],engine);self.assertEqual(bad['errors'],[],bad['errors']);self.assertFalse(all(c['passed'] for c in state_checks(bad,l['expected_state'])))
    return test
for s in HARDWARE:
    for i,l in enumerate(s['labs'],1):
        for engine in ('c','assembly'):setattr(AuthoredExamples,f'test_lab_{s["slug"].replace("-","_")}_{i:02}_{engine}',lab_test(l,engine))
