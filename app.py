import logging
import os
import sys
import time
import yaml

from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

log_dir = ''
config_file_path = 'config.yaml'

if os.getenv('APP_LOG_DIR'):
  log_dir = os.environ['APP_LOG_DIR']
  os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s',
  handlers=[
    logging.FileHandler(os.path.join(log_dir, 'azure-spot-starter.log')),
    logging.StreamHandler()
  ]
)
logging.getLogger('azure').setLevel(logging.ERROR)

if not os.path.exists(config_file_path):
  logging.error(f'config file does not exist: {os.path.abspath(config_file_path)}')
  exit(1)

with open(os.path.join(config_file_path)) as config_file:
  config = yaml.safe_load(config_file)

az_tenant_id = config['az_tenant_id']
az_client_id = config['az_client_id']
az_client_secret = config['az_client_secret']

az_subscription_id = config['az_subscription_id']

az_credential = ClientSecretCredential(az_tenant_id, az_client_id, az_client_secret)
az_compute_client = ComputeManagementClient(az_credential, az_subscription_id)

interval_secs = config['interval_secs']

vms = config['vms']
for vm in vms:
  vm['str'] = f"{vm['az_resource_group']}/{vm['az_vm']}"
# Map azure power states to simplified power state
power_state_map = {
  'stopped': {'deallocated', 'deallocating', 'stopped', 'unknown', 'stopping'},
  'running': {'running'},
  'starting': {'starting'}
}


def vm_power_state(vm):
  instance_view = az_compute_client.virtual_machines.instance_view(vm['az_resource_group'], vm['az_vm'])
  for status in instance_view.statuses:
    if status.code.startswith('PowerState/'):
      #logging.info(f'Power state: {status.code}')
      az_state = status.code[len('PowerState/'):]
      for key in power_state_map.keys():
        if az_state in power_state_map[key]:
          return key
      logging.error(f'{az_state} not in power_state_map')
      return 'unknown'
  logging.error(f"No power state in statuses {instance_view}")
  return 'unknown'


def check_vm(vm):  
  if vm_power_state(vm) == 'stopped':
    logging.info(f"{vm['str']} is not running. Starting now.")
    result = az_compute_client.virtual_machines.begin_start(vm['az_resource_group'], vm['az_vm']).wait()
    logging.info(f"Started {vm['str']}")
    

def main():
  logging.info("Starting...")
  logging.info(f"interval_secs={interval_secs}")
  vm_str = ", ".join(map(lambda v: v['str'], vms))
  logging.info(f"{len(vms)} VMs: {vm_str}")

  while True:
    for vm in vms:
      try:
        check_vm(vm)
      except Exception as e:
        logging.error(e)
    time.sleep(interval_secs)

if __name__ == '__main__':
  main()
