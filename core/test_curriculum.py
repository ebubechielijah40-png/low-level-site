import json
import re
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from core.content_checks import documented_experiments, verify_experiment
from core.hardware_sim import effects
from core.models import CodeDraft, HardwareChallenge, Language, Lesson, LessonCompletion
from core.templatetags.learning import prose


class DocumentationProgramTests(SimpleTestCase):
    pass


def program_test(item):
    def test(self):
        verify_experiment(item)
    return test


for _item in documented_experiments():
    _name = 'test_' + _item['file'].replace('-', '_').replace('.md', '') + '_' + _item['engine'] + '_' + _item['id'].replace('-', '_')
    setattr(DocumentationProgramTests, _name, program_test(_item))


class ProseInteractionTests(SimpleTestCase):
    def test_runnable_program_retains_literal_source(self):
        from html import unescape
        source = 'int main(void){printf("<b> & ");return 0;}'
        html = str(prose('```c run:example\n' + source + '\n```'))
        self.assertIn('data-load-example', html)
        self.assertEqual(unescape(re.search(r'<pre><code>(.*?)</code></pre>', html, re.S)[1]), source)
        self.assertNotIn('<b>', html)

    def test_partial_code_has_no_load_control(self):
        self.assertNotIn('data-load-example', str(prose('```c\nvalue += 1;\n```')))

    def test_internal_links_and_primary_source_links_work(self):
        html = str(prose('[Registers](/learn/device/1/) [Manual](https://docs.kernel.org/driver-api/device-io.html)'))
        self.assertIn('href="/learn/device/1/"', html)
        self.assertIn('href="https://docs.kernel.org/', html)

    def test_unsafe_markdown_links_cannot_become_script_links(self):
        html = str(prose('[Bad](javascript:alert) [Bad](//example.invalid/) `**literal**`'))
        self.assertNotIn('href=', html)
        self.assertIn('<code>**literal**</code>', html)


class CurriculumUpgradeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_lessons', verbosity=0)
        call_command('seed_hardware', verbosity=0)
        cls.user = User.objects.create_user('depth_learner')

    def setUp(self):
        cache.clear()
        self.client.force_login(self.user)

    def create_historical_teaching(self):
        language = Language.objects.create(name='Machine Language', engine='c')
        lesson = Lesson.objects.create(language=language, order=1, title='Old x86 decoding', content='stale', challenge='stale', starter_code='; x86 bytes')
        extra = Lesson.objects.create(language=Language.objects.get(slug='c'), order=99, title='Old arrays', content='stale', challenge='stale')
        LessonCompletion.objects.create(user=self.user, lesson=lesson)
        CodeDraft.objects.create(user=self.user, key=f'lesson:{lesson.pk}', code='historical private work')
        call_command('seed_lessons', verbosity=0)
        language.refresh_from_db()
        lesson.refresh_from_db()
        extra.refresh_from_db()
        return language, lesson, extra

    def test_upgrade_archives_stale_rows_and_preserves_private_work(self):
        language, lesson, extra = self.create_historical_teaching()
        self.assertTrue(language.is_archived)
        self.assertTrue(lesson.is_archived)
        self.assertTrue(extra.is_archived)
        self.assertTrue(LessonCompletion.objects.filter(user=self.user, lesson=lesson).exists())
        self.assertEqual(CodeDraft.objects.get(user=self.user, key=f'lesson:{lesson.pk}').code, 'historical private work')
        self.assertEqual(self.client.get('/dashboard/').context['done_count'], 0)
        self.assertEqual(self.client.get('/dashboard/').context['total_count'], 41)
        self.assertNotContains(self.client.get('/languages/'), 'Machine Language')
        self.assertNotContains(self.client.get('/languages/'), 'Old x86')

    def test_stale_lesson_and_track_do_not_open_wrong_terminal(self):
        language, lesson, extra = self.create_historical_teaching()
        for url in (f'/languages/{language.pk}/', f'/lessons/{lesson.pk}/', f'/lessons/{extra.pk}/'):
            self.assertRedirects(self.client.get(url), '/languages/')

    def test_archived_source_is_not_an_executable_lesson_context(self):
        _, lesson, _ = self.create_historical_teaching()
        response = self.client.post('/api/execute/', json.dumps({'language':'c','code':'int main(void){return 0;}','context_kind':'lesson','context_id':lesson.pk}), content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.client.post(f'/lessons/{lesson.pk}/complete/').status_code, 404)

    def test_canonical_slug_survives_display_name_changes(self):
        language = Language.objects.get(slug='machine')
        original_id = language.pk
        language.name = 'Temporary display name'
        language.save()
        call_command('seed_lessons', verbosity=0)
        self.assertEqual(Language.objects.get(slug='machine',is_archived=False).pk, original_id)
        self.assertEqual(Language.objects.filter(is_archived=False).count(), 7)

    def test_prerequisite_links_resolve_to_seeded_workspaces(self):
        texts = list(Lesson.objects.filter(is_archived=False).values_list('content',flat=True))
        texts += list(HardwareChallenge.objects.values_list('instructions',flat=True))
        paths = {path for text in texts for path in re.findall(r'\]\((/[^\s)]+)\)', text)}
        self.assertGreater(len(paths), 20)
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path,follow=True).status_code, 200)

    def test_foundations_are_open_and_use_the_c_terminal(self):
        lesson = Lesson.objects.get(language__slug='device',order=1)
        response = self.client.get(f'/lessons/{lesson.pk}/')
        self.assertContains(response, 'data-engine="c"')
        self.assertContains(response, 'data-load-example')
        self.assertFalse(LessonCompletion.objects.filter(user=self.user).exists())

    def test_ram_activation_is_independent_of_parity(self):
        lab = HardwareChallenge.objects.get(system__slug='pc',component='ram')
        self.assertFalse(effects(lab,{'mmio':{'61444':0,'61448':1}})['enabled'])
        self.assertTrue(effects(lab,{'mmio':{'61444':1,'61448':0}})['enabled'])

    def test_quantum_shots_are_not_an_enable_flag(self):
        lab = HardwareChallenge.objects.get(system__slug='quantum',order=1)
        model = effects(lab, {'mmio':{'61440':1,'61444':2,'61448':1024}})
        self.assertNotIn('enabled', model)
        self.assertTrue(model['configuration_valid'])
        self.assertEqual(model['probabilities'], {'00':.5,'01':.5,'10':0.0,'11':0.0})

    def test_invalid_quantum_profile_has_no_misleading_probability_table(self):
        lab = HardwareChallenge.objects.get(system__slug='quantum',order=1)
        for mask,qubits,shots in ((4,2,1024),(1,3,1024),(1,2,0)):
            model = effects(lab, {'mmio':{'61440':mask,'61444':qubits,'61448':shots}})
            self.assertFalse(model['configuration_valid'])
            self.assertNotIn('probabilities',model)

    def test_quantum_gate_masks_have_independently_predicted_states(self):
        lab = HardwareChallenge.objects.get(system__slug='quantum',order=2)
        expected = {
            0:{'00':1.0,'01':0.0,'10':0.0,'11':0.0},
            1:{'00':.5,'01':.5,'10':0.0,'11':0.0},
            2:{'00':1.0,'01':0.0,'10':0.0,'11':0.0},
            3:{'00':.5,'01':0.0,'10':0.0,'11':.5},
        }
        for mask,probabilities in expected.items():
            for shots in (1024,2048):
                model = effects(lab,{'mmio':{'61440':mask,'61444':2,'61448':shots}})
                self.assertEqual(model['probabilities'],probabilities)
