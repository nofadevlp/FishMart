# -- Flask => Create HTML Files --
#name on pythonanywhere
# /home/nofadevlp/mysite/flask_app.py
# --------------------------------
# Libraries that we needed
import datetime
from datetime import date
from sqlalchemy import Column, extract
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL
from wtforms import SelectField
from flask_wtf import FlaskForm

# configuration and config connect to database
mysql = MySQL()
# app is the name of our project in flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cfa.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://root:''@localhost/cfa'
# ignore some issue errors
app.secret_key = "cfa123"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


################################# Tables in database
#####################################################################


class Boats(db.Model):
    # table name
    __tablename__ = 'boats'
    # columns
    boat_id = db.Column("boat_id", db.Integer(), primary_key=True, autoincrement='auto')
    boat_name = db.Column("boat_name", db.String(50), nullable=False)
    licences = db.Column("licences", db.String(200), unique=True, nullable=False)

    def __init__(self, boat_name, licences):
        self.licences = licences
        self.boat_name = boat_name


class Agents(db.Model):
    # table name
    __tablename__ = 'agents'
    # columns
    agent_id = Column("agent_id", db.Integer(), primary_key=True, autoincrement='auto')
    agent_serial = Column("agent_serial", db.String(50), unique=True, nullable=False)
    agent_name = Column("agent_name", db.String(50), nullable=False)

    def __init__(self, agent_name, agent_serial):
        self.agent_name = agent_name
        self.agent_serial = agent_serial


class Fishes(db.Model):
    __tablename__ = 'fishes'
    # columns
    fish_id = Column("fish_id", db.Integer(), primary_key=True, autoincrement='auto')
    fish_type = Column("fish_type", db.String(50), nullable=False, unique=True)

    def __init__(self, fish_type):
        self.fish_type = fish_type


class DeliverLoads(db.Model):
    __tablename__ = 'deliver_loads'
    # columns
    id = db.Column("id", db.Integer(), primary_key=True, autoincrement='auto')
    batch_id = db.Column("batch_id", db.Integer(), unique=True, nullable=False)
    boat = db.Column("boat", db.String(50), db.ForeignKey("boats.licences"), nullable=False)
    load_date = db.Column("load_date", nullable=False)
    exp_date = db.Column("exp_date", nullable=False)
    fish_type = db.Column("fish_type", db.String(100), db.ForeignKey("fishes.fish_type"), nullable=False)
    quantity_kg = db.Column("quantity_kg", db.Integer(), nullable=False)

    def __init__(self, batch_id, boat, load_date, exp_date, fish_type, quantity_kg):
        self.batch_id = batch_id
        self.boat = boat
        self.load_date = load_date
        self.exp_date = exp_date
        self.fish_type = fish_type
        self.quantity_kg = quantity_kg


class Loads_save(db.Model):
    __tablename__ = 'loads_save'
    # columns random.randrange(1, 5000, 2)
    id = db.Column("id", db.Integer(), primary_key=True, autoincrement='auto')
    batch_id = db.Column("batch_id", db.Integer(), db.ForeignKey("deliver_loads.batch_id"), nullable=False)
    boat = db.Column("boat", db.String(50), db.ForeignKey("boats.licences"), nullable=False)
    fish_type = db.Column("fish_type", db.String(100), nullable=False)
    quantity_kg = db.Column("quantity_kg", db.Integer(), nullable=False)
    load_date = db.Column("load_date", nullable=False)

    def __init__(self, batch_id, boat, fish_type, quantity_kg, load_date):
        self.batch_id = batch_id
        self.boat = boat
        self.fish_type = fish_type
        self.quantity_kg = quantity_kg
        self.load_date = load_date


class Orders(db.Model):
    __tablename__ = 'orders'
    # columns
    order_id = db.Column("order_id", db.Integer(), primary_key=True, autoincrement='auto')
    fish_type = db.Column("fish_type", db.String(50), db.ForeignKey("deliver_loads.fish_type"), nullable=False)
    quantity_kg = db.Column("quantity_kg", db.Integer(), nullable=False)
    agent = db.Column("agent", db.String(50), db.ForeignKey("agents.agent_serial"), nullable=False)
    order_date = db.Column("order_date", nullable=False)
    state = db.Column("state", db.String(50), nullable=False)
    batch_id = db.Column("batch_id", db.Integer(), db.ForeignKey("deliver_loads.batch_id"), nullable=False)

    def __init__(self, fish_type, quantity_kg, agent, order_date, state, batch_id):
        self.fish_type = fish_type
        self.quantity_kg = quantity_kg
        self.agent = agent
        self.order_date = order_date
        self.state = state
        self.batch_id = batch_id


# create table in cfa.db
########################################################################################
#connect to db an creates tables
@app.route("/c")
def connect():
    try:
        db.create_all()
        # db.drop_all()
        return "<div align=center><h1>Creates table</h1></div>"
        # return "Droped table"
    except:
        return '<html><body><h1>Poor Connection</h1></body></html>'


class Form(FlaskForm):
    fish = SelectField(u'fish', choices=[])
    agents = SelectField(u'agents', choices=[])
    boat = SelectField(u'boat', choices=[])


@app.errorhandler(404)
def invalid_route(e):
    return jsonify({'errorCode': 404, 'message': 'Page not found'})


@app.route("/report")
def report():
    form4 = Form()
    form4.boat.choices = [boat.licences for boat in Boats.query.all()]
    return render_template("report.html", title="Manage CFA", form=form4)


@app.route("/report_load", methods=['GET', 'POST'])
def load_report():
    if request.method == 'POST':
        if request.form.get('boat') != '':
            load = Loads_save.query.filter(Loads_save.load_date.between
                                           (request.form.get('load_date1'),
                                            request.form.get('load_date2'), False)
                                             & (Loads_save.boat == request.form.get('boat'))).all()
        elif request.form.get('boat') == '':
            load = Loads_save.query.filter(Loads_save.load_date.between
                                       (request.form.get('load_date1'),
                                        request.form.get('load_date2'), False)).all()
        return render_template("report_load.html", title="Load Report", load=load)


@app.route("/order_report", methods=['GET', 'POST'])
def order_report():
    order = Orders.query.filter_by(state='Pendent').all()
    return render_template("report_order.html", title="Orders Reports", order=order)


@app.route("/boat_report", methods=['GET', 'POST'])
def boat_report():
    if request.method == "POST":
        boat = Loads_save.query.with_entities(Loads_save.boat, Loads_save.fish_type,
                                                db.func.sum(Loads_save.quantity_kg).label('total_quantity')) \
            .filter(Loads_save.load_date.between(request.form.get('load_date1'),
                                                   request.form.get('load_date2'), False)) \
            .group_by(Loads_save.fish_type).all()
        return render_template("boat_report.html", title="Orders Reports", boat=boat)


@app.route("/loads_dist", methods=['GET', 'POST'])
def distribute_report():
    if request.method == "POST":
        if request.form.get('batch') != '':
            boat = Orders.query.with_entities(Orders.batch_id, Orders.agent, Orders.fish_type,
                                              Orders.quantity_kg) \
                .filter(Orders.order_date.between
                        (request.form.get('load_date1'),
                         request.form.get('load_date2'), False)
                   & (Orders.batch_id == request.form.get('batch'))).all()
        elif request.form.get('batch') == '':
            boat = Orders.query.with_entities(Orders.batch_id, Orders.agent, Orders.fish_type,
                                              Orders.quantity_kg) \
                .filter(Orders.order_date.between
                        (request.form.get('load_date1'),
                         request.form.get('load_date2'), False)).all()
        return render_template("distribute.html", title="Distributed Reports", boat=boat)


@app.route("/compare+", methods=['GET', 'POST'])
def compare():
    if request.method == 'POST':
        total = Orders.query.with_entities(Orders.fish_type,
                                           db.func.sum(Orders.quantity_kg).label('total_request'), Orders.state).all()
        total_ = Orders.query.with_entities(Orders.fish_type, db.func.sum(Orders.quantity_kg).label('total_request'), Orders.state). \
            filter(Orders.order_date.between(request.form.get('load_date1'),
                                             request.form.get('load_date2'), False)).group_by(Orders.state).all()

        a = []
        for row in total:
            print(row)
            for col in total_:
                print(col)
                t = row[1]
                c = col[1]
                per = (c / t) * 100
                a.append([round(per, 2), col[2]])
                # a.append(col[2])
                print(f"{per}% {col[2]}")
            print(a[0][0]+a[1][0])
            print(f"\n \n {a}")

        return render_template("compare+.html", title="Orders Reports", total_=total, total=total_, a=a)


@app.route("/show+relation", methods=['GET', 'POST'])
def show():
    show = Loads_save.query.with_entities(extract('month', Loads_save.load_date).label('month'),
                                            Loads_save.fish_type.label('fish_type'),
                                            db.func.sum(Loads_save.quantity_kg).label('total')). \
        filter(extract('month', Loads_save.load_date)) \
        .group_by(Loads_save.fish_type).all()
    print(show)
    return render_template("show+relation.html", title="Orders Reports", show=show)


@app.route("/agent/<int:page_num>", methods=['GET', 'POST'])
def agent(page_num):
    all_agent = Agents.query.order_by(Agents.agent_id.desc()).paginate(per_page=5, page=page_num, error_out=True)
    if request.method == "POST":
        if 'serial' in request.form:
            all_data = Agents.query.filter_by(agent_serial=request.form.get('serial')).paginate(per_page=5, page=page_num, error_out=False)
            db.session.commit()
            return render_template("agent.html", title="Loads", agent=all_data)
        else:
            page = request.args.get('page', 1, type=int)
            return redirect(url_for('agent', page_num=page))
    return render_template("agent.html", title="Manage CFA", agent=all_agent)


@app.route("/add_agent", methods=['POST'])
def add_agent():
    page = request.args.get('page', 1, type=int)
    try:
      if request.method == 'POST':
          agent = request.form['agent']
          serial = request.form['serial']
          my_agent = Agents(agent, serial)
          db.session.add(my_agent)
          db.session.commit()
          flash("Add Agents successfully")
          return redirect(url_for('agent', page_num=page))
    except:
      flash("Agent Add un successfully")
      return redirect(url_for('agent', page_num=page))


@app.route("/update_agent", methods=['POST'])
def update_agent():
    page = request.args.get('page', 1, type=int)
    try:
        if request.method == 'POST':
            my_agent = Agents.query.get(request.form.get('id'))
            my_agent.agent_name = request.form['agent']
            my_agent.agent_serial = request.form['serial']
            db.session.commit()
            flash("Agent Edite successfully")
            return redirect(url_for('agent', page_num=page))
    except:
        flash("Edite un successfully")
        return redirect(url_for('agent', page_num=page))


@app.route("/delete_agent/<id>", methods=['GET','POST'])
def delete_agent(id):
    page = request.args.get('page', 1, type=int)
    try:
        my_agent = Agents.query.get(id)
        db.session.delete(my_agent)
        db.session.commit()
        flash("Agent Deleted")
        return  redirect(url_for('agent', page_num=page))
    except:
        flash("Agent un Delete")
        return redirect(url_for('agent', page_num=page))


@app.route("/boat/<int:page_num>", methods=['GET', 'POST'])
def boat(page_num):
    all = Boats.query.order_by(Boats.boat_id.desc()).paginate(per_page=5, page=page_num, error_out=True)
    if request.method == "POST":
        if 'licences' in request.form:
            all_data = Boats.query.filter_by(licences=request.form.get('licences')).paginate(per_page=5, page=page_num, error_out=False)
            db.session.commit()
            return render_template("boats.html", title="Boats", boats=all_data)
        else:
            page = request.args.get('page', 1, type=int)
            return redirect(url_for('boat', page_num=page))
    return render_template("boats.html", title='Fishing Boats', boats=all)


@app.route("/boat", methods=['POST'])
def add_boat():
    page = request.args.get('page', 1, type=int)
    try:
        if request.method == 'POST':
            boat = request.form['boat']
            serial = request.form['licences1']
            my_boat = Boats(boat, serial)
            db.session.add(my_boat)
            db.session.commit()
            flash("Add boat successfully".capitalize())
            return redirect(url_for('boat', page_num=page))
    except:
        flash("boat licences already exist".capitalize())
        return render_template("boat.html", page_num=page)


@app.route('/update_boat', methods=['GET', 'POST'])
def update_boat():
    page = request.args.get('page', 1, type=int)
    try:
        if request.method == 'POST':
            my_boat = Boats.query.get(request.form.get('id'))
            my_boat.boat_name = request.form['boat_name']
            my_boat.licences = request.form['licences']
            db.session.commit()
            flash("boat Edit Successfully".capitalize())
            return redirect(url_for('boat', page_num=page))
    except:
        flash("boat Edit un Successfully".capitalize())
        return redirect(url_for('boat', page_num=page))


@app.route('/delete_boat/<id>', methods=['GET', 'POST'])
def delete_boat(id):
    page = request.args.get('page', 1, type=int)
    try:
        my_boat = Boats.query.get(id)
        db.session.delete(my_boat)
        db.session.commit()
        flash("boat deleted successfully".capitalize())
        return redirect(url_for('boat', page_num=page))
    except:
        flash("boat Delete un Successfully".capitalize())
        return redirect(url_for('boat', page_num=page))


@app.route("/loads/<int:page_num>", methods=['GET', 'POST'])
def loads(page_num):
    all_data = DeliverLoads.query.order_by(DeliverLoads.id.desc()).paginate(per_page=5, page=page_num, error_out=True)
    form = Form()
    form.fish.choices = [fish.fish_type for fish in Fishes.query.all()]
    form3 = Form()
    form3.boat.choices = [boat.licences for boat in Boats.query.all()]
    if request.method == "POST":
        if 'batch_id' in request.form:
            all_data = DeliverLoads.query.filter_by(batch_id=request.form.get('batch_id')).paginate(per_page=5, page=page_num, error_out=False)
            db.session.commit()
            return render_template("loads.html", title="Loads", form=form, form3=form3,
                                   loads=all_data)
        else:
            page = request.args.get('page', 1, type=int)
            return redirect(url_for('loads', page_num=page))

    return render_template("loads.html", title="Manage CFA", loads=all_data, form=form, form3=form3)


@app.route("/insert", methods=['POST'])
def insert_load():
    page = request.args.get('page', 1, type=int)
    try:
        if request.method == 'POST':
            batch_id = request.form['batch_id']
            boat = request.form['boat']
            date = request.form['date']
            exp = request.form['exp']
            fish = request.form['fish']
            quantity = request.form['quantity_kg']
            my_data = DeliverLoads(batch_id, boat, date, exp, fish, quantity)
            save = Loads_save(batch_id, boat, fish, quantity,date)
            db.session.add(my_data)
            db.session.add(save)
            db.session.commit()
            flash("Insert Load successfully".capitalize())
            return redirect(url_for('loads', page_num=page))
    except:
        flash("Load number is allready exist".capitalize())
        return redirect(url_for('loads', page_num=page))


@app.route('/update', methods=['GET', 'POST'])
def update_load():
    page = request.args.get('page', 1, type=int)
    try:
        if request.method == 'POST':
            my_data = DeliverLoads.query.get(request.form.get('d_id'))
            my_data.load_id = request.form['batch_id']
            my_data.boat = request.form['boat']
            my_data.load_date = request.form['date']
            my_data.exp_date = request.form['exp']
            my_data.fish_type = request.form['fish']
            my_data.quantity_kg = request.form['quantity_kg']
            db.session.commit()
        flash("Deliver Edit Successfully".capitalize())
        return redirect(url_for('loads', page_num=page))
    except:
        flash("Deliver Load Not Edit".capitalize())
        return redirect(url_for('loads', page_num=page))


@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete(id):
    page = request.args.get('page', 1, type=int)
    try:
        my_data = DeliverLoads.query.get(id)
        db.session.delete(my_data)
        db.session.commit()
        flash("Load deleted successfully".capitalize())
        return redirect(url_for('loads', page_num=page))
    except:
        flash("Load un Delete".capitalize())
        return redirect(url_for('loads', page_num=page))


@app.route("/order/<int:page_num>", methods=['GET', 'POST'])
def order(page_num):
    state = [{'state': 'Delivered'}, {'state': 'Pendent'}]
    orders = Orders.query.order_by(Orders.order_id.desc()).paginate(per_page=5, page=page_num, error_out=True)
    form = Form()
    form2 = Form()
    form.fish.choices = [fish.fish_type for fish in DeliverLoads.query.group_by(DeliverLoads.fish_type).all()]
    form2.agents.choices = [agents.agent_serial for agents in Agents.query.all()]
    if request.method == "POST":
        if 'order_id' in request.form:
            orders = Orders.query.filter_by(order_id=request.form.get('order_id')).paginate(per_page=5, page=page_num, error_out=False)
            db.session.commit()
            return render_template("orders.html", title="Orders", form=form, form2=form2,
                                   orders=orders,
                                   state=state)
        else:
            page = request.args.get('page', 1, type=int)
            return redirect(url_for('order', page_num=page))

    return render_template("orders.html", title="Orders", form=form, form2=form2,
                           orders=orders,
                           state=state)

# @app.route("/search_order", methods=['GET', 'POST'])
# def search_order():
#     try:
#         if request.method == "POST":
#             my_order = Orders.query.filter_by(order_id=request.form.get('order_id')).all()
#             print(my_order)
#             db.session.commit()
#             state = [{'state': 'Delivered'}, {'state': 'Pendent'}]
#             form = Form()
#             form2 = Form()
#             form.fish.choices = [fish.fish_type for fish in Fishes.query.all()]
#             form2.agents.choices = [agents.agent_serial for agents in Agents.query.all()]
#             flash(f"Order number Founded ".capitalize())
#             # return redirect(url_for('search_order', title="Orders",
#             #                        order=my_order))
#             return render_template("search.html", title="Orders",
#                                    form=form, form2=form2,
#                                    order=my_order,
#                                    state=state)
#     except:
#
#         flash("Order number NOT Founded ".capitalize())
#         return render_template("search.html", title="Orders",
#                                    order=my_order)


@app.route("/insert_order", methods=['GET', 'POST'])
def insert_order():
    page = request.args.get('page', 1, type=int)
    try:
        get_quantity = DeliverLoads.query.with_entities(DeliverLoads.batch_id,
                                                        DeliverLoads.quantity_kg,
                                                        DeliverLoads.fish_type,
                                                        DeliverLoads.exp_date,
                                                        DeliverLoads.id).all()

        quantity = [row for row in get_quantity]
        # print(f"{len(quantity)} \n {quantity} \n")
        if request.method == 'POST':
            fish = request.form['fish']
            quantity_kg = request.form['quantity_kg']
            agent = request.form['agents']
            date = request.form['date']
            state = request.form['state']
            for row in quantity:
                # print(row)
                batch_id = str(row[0])
                print(f"{batch_id} \n \n ...........")
                my_order = Orders(fish, quantity_kg, agent, date, state, batch_id)
                if int(quantity_kg) <= row[1] and fish == row[2]:
                    # print(row[3], '\n', datetime.date.today())
                    print(f"{row} Successfuly \n {row[0]}")
                    update = DeliverLoads.query.get(row[4])
                    r = row[1] - int(quantity_kg)
                    update.quantity_kg = r
                    print(update.quantity_kg)
                    print(f"new quantity {r}")
                    db.session.add(my_order)
                    db.session.commit()
                    flash("Add Order successfully".capitalize())
                    return redirect(url_for('order', page_num=page))
                    # break

            else:
                print(f"{row} Quantity \n {row[0]}")
                my_order.state = 'Pendent'
                db.session.commit()
                flash("Quantity is not available for this Fish".capitalize())
                return redirect(url_for('order', page_num=page))
                # break
        #     else:
        #         flash("Tray again".capitalize())
        #         return redirect(url_for('order'))
        # return render_template("orders.html", page_num=page)
    except:
        flash("Add Order not successfully".capitalize())
        return redirect(url_for('order', page_num=page))


@app.route("/update_order", methods=['GET', 'POST'])
def update_order():
    page = request.args.get('page', 1, type=int)
    try:
        if request.method == 'POST':
            batch_id = request.form.get('batch_id')
            my_order = Orders.query.get(request.form.get('order_id'))
            my_order.fish_type = request.form.get('fish')
            my_order.quantity_kg = request.form['quantity_kg']
            my_order.agent = request.form['agents']
            my_order.order_date = request.form['date']
            my_order.state = request.form['state']
            db.session.commit()
            flash("Order Edit Successfully".capitalize())
            return redirect(url_for('order', page_num=page))
    except:
        flash("Order un Edite".capitalize())
        return redirect(url_for('order', page_num=page))

# for row in quantity:
#     # print(row)
#     batch = str(row[0])
#     print(f"{batch_id} \n \n ...........")
#     if batch_id == batch and int(my_order.quantity_kg) <= row[1]:
#         # print(row[3], '\n', datetime.date.today())
#         print(f"{row} Successfuly \n {row[0]}")
#         update = DeliverLoads.query.get(row[4])
#         r = row[1] - int(my_order.quantity_kg)
#         update.quantity_kg = r
#         print(update.quantity_kg)
#         print(f"new quantity {r}")
#         db.session.commit()
#         # order = Orders.query.all()
#     elif batch_id == batch and int(my_order.quantity_kg) > row[1]:
#         print(f"{row} NOT Successfuly \n {row[0]}")
#         update = DeliverLoads.query.get(row[4])
#         r = row[1] + int(my_order.quantity_kg)
#         update.quantity_kg = r
#         my_order.quantity_kg = 0
#         print(update.quantity_kg)
#         print(f"new quantity {r}")
#         flash("NON Edit ".capitalize())
#         return redirect(url_for('order', page_num=page))
# else:
#     flash("WRong ".capitalize())
#     return redirect(url_for('order', page_num=page))
#
#
# # orders = [orders for orders in order]
# # print(orders)
# # for row in orders:
# #     print(f"{row.order_id}\n.............")
# #     print(f"int(request.form.get('order_id'))")
# #     if int(request.form.get('order_id')) == row.order_id:
# #         if int(my_order.quantity_kg) == row.quantity_kg and my_order.fish_type == row.fish_type:
# #             db.session.commit()
# #             flash("Order Edit Successfully".capitalize())
# #             return redirect(url_for('order', page_num=page))
# #         elif int(my_order.quantity_kg) != row.quantity_kg and my_order.fish_type != row.fish_type:
# #             flash("quantaty NOT ".capitalize())
# #             return redirect(url_for('order', page_num=page))
# # else:
# #     flash("NON Edit Successfully".capitalize())
# #     return redirect(url_for('order', page_num=page))


@app.route("/delete_order/<order_id>", methods=['GET', 'POST'])
def delete_order(order_id):
    page = request.args.get('page', 1, type=int)
    try:
        my_order = Orders.query.get(order_id)
        db.session.delete(my_order)
        db.session.commit()
        flash("Order deleted successfully".capitalize())
        return redirect(url_for('order', page_num=page))
    except:
        flash("Order un deleted".capitalize())
        return redirect(url_for('order', page_num=page))


@app.route("/fishes")
def fishes():
    all = Fishes.query.all()
    return render_template("fishes.html", title="Manage CFA", fish=all)


@app.route("/fish", methods=['POST'])
def add_fish():
    try:
        if request.method == 'POST':
            fish = request.form['fish']
            my_fish = Fishes(fish)
            db.session.add(my_fish)
            db.session.commit()
            flash("Add fish successfully".capitalize())
            return redirect(url_for('fishes'))
    except:
        flash("Fish type already exist".capitalize())
        return render_template("fishes.html")


@app.route('/update_fish', methods=['GET', 'POST'])
def update_fish():
    try:
        if request.method == 'POST':
            my_fish = Fishes.query.get(request.form.get('id'))
            my_fish.fish_type = request.form['fish']
            db.session.commit()
            flash("Fish Edit Successfully".capitalize())
            return redirect(url_for('fishes'))
    except:
        flash("Fish type un Edite".capitalize())
        return render_template("fishes.html")


@app.route('/delete_fish/<id>', methods=['GET', 'POST'])
def delete_fish(id):
    try:
        my_fish = Fishes.query.get(id)
        db.session.delete(my_fish)
        db.session.commit()
        flash("Fish deleted successfully".capitalize())
        return redirect(url_for('fishes'))
    except:
        flash("Fish deleted un successfully".capitalize())
        return redirect(url_for('fishes'))


if __name__ == "__main__":
    app.run(debug=True, port=9000)


