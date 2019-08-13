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

### Config in Sesam :

#### System config :
```

```

#### Pipe config :
```

```