import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from stellar_sdk import (
Keypair,
Server,
Network,
TransactionEnvelope,
TransactionBuilder,
)

load_dotenv()

app = Flask(name)

logging.basicConfig(level=logging.INFO)

NETWORK = os.getenv("STELLAR_NETWORK", "testnet")

if NETWORK == "public":
HORIZON_URL = "https://horizon.stellar.org"
NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE
else:
HORIZON_URL = "https://horizon-testnet.stellar.org"
NETWORK_PASSPHRASE = Network.TESTNET_NETWORK_PASSPHRASE

server = Server(HORIZON_URL)

SPONSOR_SECRET = os.getenv("LUMI_SPONSOR_SECRET")

if not SPONSOR_SECRET:
raise RuntimeError(
"LUMI_SPONSOR_SECRET is missing. "
"Add it to your .env file."
)

sponsor = Keypair.from_secret(SPONSOR_SECRET)

Basic MVP safety limits.

MAX_SPONSOR_FEE_STROOPS = 10000
MAX_XDR_LENGTH = 50000

@app.get("/health")
def health():
return jsonify({
"service": "Lumi",
"status": "online",
"network": NETWORK,
"sponsor": sponsor.public_key()
})

@app.get("/sponsor")
def sponsor_info():
try:
account = server.load_account(sponsor.public_key())

    return jsonify({
        "sponsor": sponsor.public_key(),
        "network": NETWORK,
        "sequence": account.sequence,
        "status": "ready"
    })

except Exception as exc:
    logging.exception("Unable to load sponsor account")

    return jsonify({
        "status": "error",
        "message": str(exc)
    }), 500

@app.post("/sponsor")
def sponsor_transaction():
"""
Accept a user-signed Stellar transaction envelope in XDR.

Lumi validates the envelope, creates a fee-bump transaction,
signs the outer transaction with the sponsor account,
and submits it to Stellar.
"""

data = request.get_json(silent=True)

if not data:
    return jsonify({
        "error": "JSON request body required"
    }), 400

xdr = data.get("xdr")

if not xdr:
    return jsonify({
        "error": "Missing transaction XDR"
    }), 400

if len(xdr) > MAX_XDR_LENGTH:
    return jsonify({
        "error": "Transaction XDR is too large"
    }), 400

try:
    # Parse the user-signed transaction.
    inner_transaction = TransactionEnvelope.from_xdr(
        xdr,
        NETWORK_PASSPHRASE
    )

    # Only ordinary transactions should enter this MVP endpoint.
    if not hasattr(inner_transaction, "transaction"):
        return jsonify({
            "error": "Invalid transaction envelope"
        }), 400

    transaction = inner_transaction.transaction

    operation_count = len(transaction.operations)

    if operation_count < 1:
        return jsonify({
            "error": "Transaction contains no operations"
        }), 400

    # Base fee for the inner transaction.
    inner_base_fee = transaction.fee

    # The sponsor fee is calculated from the number of operations.
    # 100 stroops is Stellar's standard base fee.
    sponsor_base_fee = max(
        100,
        inner_base_fee
    )

    total_fee = sponsor_base_fee * (operation_count + 1)

    if total_fee > MAX_SPONSOR_FEE_STROOPS:
        return jsonify({
            "error": "Transaction exceeds Lumi sponsorship limit",
            "fee_stroops": total_fee,
            "maximum_stroops": MAX_SPONSOR_FEE_STROOPS
        }), 400

    # Build the fee-bump transaction.
    fee_bump = TransactionBuilder.build_fee_bump_transaction(
        fee_source=sponsor,
        base_fee=sponsor_base_fee,
        inner_transaction_envelope=inner_transaction,
        network_passphrase=NETWORK_PASSPHRASE
    )

    # Lumi signs only the fee-bump layer.
    fee_bump.sign(sponsor)

    # Submit to Stellar.
    response = server.submit_transaction(fee_bump)

    return jsonify({
        "status": "submitted",
        "transaction_hash": response["hash"],
        "sponsor": sponsor.public_key(),
        "network": NETWORK,
        "fee_stroops": total_fee
    }), 200

except Exception as exc:
    logging.exception("Sponsorship failed")

    return jsonify({
        "status": "failed",
        "error": str(exc)
    }), 400

@app.get("/transaction/<tx_hash>")
def transaction_status(tx_hash):
try:
transaction = server.transactions().get(tx_hash).call()

    return jsonify({
        "status": "success",
        "hash": tx_hash,
        "ledger": transaction.get("ledger"),
        "successful": transaction.get("successful"),
        "fee_charged": transaction.get("fee_charged")
    })

except Exception:
    return jsonify({
        "status": "not_found_or_pending",
        "hash": tx_hash
    }), 404

@app.errorhandler(404)
def not_found(_error):
return jsonify({
"error": "Endpoint not found"
}), 404

@app.errorhandler(500)
def internal_error(_error):
return jsonify({
"error": "Internal server error"
}), 500

if name == "main":
app.run(
host="127.0.0.1",
port=5000,
debug=False
)