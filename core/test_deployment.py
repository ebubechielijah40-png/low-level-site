import json
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from core.templatetags.learning import prose, render_prose


class DeploymentResponseTests(TestCase):
    @override_settings(APP_REVISION='reviewable-release')
    def test_html_has_timing_revision_and_private_cache_headers(self):
        response=self.client.get('/login/')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response['X-App-Revision'],'reviewable-release')
        self.assertRegex(response['Server-Timing'],r'^app;dur=\d+\.\d{2}$')
        self.assertIn('private',response['Cache-Control'])
        self.assertIn('no-store',response['Cache-Control'])
    def test_private_execution_is_never_shared_cached(self):
        self.client.force_login(User.objects.create_user('timing_learner'))
        response=self.client.post('/api/execute/',json.dumps({'language':'c','code':'int main(void){printf("42");}','context_kind':'free'}),content_type='application/json')
        self.assertEqual(response.json()['output'],'42')
        self.assertIn('no-store',response['Cache-Control'])
        self.assertIn('app;dur=',response['Server-Timing'])
    def test_error_responses_are_measured_too(self):
        response=self.client.post('/api/execute/','{}',content_type='application/json')
        self.assertEqual(response.status_code,401)
        self.assertIn('app;dur=',response['Server-Timing'])
        self.assertIn('no-store',response['Cache-Control'])
    def test_cached_teaching_stays_escaped_and_updates_with_its_text(self):
        render_prose.cache_clear()
        first=prose('## Example\n<script>alert(1)</script>')
        self.assertNotIn('<script>',first)
        self.assertIn('&lt;script&gt;',first)
        self.assertEqual(prose('## Example\n<script>alert(1)</script>'),first)
        self.assertIn('Changed',prose('## Changed\nAnother explanation.'))
        self.assertNotEqual(prose('## Changed\nAnother explanation.'),first)
