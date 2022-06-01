from typing import List


class Rocket:
    """represents a rocket"""
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
    """represents a business"""
    def __init__(
        self,
        owner_id: int,
        name: str,
        rockets: List[Rocket],
        last_claim_time: int,
        money: int,
    ):
        self.owner_id = owner_id
        self.name = name
        self.rockets = rockets
        self.last_claim_time = last_claim_time
        self.money = money

    def to_dict(self):
        return {
            "owner_id": self.owner_id,
            "name": self.name,
            "rockets": [rocket.to_dict() for rocket in self.rockets],
            "last_claim_time": self.last_claim_time,
            "money": self.money,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["owner_id"],
            data["name"],
            [Rocket.from_dict(rocket) for rocket in data["rockets"]],
            data["last_claim_time"],
            data["money"],
        )

class Item:
    """
    represents a stat upgrade
    """
    def __init__(self,name:str,price:int,emoji:str,step:int):
        self.name = name
        self.price = price
        self.emoji = emoji
        self.step = step
    
    def multiplier(self,multiply:int):
        self.price *= multiply
    
    def from_dict(self,data:dict):
        self.name = data["name"]
        self.price = data["price"]
        self.emoji = data["emoji"]
    
    def to_dict(self):
        return {
            "name":self.name,
            "price":self.price,
            "emoji":self.emoji
        }