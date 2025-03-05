from flask import Flask, jsonify, request
from faker import Faker
import random

app = Flask(__name__)
faker = Faker()


# Helper function to generate random product data
def generate_product(user_id):
    product_types = [
        "mobile",
        "landline",
        "internet",
        "iptv",
        "bundle",
        "value_added_service",
    ]
    status_types = ["active", "activating", "suspended", "cancelled"]
    subscription_types = ["prepaid", "postpaid", "control"]

    return {
        "id": user_id,
        "product_name": faker.word(),
        "product_type": random.choice(product_types),
        "status": random.choice(status_types),
        "start_date": faker.date_time_this_decade().isoformat(),
        "subscription_type": random.choice(subscription_types),
        "identifiers": [faker.phone_number()],
        "descriptions": [{"text": faker.sentence()}],
        "sub_products": (
            [generate_product(user_id)] if random.choice([True, False]) else []
        ),
    }


@app.route("/users/<string:user_id>/products", methods=["GET"])
def list_user_products(user_id):
    # Simulate different responses based on query parameters or random
    if "status" in request.args and request.args["status"] not in [
        "active",
        "activating",
        "suspended",
        "cancelled",
    ]:
        return (
            jsonify(
                {
                    "code": "INVALID_ARGUMENT",
                    "message": "Client specified an invalid argument, request body or query param",
                }
            ),
            400,
        )

    return jsonify(generate_product(user_id))


# Error responses
@app.errorhandler(404)
def not_found(e):
    return (
        jsonify(
            {
                "code": "NOT_FOUND",
                "message": "A specified resource is not found",
            }
        ),
        404,
    )


@app.errorhandler(403)
def forbidden(e):
    return (
        jsonify(
            {
                "code": "PERMISSION_DENIED",
                "message": "Authenticated user has no permission to access the requested resource",
            }
        ),
        403,
    )


@app.errorhandler(504)
def timeout(e):
    return (
        jsonify(
            {
                "code": "TIMEOUT",
                "message": "Request timeout exceeded. Try it later",
            }
        ),
        504,
    )

# Mock data for Vivo Fibra
@app.route('/fibra/planos', methods=['GET'])
def get_fibra_planos():
    planos = [
        {
            "id": str(i),
            "nome": faker.word() + " Fibra",
            "velocidade_download": f"{faker.random_number(digits=3)} Mbps",
            "velocidade_upload": f"{faker.random_number(digits=2)} Mbps",
            "preco": f"R$ {faker.random_number(digits=2)},99",
            "descricao": faker.sentence()
        }
        for i in range(1, 3)
    ]
    return jsonify({"planos": planos})

@app.route('/fibra/planos/<id>', methods=['GET'])
def get_fibra_plano(id):
    plano = {
        "id": id,
        "nome": faker.word() + " Fibra",
        "velocidade_download": f"{faker.random_number(digits=3)} Mbps",
        "velocidade_upload": f"{faker.random_number(digits=2)} Mbps",
        "preco": f"R$ {faker.random_number(digits=2)},99",
        "descricao": faker.sentence()
    }
    return jsonify(plano)

# Mock data for Vivo Móvel
@app.route('/movel/planos', methods=['GET'])
def get_movel_planos():
    planos = [
        {
            "id": str(i),
            "nome": faker.word() + " Controle",
            "dados": f"{faker.random_number(digits=1)} GB",
            "chamadas": "Ilimitadas",
            "preco": f"R$ {faker.random_number(digits=2)},99",
            "descricao": faker.sentence()
        }
        for i in range(1, 3)
    ]
    return jsonify({"planos": planos})

@app.route('/movel/planos/<id>', methods=['GET'])
def get_movel_plano(id):
    plano = {
        "id": id,
        "nome": faker.word() + " Controle",
        "dados": f"{faker.random_number(digits=1)} GB",
        "chamadas": "Ilimitadas",
        "preco": f"R$ {faker.random_number(digits=2)},99",
        "descricao": faker.sentence()
    }
    return jsonify(plano)

# Mock data for Vivo Televisão
@app.route('/televisao/pacotes', methods=['GET'])
def get_televisao_pacotes():
    pacotes = [
        {
            "id": str(i),
            "nome": faker.word() + " TV Básica",
            "canais": f"{faker.random_number(digits=2)} canais",
            "preco": f"R$ {faker.random_number(digits=2)},99",
            "descricao": faker.sentence()
        }
        for i in range(1, 3)
    ]
    return jsonify({"pacotes": pacotes})

@app.route('/televisao/pacotes/<id>', methods=['GET'])
def get_televisao_pacote(id):
    pacote = {
        "id": id,
        "nome": faker.word() + " TV Básica",
        "canais": f"{faker.random_number(digits=2)} canais",
        "preco": f"R$ {faker.random_number(digits=2)},99",
        "descricao": faker.sentence()
    }
    return jsonify(pacote)

# Mock data for Vivo Fixo
@app.route('/fixo/planos', methods=['GET'])
def get_fixo_planos():
    planos = [
        {
            "id": str(i),
            "nome": faker.word() + " Fixo Básico",
            "minutos": f"{faker.random_number(digits=3)} minutos",
            "preco": f"R$ {faker.random_number(digits=2)},99",
            "descricao": faker.sentence()
        }
        for i in range(1, 3)
    ]
    return jsonify({"planos": planos})

@app.route('/fixo/planos/<id>', methods=['GET'])
def get_fixo_plano(id):
    plano = {
        "id": id,
        "nome": faker.word() + " Fixo Básico",
        "minutos": f"{faker.random_number(digits=3)} minutos",
        "preco": f"R$ {faker.random_number(digits=2)},99",
        "descricao": faker.sentence()
    }
    return jsonify(plano)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5100)
