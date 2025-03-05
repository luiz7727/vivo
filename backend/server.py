# Flask
from flask import (
    Flask,
    request,
    jsonify,
)
from flask_swagger_ui import get_swaggerui_blueprint
import atexit
import flask_cors
from datetime import datetime


# Project
import repos.cache as cache
import repos.vivo_dns as vivo_dns
import utils
import repos.updatable as updatable
import repos.dashboard as dashboard

import threading

app = Flask(__name__)

cors = flask_cors.CORS(app)

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"

thread_lock = threading.Lock()

# updatable.open_cache()
# cache.open_cache()


def close_running_threads():

    print("Closing DB Connection...")


# Register the function to be called on exit
atexit.register(close_running_threads)

# start your process
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "MapVIVO"}
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


# REGION DNS
@app.get("/dns/all")
def dns_all():
    produtos, status = vivo_dns.getAll()
    ok = (len(produtos) > 0) and status

    return jsonify(produtos), (200 if ok else 404)


@app.get("/dns/search/<produto>")
def dns_search(produto: str):
    produto, status = vivo_dns.search(produto.upper())

    return jsonify(
        {
            "ok": status,
            "content": produto if status else "Rota não encontrada",
        }
    ), (200 if status else 404)


@app.post("/dns/add")
def dns_add():
    name = str(request.json["name"]).upper()
    address = str(request.json["address"]).lower()
    status = vivo_dns.add(
        {
            "name": name,
            "address": address,
        }
    )

    return jsonify(
        {"message": "DNS Added" if status else "Failed to add dns", "ok": status}
    ), (200 if status == True else 404)


@app.delete("/dns/delete")
def dns_delete():
    index = request.args["id"]
    msg, status = vivo_dns.delete(index)

    return jsonify({"ok": status}), (200 if status == True else 404)


@app.get("/dns/names")
def dns_products():
    produtos, status = vivo_dns.products()
    ok = (len(produtos) > 0) and status

    return jsonify(
        {
            "ok": ok,
            "content": produtos,
        }
    ), (200 if ok else 404)


# END REGION


# REGION CACHE


@app.get("/cache/all")
def cache_all():
    with thread_lock:
        result, status = cache.getAll()
    print(status)
    if len(result) > 0:
        return jsonify(result), 200
    else:
        return jsonify({"status": "No entries in cache"}), 404


@app.get("/users/<user_id>/products")
def fetch(user_id: str):
    with thread_lock:
        print(user_id)
        cliente, status = cache.get(
            cliente=user_id.upper(),
        )
    if status == True and len(cliente) > 0:
        return jsonify(cliente), 200
    else:
        return (
            jsonify(
                {
                    "status": "Error",
                    "message": f"Unable to fetch entry with id {user_id}",
                }
            ),
            404,
        )


# PRODUTO | CLIENTE | DATA


@app.post("/cache/save")
def save():
    contents = request.json["contents"]
    id = contents["id"]
    with thread_lock:
        index, ok = cache.save(id, contents)

    return (
        jsonify(
            {
                "ok": ok,
                "message": (
                    f"Contents added to cache with key {index}"
                    if ok
                    else f"Oops something went wrong"
                ),
            }
        ),
        200 if ok else 500,
    )


@app.delete("/cache/delete")
def delete_cache():
    user_id = str(request.args["user_id"])

    with thread_lock:
        ok = cache.delete(user_id)
    return f"{user_id} Deleted" if ok else "Unable to delete", 200 if ok else 400


# END REGION


# REGION Updatable


@app.get("/updatable/all")
def clientes_all():
    with thread_lock:
        clients, ok = updatable.getAll()
    return {
        "ok": ok,
        "contents": clients,
    }, (200 if ok else 404)


@app.post("/updatable/add")
def clientes_add():
    user_id = str(request.json["user_id"])
    shards = list(request.json["shards"])
    in_cache = False

    with thread_lock:
        ok = updatable.add(
            {
                "user_id": user_id,
                "in_cache": in_cache,
                "last_seen": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "shards": shards,
            },
        )

    return jsonify(
        {
            "ok": ok,
            "message": (
                "user_id adicionado" if ok else "Não foi possível adicionar o user_id"
            ),
        }
    ), (200 if ok else 400)


@app.delete("/updatable/delete")
def cliente_delete():
    user_id = str(request.args["user_id"])
    with thread_lock:
        ok = updatable.delete(user_id)
    return f"{user_id} Deleted" if ok else "Unable to delete", 200 if ok else 400


@app.put("/updatable/update")
def cliente_update():
    user_id = str(request.json["user_id"])
    contents = dict(request.json["contents"])

    contents.update({"user_id": user_id})

    with thread_lock:
        ok = updatable.update(user_id, contents)

    return "Updated" if ok else "Unable to update", 200 if ok else 400


@app.get("/updatable/search")
def client_search():
    user_id = str(request.args["user_id"])
    with thread_lock:
        result, ok = updatable.get(user_id)
    return jsonify({"ok": ok, "message": result}), 200 if ok else 404


# END REGION


# REGION DASHBOARD (API)
@app.get("/dashboard/ping/<server>")
def ping(server: str):
    with thread_lock:
        respTime, ok = utils.ping(server)

    response = jsonify(
        {
            "server": server,
            "time": respTime,
        }
    )

    with thread_lock:
        result, status = vivo_dns.changePing(server, respTime)
    print(result, status)
    response.status_code == 200 if ok else 500
    return response



@app.get("/dashboard/usage")
def checkUsage():
    with thread_lock:
        ram, statusRam = utils.getRAM()

    response = jsonify(
        {
            "status": (statusRam),
            "ram": ram if statusRam else -1,
        }
    )

    return response, 200


@app.get("/dashboard/connector/users_cache")
def usersInCache():
    with thread_lock:
        in_cache, status = updatable.inCache()
        total, status_all = updatable.getAll()

    if status and status_all:
        return jsonify(
            {
                "in_cache": len(in_cache),
                "total": len(total),
            }
        ), 200
    else:
        return jsonify({
            "status": "FAIL",
            "message": "Unable to fetch data"
        })
    
@app.get("/dashboard/connector/last")
def connectorLastRun():
    run, status = dashboard.last()
    if(status == True and len(run) > 0):
        return jsonify(run[0]), 200
    else:
        return jsonify({
            "status": "FAIL",
            "message": "Unable to fetch last run"
        }), 500

@app.get("/dashboard/connector/runs")
def connectorRuns():
    with thread_lock:
        runs_total, ok = dashboard.getAll()
        runs_ok, ok_ok = dashboard.successful()

    return {
        "ok": ok and ok_ok,
        "stats": {
            "total": len(runs_total),
            "successful": len(runs_ok) if len(runs_total) >= 0 else -1
        },
    }, (200 if ok else 404)


@app.post("/dashboard/connector/run")
def connectorAddRun():
    last_run = request.json["last_run"]
    next_run = request.json["next_run"]
    ok = request.json["ok"]

    run = {
        "last_run": last_run,
        "next_run": next_run,
        "ok": ok,
    }

    ok = dashboard.add(run)
    
    return jsonify({
        "ok": ok,
        "message": "Run added successfully" if ok else "Unable to add run"
    }), 200 if ok else 500


@app.get("/dashboard/connector/all")
def runs_all():
    with thread_lock:
        clients, ok = updatable.getAll()
    return {
        "ok": ok,
        "contents": clients,
    }, (200 if ok else 404)

# END REGION

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)
