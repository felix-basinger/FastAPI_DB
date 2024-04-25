from typing import List
import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import ForeignKey
import random
from datetime import datetime as DT
from datetime import timedelta

DATABASE_URL = "sqlite:///hw_database.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

goods = sqlalchemy.Table(
    "goods",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(100)),
    sqlalchemy.Column("description", sqlalchemy.String(500)),
    sqlalchemy.Column("price", sqlalchemy.Float)
)

orders = sqlalchemy.Table(
    "orders",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer, ForeignKey("users.id")),
    sqlalchemy.Column("good_id", sqlalchemy.Integer, ForeignKey("goods.id")),
    sqlalchemy.Column("order_date", sqlalchemy.String(10)),
    sqlalchemy.Column("order_status", sqlalchemy.String(150))
)

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String(40)),
    sqlalchemy.Column("second_name", sqlalchemy.String(50)),
    sqlalchemy.Column("email", sqlalchemy.String(128)),
    sqlalchemy.Column("password", sqlalchemy.String(255))
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": True}
)

metadata.create_all(engine)

app = FastAPI()


class UserIn(BaseModel):
    first_name: str = Field(max_length=40)
    second_name: str = Field(max_length=50)
    email: str = Field(max_length=128)
    password: str = Field(max_length=255)


class User(BaseModel):
    id: int
    first_name: str = Field(max_length=40)
    second_name: str = Field(max_length=50)
    email: str = Field(max_length=128)
    password: str = Field(max_length=255)


class GoodIn(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    price: float


class Good(BaseModel):
    id: int
    name: str = Field(max_length=100)
    description: str = Field(max_length=500)
    price: float


class OrderIn(BaseModel):
    user_id: int
    good_id: int
    order_date: str = Field(max_length=10)
    order_status: str = Field(max_length=150)


class Order(BaseModel):
    id: int
    user_id: int
    good_id: int
    order_date: str = Field(max_length=10)
    order_status: str = Field(max_length=150)


# -------------------Users--------------------

@app.get('/fake_users/{count}')
async def create_note(count: int):
    for i in range(count):
        pw = random.randint(100000, 999999)
        query = users.insert().values(first_name=f'User{i}', second_name=f'Petrov{i}',
                                      email=f'{i}user{i}@email.com', password=f'useer{pw}')
        await database.execute(query)
    return {'message': f'{count} users created'}


@app.post('/users/', response_model=User)
async def create_user(user: UserIn):
    query = users.insert().values(**user.dict())
    last_record_id = await database.execute(query)
    return {**user.dict(), "id": last_record_id}


@app.get('/users/', response_model=List[User])
async def read_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get('/users/{user_id}', response_model=User)
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, new_user: UserIn):
    query = users.update().where(users.c.id == user_id).values(**new_user.dict())
    await database.execute(query)
    return {**new_user.dict(), "id": user_id}


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    query = users.delete().where(users.c.id == user_id)
    await database.execute(query)
    return {'message': 'User deleted successfully'}


# ----------------------Goods----------------------


@app.get('/fake_goods/{count}')
async def create_goods(count: int):
    for i in range(count):
        rand_price = round(random.uniform(15, 150), 2)
        query = goods.insert().values(name=f'Good{i}', description="nidnjncecjdcjdn", price=rand_price)
        await database.execute(query)
    return {'message': f'{count} goods created'}


@app.post('/goods/', response_model=Good)
async def create_good(good: GoodIn):
    query = goods.insert().values(**good.dict())
    last_record_id = await database.execute(query)
    return {**good.dict(), "id": last_record_id}


@app.get('/goods/', response_model=List[Good])
async def read_goods():
    query = goods.select()
    return await database.fetch_all(query)


@app.get('/goods/{good_id}', response_model=Good)
async def read_goods(good_id: int):
    query = goods.select().where(goods.c.id == good_id)
    return await database.fetch_one(query)


@app.put("/goods/{good_id}", response_model=Good)
async def update_good(good_id: int, new_good: GoodIn):
    query = goods.update().where(goods.c.id == good_id).values(**new_good.dict())
    await database.execute(query)
    return {**new_good.dict(), "id": good_id}


@app.delete("/goods/{good_id}")
async def delete_good(good_id: int):
    query = goods.delete().where(goods.c.id == good_id)
    await database.execute(query)
    return {'message': 'Good deleted successfully'}


# -------------------------Orders----------------

@app.get('/fake_orders/{count}')
async def create_orders(count: int):
    for i in range(count):
        def get_rand_date(start, end):
            delta = end - start
            return start + timedelta(random.randint(0, delta.days))

        def get_order_status(status_list: list):
            return status_list[random.randint(0, 2)]

        order_status_list = ['Paid', 'Sent', 'Delivered']
        start_dt = DT.strptime('01.01.2022', '%d.%m.%Y')
        end_dt = DT.strptime('25.03.2024', '%d.%m.%Y')
        u_id = random.randint(0, 29)
        g_id = random.randint(0, 29)
        query = orders.insert().values(user_id=u_id, good_id=g_id,
                                       order_date=get_rand_date(start_dt, end_dt),
                                       order_status=get_order_status(order_status_list))

        await database.execute(query)
    return {'message': f'{count} orders created'}


@app.post('/orders/', response_model=Order)
async def create_order(order: OrderIn):
    query = orders.insert().values(**order.dict())
    last_record_id = await database.execute(query)
    return {**order.dict(), "id": last_record_id}


@app.get('/orders/', response_model=List[Order])
async def read_orders():
    query = orders.select()
    return await database.fetch_all(query)


@app.get('/orders/{order_id}', response_model=Order)
async def read_order(order_id: int):
    query = orders.select().where(orders.c.id == order_id)
    return await database.fetch_one(query)


@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, new_order: OrderIn):
    query = orders.update().where(orders.c.id == order_id).values(**new_order.dict())
    await database.execute(query)
    return {**new_order.dict(), "id": order_id}


@app.delete("/orders/{order_id}")
async def delete_order(order_id: int):
    query = orders.delete().where(orders.c.id == order_id)
    await database.execute(query)
    return {'message': 'Order deleted successfully'}
