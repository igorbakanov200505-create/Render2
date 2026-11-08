import importlib.util
import unittest
from pathlib import Path

p=Path(__file__).resolve().parents[1] / 'monitor' / 'telegram_bot.py'
spec=importlib.util.spec_from_file_location('telegram_bot',p)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SAMPLE={'status':'up','checked_at':'2026-11-09T01:00:00Z','http_status':200,'duration_ms':158, 'history': []}

class TestTelegram(unittest.TestCase):
    def test_summary(self):
        self.assertIn('ДОСТУПЕН',mod.summary(SAMPLE))
        self.assertIn('HTTP: 200',mod.summary(SAMPLE))

    def test_alert_after_two_failures(self):
        state={'failure_streak':0,'alert_open':False,'update_offset':0};calls=[]
        send=lambda m: calls.append(m) or True
        down={**SAMPLE,'status':'down','http_status':500,'error':'HTTP 500'}
        mod.evaluate_alert(state,down,send)
        self.assertEqual(calls,[])
        mod.evaluate_alert(state,down,send)
        self.assertEqual(len(calls),1)
        self.assertTrue(state['alert_open'])
        mod.evaluate_alert(state,down,send)
        self.assertEqual(len(calls),1)

    def test_recovery(self):
        state={'failure_streak':5,'alert_open':True,'update_offset':0};sent=[]
        mod.evaluate_alert(state,SAMPLE,lambda m: sent.append(m) or True)
        self.assertEqual(len(sent),1)
        self.assertIn('восстановлен', sent[0])
        self.assertFalse(state['alert_open'])

    def test_failed_send_retries(self):
        state={'failure_streak':1,'alert_open':False,'update_offset':0}
        mod.evaluate_alert(state,{**SAMPLE,'status':'down'},lambda m: False)
        self.assertFalse(state['alert_open'])

    def test_only_authorized_chat_gets_response(self):
        state={'update_offset':0};sent=[]
        updates=[{'update_id':1,'message':{'chat':{'id':42},'text':'/status'}},
                 {'update_id':2,'message':{'chat':{'id':99},'text':'/status'}}]
        def api(token,method,payload):
            if method=='getUpdates':return updates
            sent.append(payload);return {'message_id':5}
        mod.handle_commands('secret','99',state,SAMPLE,call_api=api)
        self.assertEqual(len(sent),1)
        self.assertEqual(sent[0]['chat_id'],'99')
        self.assertEqual(state['update_offset'],3)

    def test_reply_failure_does_not_advance_offset(self):
        updates=[{'update_id':7,'message':{'chat':{'id':99},'text':'/status'}}]
        def api(token,method,payload):return updates if method=='getUpdates' else None
        state={'update_offset':0}
        mod.handle_commands('secret','99',state,SAMPLE,call_api=api)
        self.assertEqual(state.get('update_offset'),0)

if __name__=='__main__':unittest.main()
