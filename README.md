# software-inventory-api

1. Create a virtual environment and activate it

```
python3 -m venv venv
source venv/bin/activate
```

2. Install the requirements

```
pip install -r requirements.txt
```

3. Create .env file
```
touch .env
```
4. Add environment vairables (Get the key from [NVD_Key](https://nvd.nist.gov/developers/request-an-api-key) or Contact for the key)
```
API_KEY=...
```

5. Run the application

```
uvicorn main:app --reload
```

