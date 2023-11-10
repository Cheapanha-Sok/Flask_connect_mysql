import urllib
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

DATABASE_HOST = "localhost"
DATABASE_NAME = "ap"
DATABASE_USERNAME = "root"
DATABASE_PASSWORD = "nha@061809946Q"
app = Flask(__name__)
db = SQLAlchemy()

# to eliminate the error, if the password contains special characters like '@'
# replace the DATABASE_PASSWORD with DATABASE_PASSWORD_UPDATED.

DATABASE_PASSWORD_UPDATED = urllib.parse.quote_plus(DATABASE_PASSWORD)
app.config["SQLALCHEMY_DATABASE_URI"] = (
        "mysql+pymysql://"
        + DATABASE_USERNAME
        + ":"
        + DATABASE_PASSWORD_UPDATED
        + "@"
        + DATABASE_HOST
        + "/"
        + DATABASE_NAME
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
from models import terms, invoices

db.init_app(app)


@app.get("/terms")
def get_terms():
    t = db.session.query(terms).with_entities(
        terms.terms_id, terms.terms_description, terms.terms_due_days
    )

    ls = []
    for u in t:
        te = {
            "id": u.terms_id,
            "description": u.terms_description,
            "due_days": u.terms_due_days,
        }
        ls.append(te)
    return ls


@app.get("/terms1")
def get_terms1():
    t = db.session.query(terms).with_entities(
        terms.terms_id, terms.terms_description, terms.terms_due_days
    )
    lst = [v._asdict() for v in t]
    return lst


@app.get("/terms/<int:id>")
def get_term(id):
    t = (
        db.session.query(terms)
        .with_entities(terms.terms_id, terms.terms_description, terms.terms_due_days)
        .filter(terms.terms_id == id)
    )
    lst = [v._asdict() for v in t]
    return lst


@app.get("/invoices/term/<int:term_id>")
def get_invoice_term(term_id):
    inv = (
        db.session.query(invoices, terms)
        .join(terms, terms.terms_id == invoices.terms_id)
        .with_entities(invoices.invoice_number, terms.terms_description)
        .filter(invoices.terms_id == term_id)
        .all()
    )
    lst = [v._asdict() for v in inv]
    return lst


@app.post("/terms")
def post_terms():
    try:
        request_data = request.get_json()
        t = terms(
            terms_description=request_data["terms_description"],
            terms_due_days=request_data["terms_due_days"],
        )
        db.session.add(t)
        db.session.commit()
        return {"message": "success"}, 200
    except Exception as e:
        return {"message": "Something went wrong!"}, 500


@app.put("/terms/<string:des>")
def put_terms(des):
    request_data = request.get_json()
    t = db.session.query(terms).filter(terms.terms_description == des).first()
    if t:
        t.terms_description = request_data["terms_description"]
        t.terms_due_days = request_data["terms_due_days"]
        try:
            db.session.commit()
            return {"message": "Success"}, 200
        except exc.SQLAlchemyError as e:
            return {"message": str(e.__cause__)}, 500
    else:
        return {"message": "Term not found"}, 404


@app.delete("/terms/<int:id>")
def delete_terms(id):
    t = db.session.query(terms).filter(terms.terms_id == id).first()
    if t:
        db.session.delete(t)
        try:
            db.session.commit()
            return {"message": "Success"}, 200
        except exc.SQLAlchemyError as e:
            return {"message": str(e.__cause__)}, 500
    else:
        return {"message": "Term not found"}, 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
