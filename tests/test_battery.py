import sys, tempfile, unittest, json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'addon/battery-monitor'))
from bms_parser import BMSParser
from multi_battery import MultiBatteryManager, VirtualBattery
from addon_config import BatteryConfig
from energy_tracker import EnergyTracker
from mqtt_helper import MultiBatteryMQTTPublisher
import modbus

SAMPLE='22014A00E0C60118FE14BC100CF40CF40CF00CF20CF30CF60D020CF50CF50CFF0CF50CF40CF80CF90CFA0CF000E600C800D20400C800C800C800C800000000006400294A1A6B003F000000000000000000230000000000000000000000000000000000000000000000D3EF'
def checksum(body): return f'{(-sum(body.encode("ascii"))) & 0xffff:04X}'
def modify(start,end,value):
    b=SAMPLE[:-4]; b=b[:start]+value+b[end:]; return b+checksum(b)
def pack(soc,cap): return {'soc_percent':soc,'full_charge_capacity_ah':cap,'pack_voltage_v':54.65,'pack_current_a':0,'cell_voltages_v':[3.4],'energy_in_kwh':1,'energy_out_kwh':2}
def cfg(): return SimpleNamespace(mqtt_host='localhost',mqtt_port=1883,device_id='bms_multi_battery',enable_virtual_battery=True,virtual_battery_name='Battery Bank',manufacturer='Daren',model='Daren BMS Multi',mqtt_username='',mqtt_password='',read_interval=10,get_enabled_batteries=lambda:[BatteryConfig('a',1,'battery_1'),BatteryConfig('b',1,'battery_2')],stale_timeout=60,batteries=[BatteryConfig('a',1,'battery_1'),BatteryConfig('b',1,'battery_2')])
class FakeClient:
    def __init__(self): self.messages=[];self.rc=0
    def publish(self,topic,payload=None,**kw): self.messages.append((topic,payload,kw)); return SimpleNamespace(rc=self.rc)
    def will_set(self,*a,**k): pass
    def reconnect_delay_set(self,**k): pass
class ProtocolTests(unittest.TestCase):
    def test_sample(self):
        d=BMSParser.parse_service_42_response(SAMPLE); self.assertAlmostEqual(d['soc_percent'],63.98);self.assertEqual(d['pack_current_a'],0);self.assertAlmostEqual(d['full_charge_capacity_ah'],105.70)
    def test_corrupt_checksum(self):
        with self.assertRaises(ValueError): BMSParser.parse_service_42_response(SAMPLE[:-4]+'0000')
    def test_length_checksum(self):
        with self.assertRaises(ValueError): BMSParser.parse_service_42_response(modify(8,9,'F'))
    def test_return_code(self):
        with self.assertRaises(ValueError): BMSParser.parse_service_42_response(modify(6,8,'01'))
    def test_wrong_identity(self):
        for start,end,val in [(0,2,'21'),(4,6,'46')]:
            with self.subTest(val=val),self.assertRaises(ValueError):BMSParser.parse_service_42_response(modify(start,end,val))
    def test_signed_current(self):
        # Current follows 6-byte prefix, 16 cells, 3 temperatures, count, 4 sensors: byte 53.
        self.assertEqual(BMSParser.parse_service_42_response(modify(118,122,'FB2E'))['pack_current_a'],-12.34)
    def test_request_address_checksum(self):
        serial=SimpleNamespace(reset_input_buffer=lambda:None,reset_output_buffer=lambda:None,flush=lambda:None,write=lambda b:setattr(self,'sent',b),read_until=lambda **k:b'~'+SAMPLE.encode()+b'\r',timeout=2)
        class Context:
            def __enter__(self):return serial
            def __exit__(self,*a):pass
        with patch('modbus.serial.Serial',return_value=Context()),patch('modbus._wait_for_serial'):
            modbus.request_device_info('dummy',address=2)
        self.assertEqual(self.sent,b'~22024A42E00202FD26\r')
    def test_serial_noise_echo_and_incomplete(self):
        chunks=iter([b'noise\r',b'~22014A42E00201FD28\r',b'~'+SAMPLE.encode()+b'\r'])
        serial=SimpleNamespace(reset_input_buffer=lambda:None,reset_output_buffer=lambda:None,flush=lambda:None,write=lambda b:None,read_until=lambda **k:next(chunks,b''),timeout=2)
        class Context:
            def __enter__(self):return serial
            def __exit__(self,*a):pass
        with patch('modbus.serial.Serial',return_value=Context()),patch('modbus._wait_for_serial'):
            self.assertEqual(modbus.request_device_info('dummy'),b'~'+SAMPLE.encode()+b'\r')
        serial.read_until=lambda **k:b'~2201'
        with patch('modbus.serial.Serial',return_value=Context()),patch('modbus._wait_for_serial'):
            with self.assertRaises(ValueError):modbus.request_device_info('dummy',timeout=.01)
class BankTests(unittest.TestCase):
    def test_capacity_weighting(self):
        v=VirtualBattery();v.add_battery_data('a',pack(20,100));v.add_battery_data('b',pack(80,200));self.assertEqual(v.get_aggregated_data()['soc_percent'],60)
    def test_missing_capacity_does_not_fake_average(self):
        v=VirtualBattery();v.add_battery_data('a',pack(20,0));v.add_battery_data('b',pack(80,200));self.assertFalse(v.get_aggregated_data())
    def test_incomplete_cycle_and_recovery(self):
        with tempfile.TemporaryDirectory() as tmp,patch('multi_battery.get_config',return_value=cfg()),patch('multi_battery.EnergyTracker',return_value=EnergyTracker(tmp+'/energy.json')):
            m=MultiBatteryManager(cfg().batteries)
            with patch.object(m,'_read_single_battery',side_effect=[pack(99.88,100),pack(90.3,100)]),patch('multi_battery.time.monotonic',return_value=100):first=m.get_all_data()
            self.assertAlmostEqual(first['_virtual_battery']['soc_percent'],95.09)
            with patch.object(m,'_read_single_battery',side_effect=[pack(99.88,100),None]),patch('multi_battery.time.monotonic',return_value=110):second=m.get_all_data()
            self.assertNotIn('_virtual_battery',second)
            with patch('multi_battery.time.monotonic',return_value=110):
                self.assertEqual(m.get_diagnostics()['battery_2']['data_age_seconds'],10)
            self.assertEqual(m.get_diagnostics()['battery_2']['error_count'],1)
            with patch.object(m,'_read_single_battery',side_effect=[pack(99.88,100),None]),patch('multi_battery.time.monotonic',return_value=160):m.get_all_data();self.assertFalse(m.get_diagnostics()['battery_2']['available'])
            with patch.object(m,'_read_single_battery',side_effect=[pack(99.88,100),pack(90.3,100)]),patch('multi_battery.time.monotonic',return_value=170):self.assertIn('_virtual_battery',m.get_all_data())
            self.assertEqual(m.get_diagnostics()['battery_2']['consecutive_errors'],0)
    def test_strict_wire_frame_and_address(self):
        with tempfile.TemporaryDirectory() as tmp,patch('multi_battery.get_config',return_value=cfg()),patch('multi_battery.EnergyTracker',return_value=EnergyTracker(tmp+'/e.json')):
            m=MultiBatteryManager(cfg().batteries)
            for raw in [b'~'+SAMPLE.encode(),b'~'+SAMPLE.encode()+b'!\r',b'~'+modify(2,4,'02').encode()+b'\r']:
                with patch('multi_battery.request_device_info',return_value=raw):self.assertIsNone(m._read_single_battery(cfg().batteries[0]))
class MQTTTests(unittest.TestCase):
    def setUp(self):
        self.client=FakeClient()
        with patch('mqtt_helper.get_config',return_value=cfg()),patch('mqtt_helper.mqtt.Client',return_value=self.client):self.pub=MultiBatteryMQTTPublisher()
        self.pub.connected=True
    def test_metadata_and_identity(self):
        self.pub.publish_multi_battery_discovery(['battery_1','battery_2'])
        configs={t:json.loads(p) for t,p,k in self.client.messages if t.startswith('homeassistant/')}
        soc=configs['homeassistant/sensor/bms_multi_battery_battery_1/soc/config']
        self.assertEqual(soc['unique_id'],'bms_multi_battery_battery_1_soc');self.assertEqual((soc['device_class'],soc['unit_of_measurement'],soc['state_class']),('battery','%','measurement'))
        self.assertEqual(soc['availability_mode'],'all');self.assertEqual(soc['expire_after'],60)
        self.assertEqual(soc['availability'][1]['topic'],'bms/bms_multi_battery_battery_1/availability')
        energy=configs['homeassistant/sensor/bms_multi_battery_virtual/energy_in_total/config'];self.assertEqual((energy['device_class'],energy['unit_of_measurement'],energy['state_class']),('energy','kWh','total_increasing'))
        status=configs['homeassistant/sensor/bms_multi_battery_battery_1/status/config'];self.assertNotIn('state_class',status)
    def test_partial_cycle_offline_bank_no_fake_states(self):
        self.pub.publish_all_battery_data({'battery_1':pack(99.88,100)},{'battery_1':{'available':True,'data_age_seconds':0},'battery_2':{'available':False,'data_age_seconds':60},'_virtual_battery':{'available':False}})
        messages={t:p for t,p,k in self.client.messages}
        self.assertEqual(messages['bms/bms_multi_battery_virtual/availability'],'offline');self.assertEqual(messages['bms/bms_multi_battery_battery_2/availability'],'offline')
        self.assertNotIn('bms/bms_multi_battery_virtual/soc',messages);self.assertNotIn('bms/bms_multi_battery_battery_2/soc',messages)
    def test_queue_failure(self):
        self.client.rc=4;self.assertFalse(self.pub.publish_battery_data('battery_1',pack(50,100)))
    def test_disconnect_callback_does_not_block_reconnect(self):
        with patch.object(self.pub,'_attempt_reconnect') as reconnect:self.pub._on_disconnect(self.client,None,1);reconnect.assert_not_called()
class EnergyTests(unittest.TestCase):
    def test_gap_and_restart_no_fabricated_energy(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=tmp+'/e.json';e=EnergyTracker(p);e.update('b',3600,100);self.assertEqual(e.update('b',3600,110),(0.01,0.0));e.mark_gap('b');self.assertEqual(e.update('b',3600,200),(0.01,0.0));r=EnergyTracker(p);self.assertEqual(r.update('b',3600,500),(0.01,0.0))
class ExtraTests(unittest.TestCase):
    def test_discovery_failure_retries_and_reconnect_refresh(self):
        client=FakeClient()
        with patch('mqtt_helper.get_config',return_value=cfg()),patch('mqtt_helper.mqtt.Client',return_value=client):p=MultiBatteryMQTTPublisher()
        p.connected=True;client.rc=4;self.assertFalse(p.publish_all_battery_data({'battery_1':pack(50,100)}));client.rc=0;self.assertTrue(p.publish_all_battery_data({'battery_1':pack(50,100)}))
        client.messages=[];p._on_disconnect(client,None,1);p._on_connect(client,None,None,0);p.publish_all_battery_data({'battery_1':pack(50,100)})
        self.assertTrue(any(t.startswith('homeassistant/') for t,x,k in client.messages))
        self.assertTrue(any(t=='bms/bms_multi_battery_battery_2/availability' and x=='offline' for t,x,k in client.messages))
    def test_missing_values_not_zero(self):
        client=FakeClient()
        with patch('mqtt_helper.get_config',return_value=cfg()),patch('mqtt_helper.mqtt.Client',return_value=client):p=MultiBatteryMQTTPublisher()
        p.connected=True;p.publish_battery_data('battery_1',{'soc_percent':None,'power_w':float('nan'),'pack_current_a':0})
        self.assertEqual([(t,x) for t,x,k in client.messages],[('bms/bms_multi_battery_battery_1/pack_current','0')])
    def test_all_sensor_units_and_classes(self):
        client=FakeClient()
        with patch('mqtt_helper.get_config',return_value=cfg()),patch('mqtt_helper.mqtt.Client',return_value=client):p=MultiBatteryMQTTPublisher()
        p.connected=True;p.publish_multi_battery_discovery(['battery_1','battery_2'])
        conf={t:json.loads(x) for t,x,k in client.messages if t.startswith('homeassistant/')}
        for sid,unit,device in [('pack_voltage','V','voltage'),('pack_current','A','current'),('power','W','power'),('temperature','°C','temperature')]:
            c=conf['homeassistant/sensor/bms_multi_battery_battery_1/'+sid+'/config'];self.assertEqual((c['unit_of_measurement'],c['device_class'],c['state_class']),(unit,device,'measurement'))
            self.assertEqual(c['device']['identifiers'],['bms_multi_battery_battery_1']);self.assertNotIn('battery_1',c['name'])
        for sid in ['remaining_capacity','full_charge_capacity']:
            c=conf['homeassistant/sensor/bms_multi_battery_battery_1/'+sid+'/config'];self.assertEqual((c['unit_of_measurement'],c['state_class']),('Ah','measurement'));self.assertNotIn('device_class',c)
        for sid in ['last_success','data_age','error_count','consecutive_errors']:
            c=conf['homeassistant/sensor/bms_multi_battery_battery_1/'+sid+'/config'];self.assertEqual(c['entity_category'],'diagnostic');self.assertNotIn('state_class',c)
        for t,c in conf.items():self.assertNotEqual(c.get('device_class'),'humidity')
        self.assertNotIn('homeassistant/sensor/bms_multi_battery_virtual/pack_current/config',conf)
    def test_bank_missing_energy_not_reset(self):
        with tempfile.TemporaryDirectory() as tmp,patch('multi_battery.get_config',return_value=cfg()),patch('multi_battery.EnergyTracker',return_value=EnergyTracker(tmp+'/e.json')):
            m=MultiBatteryManager(cfg().batteries);a=pack(50,100);b=pack(50,100);del b['energy_in_kwh']
            with patch.object(m,'_read_single_battery',side_effect=[a,b]):d=m.get_all_data()['_virtual_battery']
            self.assertNotIn('energy_in_kwh',d);self.assertEqual(d['energy_out_kwh'],4)
    def test_empty_bank_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp,patch('multi_battery.get_config',return_value=cfg()),patch('multi_battery.EnergyTracker',return_value=EnergyTracker(tmp+'/e.json')):
            m=MultiBatteryManager([]);self.assertFalse(m.get_all_data());self.assertFalse(m.get_diagnostics()['_virtual_battery']['available'])
    def test_publish_failure_does_not_mark_pack_online(self):
        client=FakeClient()
        with patch('mqtt_helper.get_config',return_value=cfg()),patch('mqtt_helper.mqtt.Client',return_value=client):p=MultiBatteryMQTTPublisher()
        p.connected=True;p._discovery_pending=False;client.rc=4;p.publish_all_battery_data({'battery_1':pack(50,100)},{'battery_1':{'available':True}})
        self.assertFalse(any(t.endswith('/availability') and x=='online' for t,x,k in client.messages))
    def test_monitor_recovers_from_failed_startup_even_without_data(self):
        import main
        c=cfg();c.log_level='CRITICAL';c.multi_battery_mode=True;c.discovery_mode=False;c.mqtt_host='localhost';c.mqtt_port=1883
        with patch('main.get_config',return_value=c),patch('main.MultiBatteryManager') as Manager,patch('main.MultiBatteryMQTTPublisher') as Publisher,patch('main.time.sleep',side_effect=KeyboardInterrupt):
            Manager.return_value.get_all_data.return_value={};Manager.return_value.get_diagnostics.return_value={'battery_1':{'available':False}}
            Publisher.return_value.connect.return_value=False
            main.main()
            Publisher.return_value.publish_all_battery_data.assert_called_once_with({}, {'battery_1':{'available':False}})

class ValidationTests(unittest.TestCase):
    def test_reserved_bank_identity_rejected(self):
        with tempfile.TemporaryDirectory() as tmp,patch('multi_battery.get_config',return_value=cfg()),patch('multi_battery.EnergyTracker',return_value=EnergyTracker(tmp+'/e.json')):
            for name in ['_virtual_battery','virtual','Virtual']:
                with self.subTest(name=name),self.assertRaises(ValueError):MultiBatteryManager([BatteryConfig('a',1,name),BatteryConfig('b',1,'battery_2')])
    def test_optional_mqtt_does_not_block_bootstrap(self):
        import subprocess
        run_script = Path(modbus.__file__).resolve().parent / 'run.sh'
        if not run_script.exists():
            run_script = Path('/run.sh')
        with tempfile.TemporaryDirectory() as tmp:
            binpath=Path(tmp)/'bin';binpath.mkdir();stub=binpath/'python3';stub.write_text('#!/bin/sh\necho BOOTED\n');stub.chmod(0o755)
            script='''
function bashio::log.info() { :; }
function bashio::services.available() { return 1; }
function bashio::services.wait() { exit 77; }
export -f bashio::log.info bashio::services.available bashio::services.wait
export PATH="''' + str(binpath) + ''':$PATH"
source "''' + str(run_script) + '''"
'''
            import os
            # Run script expects /app; use controlled replacement only for cwd in this
            # standalone script boundary test, retaining all bootstrap decisions.
            script=script.replace('source "'+str(run_script)+'"', 'eval "$(sed \'s|cd /app|cd '+tmp+'|g\' '+str(run_script)+')"')
            r=subprocess.run(['bash','-c',script],capture_output=True,text=True,timeout=3)
            self.assertEqual(r.returncode,0,r.stderr);self.assertIn('BOOTED',r.stdout)

if __name__=='__main__':unittest.main()
