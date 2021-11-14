from flask import Flask
from flask_caching import Cache
import json
import redis
from flasgger import Swagger
from config import config
import threading
import schedule

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
swagger = Swagger(app)

redisDB = redis.StrictRedis(
    host='redis-10226.c135.eu-central-1-1.ec2.cloud.redislabs.com',
    port=10226,
    db=0,
    password="kKcvEj3O75RFMPHkiXR8DrN81kHA92af",
    charset="utf-8",
    decode_responses=True)
redisConst = "bcd8b0c2eb1fce714eab6cef0d771acc"


@app.route("/primes/<n>", methods=['POST'])
@cache.cached(query_string=True)
def getAllNPrimitives(n):
    """Vraća listu prostih brojeva do 'n' (cache)
    ---
    parameters:
      - name: n
        in: path
        type: string
        required: true
    responses:
      200:
        description: Lista prostih brojeva do broja 'n'
    """
    if (int(n) == 0 or int(n) == 1):
        return json.dumps([])

    n = int(n) + 1
    arr = []
    is_prime = [1] * int(n)

    i = 2
    while i * i <= int(n):
        if is_prime[i] == 0:
            i += 1
            continue
        j = 2 * i
        while j < int(n):
            is_prime[j] = 0
            j += i
        i += 1

    for number in range(2, int(n)):
        if is_prime[number] == 1:
            arr.append(number)
    return json.dumps(arr)


@app.route("/dynamicPrimes/<n>", methods=['POST'])
#@cache.cached(query_string=True)
def getDynamicPrimes(n):
    """Vraća listu prostih brojeva do 'n' (dinamicno)
    ---
    parameters:
      - name: n
        in: path
        type: string
        required: true
    responses:
      200:
        description: Lista prostih brojeva do broja 'n'
    """
    if (int(n) == 0 or int(n) == 1):
        return json.dumps([])

    if (int(n) == 2):
        return json.dumps([2])
    elif (int(n) == 3):
        return json.dumps([2, 3])

    min = int(n)
    start = 2
    dynamic = False
    for key in redisDB.keys():
        keyArr = key.split('/')
        if keyArr[1] == "dynamicPrimes":
            num = int(keyArr[2][:-(len(redisConst))])
            if int(n) == num:
                return cache.get(f'/dynamicPrimes/{num}{redisConst}')
            elif int(n) >= num:
                dynamic = True
                if int(n) - num < min:
                    min = int(n) - num
                    start = num
    if dynamic:
        arr = json.loads(cache.get(f'/dynamicPrimes/{start}{redisConst}'))
        for number in range(start, int(n)):
            skip = False
            i = 3
            while i * i <= number:
                if number % i == 0:
                    skip = True
                    break
                i += 2
            if not skip:
                arr.append(number)
        cache.add(f'/dynamicPrimes/{n}{redisConst}', json.dumps(arr))
        return json.dumps(arr)

    arr = [2]
    for number in range(3, int(n), 2):
        skip = False
        i = 3
        while i * i <= number:
            if number % i == 0:
                skip = True
            i += 2
        if not skip:
            arr.append(number)
    cache.add(f'/dynamicPrimes/{n}{redisConst}', json.dumps(arr))
    return json.dumps(arr)


@app.route("/primes/<data>", methods=['DELETE'])
def cleanPrimesCache(data):
    """Briše zadani podatak iz 'primes' cache memorije
    ---
    parameters:
      - name: data
        in: path
        type: string
        required: true
    responses:
      200:
        description: Podatak obrisan
    """
    redisDB.delete('flask_cache_/primes/' + data + redisConst)
    return "Cache data deleted"


@app.route("/dynamicPrimes/<data>", methods=['DELETE'])
def cleanDynamicPrimesCache(data):
    """Briše zadani podatak iz 'dynamicPrimes' cache memorije
    ---
    parameters:
      - name: data
        in: path
        type: string
        required: true
    responses:
      200:
        description: Podatak obrisan
    """
    redisDB.delete('flask_cache_/dynamicPrimes/' + data + redisConst)
    return "Cache data deleted"


@app.route("/primes/clean/<amount>", methods=['DELETE'])
def cleanCasheAmount(amount):
    """Briše određeni broj cache memorije ( '0' za sve )
    ---
    parameters:
      - name: amount
        in: path
        type: string
        required: true
    responses:
      200:
        description: Podaci obrisani
    """
    amount = abs(int(amount))
    for key in redisDB.keys():
        if not amount:
            break
        if str(key) != "timeout/time":
            redisDB.delete(key)
            amount -= 1
    return "Cashe cleaned"


@app.route("/primes/clean", methods=['DELETE'])
def cleanCashe():
    """Brisanje cache memorije
    ---
    responses:
      200:
        description: Briše sve iz cashe memorije
    """
    with app.app_context():
        cache.clear()
    return "Cleaned"


@app.route("/primes/get", methods=['GET'])
def getCashe():
    """Vraća listu sačuvanih vrijednosti
    ---
    responses:
      200:
        description: Sačuvane vrijednosti
    """
    arr = []
    for key in redisDB.keys():
        keyArr = key.split('/')
        if keyArr[0] == "flask_cache_":
            arr.append(keyArr[1] + '/' + keyArr[2][:-(len(redisConst))])
    return json.dumps(arr)


@app.route("/primes/setTimeout/<timeout>", methods=['POST'])
def setCasheTimeout(timeout):
    """Mjenja vrijeme kada se cache memorija briše (format HH:MM)
    ---
    parameters:
      - name: timeout
        in: path
        type: string
        required: true
        description: HH:MM
    responses:
      200:
        description: Nova cache-timeout vrijednost
    """
    redisDB.set('timeout/time', timeout)
    return "Timeout set"


def cleanCasheInterval():
    threading.Timer(60, cleanCasheInterval).start()
    schedule.run_pending()

schedule.every().day.at(str(redisDB.get('timeout/time'))).do(cleanCashe)
#clean cashe periodically
cleanCasheInterval()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
