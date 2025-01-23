# Resilient HTTP Client :
This is a small resilient HTTP Client that retries HTTP requests in case of an error. This client adds new features such as timeout personalization and selection of errors to retry on.
## Tutorial
At first, make sure you have installed Python in your machine.
To run the tests of the HTTP Client.

1. Create a virtual environment :
```bash
python -m venv venv
```
OR
```bash
python3 -m venv venv
```

2. Activate the virtual environment :
- On Linux and MacOS :
```bash
source venv/bin/activate
```
- On Windows :
```shell
.\venv\Scripts\activate
```

3. Install all the requirements :
```bash
pip install -r requirements.txt
```

4. Run the tests :
```bash
pytest -v
```
