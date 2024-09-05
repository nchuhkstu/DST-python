import os

from utils.global_variable import user


class UserService:
    def __init__(self):
        pass

    @staticmethod
    def get_users(cluster_name):
        return user[cluster_name]

