# azure-spot-starter
A service which keeps azure spot instances running.

## Setup
- First, copy template_config.yaml to data/config.yaml. All configuration/secrets will go in config.yaml.

```
$ docker pull chickenbellyfin/azure-spot-starter

# OR

$ docker build . -t azure-spot-starter
```

## Run
```
$ docker run -v $(pwd)/data:/data chickenbellyfin/azure-spot-starter
```

### Create Azure Service Principal
  - From Azure Portal, go to Azure Active Directory -> App registrations
  - Click "New registration", enter a name, and click "Register"
  - From the new application
    - Copy the **Application (client) ID** as `az_client_id` in config.yaml
    - Copy the **Directory (tenant) ID** as `az_tenant_id` in config.yaml
  - Go to "Certificates & secrets" and click "New Client Secret"
    - Copy the secret **Value** as `az_client_secret` in config.yaml
  - From Azure Portal, go to "Subscriptions" and copy your **Subscription ID** as `az_subscription_id` in config.yaml

### To add a VM to the bot
You need to grant permission for azure-spot-starter to control each VM you create.

- Go to the VM page in Azure Portal
- Click on "Access control (IAM)"
- Click "Add role assignment", select "Virtual Machine Contributor" and click "Next"
- Under "Assign access to", make sure "User, group, or service principal" is selected
- Click "Select members" and search for the application name you created in the first step. Click on it and then "Select"
- Click "Review + assign"