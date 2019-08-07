# Microsoft Planner Connector

## Prerequisites

1. Python3
2. Azure account

## Register a web application with the Azure Active Directory admin center

1. Open a browser and navigate to the [Azure Active Directory admin center](https://aad.portal.azure.com).

2. Select **New registration**. On the **Register an application** page, set the values as follows.

    - Set **Name** to `<Some Nice Name>`.
    - Under **Redirect URI**, set the first drop-down to `Web` and set the value to `http://localhost:8000/login/authorized`.

3. Choose **Register**. On the **Python Graph Tutorial** page, copy the value of the **Application (client) ID** and save it, you will need it in the next step.

4. Select **Certificates & secrets** under **Manage**. Select the **New client secret** button. Enter a value in **Description** and select one of the options for **Expires** and choose **Add**.

5. Copy the client secret value before you leave this page. You will need it in the next step.

    > [!IMPORTANT]
    > This client secret is never shown again, so make sure you copy it now.

## Create and Configure an oauth_settings.yml file. 

`oauth_settings.yml`
```
app_id: <your app/client id>
app_secret: <your app/client secret>
redirect: http://localhost:8000/login/authorized
scopes: openid profile offline_access user.read
authority: https://login.microsoftonline.com/<tenant id>
authorize_endpoint: /oauth2/v2.0/authorize
token_endpoint: /oauth2/v2.0/token
```

## To install the app

1. In your preferred cli run :

    ```Shell
    pip3 install -r requirements.txt
    ```

2. In your CLI, run the following command to initialize the app's database.

    ```Shell
    python3 manage.py migrate
    ```

## To run the app

1. Run the following command in your CLI to start the application.

    ```Shell
    python3 manage.py runserver
    ```

1. Open a browser and browse to `http://localhost:8000/login/`.
