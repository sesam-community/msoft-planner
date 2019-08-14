# Microsoft Planner Connector

## Prerequisites

1. Python3
2. Azure account

### Running the script in development requires environment variables

Set the following env variables in 'service.py' :

os.environ['client_id'] = '<Azure client ID>'
os.environ['client_secret'] = '<Azure client Secret>'
os.environ['tenant_id'] = '<Azure tenant ID>'
os.environ['username'] = '<Azure Username>'
os.environ['password'] = '<Azure password>'
os.environ['redirect_url'] = 'http://localhost:5000/auth'
os.environ['access_token'] = '<Access token>'

### Register a web application with the Azure Active Directory admin center

1. Open a browser and navigate to the [Azure Active Directory admin center](https://aad.portal.azure.com).

2. Select **New registration**. On the **Register an application** page, set the values as follows.

    - Set **Name** to `<Some Nice Name>`.
    - Under **Redirect URI**, set the first drop-down to `Web` and set the value to `http://localhost:5000/auth`.

3. Choose **Register**. On the **Name** page, copy the value of the **Application (client) ID** and save it, you will need it later.

4. Select **Certificates & secrets** under **Manage**. Select the **New client secret** button. Enter a value in **Description** and select one of the options for **Expires** and choose **Add**.

5. Enter the values provided as environment variables when working on this repo in development.

### Running the app in development.

Go into package.json and follow the instructions to run the app.

## After having hosted the service on docker.

1. Make a temporary system in Sesam as shown below :
    ```
    {
    "_id": "msplanner-connector",
    "type": "system:microservice",
    "docker": {
        "environment": {
        "client_id": "$SECRET(azure-client-id)",
        "client_secret": "$SECRET(azure-client-secret)",
        "password": "$SECRET(azure-password)",
        "redirect_url": "$ENV(azure-redirect-url)",
        "tenant_id": "$SECRET(azure-tenant-id)",
        "username": "$ENV(azure-username)"
        },
        "image": "jc89als/msplanner-connector:latest",
        "port": 5000
    },
    "verify_ssl": true
    }
    ```

2. Connect to the system via the /proxy/ route to generate access token :

    1. Go into the System permissions tab and under 'local Permissions' add the following :

    ![alt text][Permissions.png "Permissions"]

    2. Go to the following url to aquire and **save** access token as instructed in the browser
    
    url example :
    https://<Node ID>.sesam.cloud/api/systems/<System _id>/proxy/auth


### After having aquired and saved access token:

#### System config :
```
{
  "_id": "msplanner-connector",
  "type": "system:microservice",
  "docker": {
    "environment": {
      "access_token": "$SECRET(msgraph-access-token)",
      "client_id": "$SECRET(azure-client-id)",
      "client_secret": "$SECRET(azure-client-secret)",
      "password": "$SECRET(azure-password)",
      "redirect_url": "$ENV(azure-redirect-url)",
      "tenant_id": "$SECRET(azure-tenant-id)",
      "username": "$ENV(azure-username)"
    },
    "image": "jc89als/msplanner-connector:latest",
    "port": 5000
  },
  "verify_ssl": true
}
```
**Obs.** in the Secrets tab in your System, remember to set the defined $SECRET's for connecting to the docker image.

#### Pipe config :

**Obs.** in the Datahub tab under Settings, remember to set the defined $ENV's in the system config needed for connecting to the docker image.
```
{
  "_id": "msplanner-connector-ms",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "msplanner-connector",
    "url": "/planner/<dynamic value i.e. 'tasks'>"
  },
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["copy", "*"]
      ]
    }
  }
}
```

Supported dynamic values for the url property :
1. tasks
2. plans
3. users
4. groups