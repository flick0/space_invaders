from typing import List


class Rocket:
    def __init__(self, name: str, rate: float, price: float):
        self.name = name
        self.rate = rate
        self.price = price

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["name"], data["rate"], data["price"])

    def to_dict(self):
        return {"name": self.name, "rate": self.rate, "price": self.price}


class Business:
    def __init__(
        self,
        owner_id: int,
        name: str,
        rockets: List[Rocket],
        income_per_second: int,
        last_claim_time: int,
        money: int,
    ):
        self.owner_id = owner_id
        self.name = name
        self.rockets = rockets
        self.income_per_second = income_per_second
        self.last_claim_time = last_claim_time
        self.money = money

    def to_dict(self):
        return {
            "owner_id": self.owner_id,
            "name": self.name,
            "rockets": [rocket.to_dict() for rocket in self.rockets],
            "income_per_second": self.income_per_second,
            "last_claim_time": self.last_claim_time,
            "money": self.money,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["owner_id"],
            data["name"],
            [Rocket.from_dict(rocket) for rocket in data["rockets"]],
            data["income_per_second"],
            data["last_claim_time"],
            data["money"],
        )
