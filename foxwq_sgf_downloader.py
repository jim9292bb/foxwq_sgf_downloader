# coding=utf-8

import os
import urllib
from urllib.request import urlopen
import json
import datetime
import collections
import string
import abc
import typing
import time
import random


class Observer(abc.ABC):

    @abc.abstractclassmethod
    def update(self) -> typing.NoReturn:
        pass


def get_sgf(cid: str) -> str:
    url: str = "https://h5.foxwq.com/yehuDiamond/chessbook_local/YHWQFetchChess?chessid=" + cid

    loop = True
    while loop:
        try:
            time.sleep(random.uniform(0.2, 0.6))
            with urlopen(url) as s:
                data = json.load(s)
            loop = False
        except Exception as e:
            time.sleep(random.uniform(3.4, 5.9))

    return data["chess"]

# def test():
#     print(get_sgf("1709456184010001396"))


def get_file_name(game: dict[str, str|int]) -> str:
    result = ""

    if game["blackenname"][0] in string.ascii_letters:
        black_player = game["blacknick"]
    else:
        black_player = game["blackenname"]

    if game["whiteenname"][0] in string.ascii_letters:
        white_player = game["whitenick"]
    else:
        white_player = game["whiteenname"]

    black_player = black_player.replace('/', '')
    white_player = white_player.replace('/', '')
    date = game["endtime"][:10]
    match game["winner"]:
        case 0:
            return "".join((date, "_[", black_player, "]vs[", white_player, "]_", "和棋", ".sgf"))
        case 1:
            result += "黑"
            winner = black_player
            loser = white_player
        case 2:
            result += "白"
            winner = white_player
            loser = black_player

    game_point = game["point"]
    if game_point == -1:
        result += "中盤勝"
    elif game_point == -2:
        result += "超時勝"
    else:
        if game["rule"] == 0:
            result += str(game_point / 100) + "目勝"
        else:
            result += str(game_point / 100) + "子勝"
    

    return "".join((date, "_[", winner, "]", result, "[", loser, "].sgf"))


class Downloader:

    def __init__(self, start_date: datetime.date, end_date: datetime.date, dir_path: str, game_type: str):
        self.start_date = start_date
        self.end_date = end_date
        self.dir_path = dir_path
        self.observer_list: collections.deque[Observer] = collections.deque(())
        self.game_type = game_type
        self.__state: str

    def notify(self):
        for observer in self.observer_list:
            observer.update()

    def append_observer(self, observer: Observer) -> typing.NoReturn:
        self.observer_list.append(observer)

    def get_state(self) -> str:
        return self.__state

    def run(self):
        url = "https://h5.foxwq.com/yehuDiamond/chessbook_local/YHWQFetchChessList?type=" + self.game_type
        game_list: collections.deque[dict] = collections.deque([])

        curr_url = url
        loop = True
        while loop:
            with urlopen(curr_url) as s:
                data: list[str] = json.load(s)["chesslist"]

            if len(data) == 0:
                break
            if self.end_date >= datetime.date.fromisoformat(data[-1]["endtime"][:10]):
                for d in data:
                    if self.start_date <= datetime.date.fromisoformat(d["endtime"][:10]):
                        if self.end_date >= datetime.date.fromisoformat(d["endtime"][:10]):
                            self.__state = get_file_name(d)
                            with open(os.path.join(self.dir_path, self.__state), encoding="utf-8", mode="w") as f:
                                f.write(get_sgf(d["chessid"]))
                            self.notify()
                    else:
                        loop = False
                        break
            curr_url = url + "&lastCode=" + data[-1]["chessid"]
