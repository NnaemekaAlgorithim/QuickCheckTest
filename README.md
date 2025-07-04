# QuickCheckTest

## Table of Content
- [Setting Up The virtual Environment](#setting-up-the-virtual-environment)
- [Setting Up .env File](#setting-up-env-file)
- [Running Server Locally](#running-server-locally)

---

## Setting Up The virtual Environment

First, clone the git repository, navigate to the project root directory and create a virtual environment:
```bash
python3 -m venv venv
```
Creating a virtual environment is different for different operating systems. You can follow this YouTube video for instructions on Linux, Windows, or macOS: [Video](https://youtu.be/kz4gbWNO1cw)

Activate the virtual environment:
* On Linux/macOS:

```bash
source venv/bin/activate
```

* On Windows:

```bash
venv\Scripts\activate
```

### Step 2: Install Dependencies
Navigate to the project directory and run the following command:

```bash
pip install -r requirements.txt
```

---

## Setting Up .env File
You need to create a file named .env at the root of the folder, then copy the contents of .env.sample into it. After that, set the variable values according to your setup for running the server.

Since this is about running django locally on your machine, set DEBUG=True in your .env file that you created and also set the other variables accordingly as shown in the .env.sample file.

## Running Server Locally
Navigate to the project root directory and run the command

```bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runserver
```

If in your .env file you have set BASE_PREFIX=dev then you can open your browser and visit http://127.0.0.1:8000/dev/ to view the redoc documentation of the server.
