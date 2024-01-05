#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import PythonCommand, ImageProcPythonCommand
from Commands.Keys import KeyPress, Button, Direction, Stick, Hat
import time

# 洞窟に移動→放置狩り→リーグ部移動→道具プリンターを繰り返します

# 放置狩り
# シンクロしてひたすらぐるぐる
# 約10秒ごとに時間チェックして、指定時間を超えてれば終了

# 道具プリンター
# 道具プリンター10連を指定回数実行します
# 道具選択はおまかせモード
# （おまかせモードの場合、持っている数が多いものから使用される）

# BPかおとしものが足りなくなれば強制終了
# BP稼ぎ要素は入っていないのでBPは十分用意しておいてください

# 設定目安
# 電気石の岩窟の場合、1時間でだいたい10連16-17回分の落とし物が集まります
# （レックウザ使用）

class WS(ImageProcPythonCommand):
    NAME = 'SV_道具プリンター&放置狩り_v0.9.0'

    def __init__(self,cam):
        super().__init__(cam)

        # -----------------------------------------------------
        # ↓↓↓ 設定ここから ↓↓↓
        # -----------------------------------------------------

        # プリンター10連を何回実行するか.
        # -1にするとBPかおとしものが無くなるまで実行.
        self.maxCount = 16*5

        # シンクロ狩りで放置する時間.
        self.maxMinute = 60*5

        # 繰り返し回数.
        self.maxRepeat = 3

        # レアボールチャンスの結果をスクショするか.
        self.isRareBallCapture = True

        # -----------------------------------------------------
        # ↑↑↑ 設定ここまで ↑↑↑
        # -----------------------------------------------------

    def do(self):
        print("-------------------------------------------------")
        print(f"シンクロ放置時間：{self.maxMinute}分")
        print(f"道具プリント実行回数：{self.maxCount}回")
        print(f"繰り返し回数：{self.maxRepeat}回")
        print("-------------------------------------------------")
        for i in range(self.maxRepeat):
            print("-------------------------------------------------")
            print(f"{i+1}回目")
            print("-------------------------------------------------")
            self.GoToElectricCave()
            self.SynchroHunting()
            self.GoToLeague()
            self.ItemPrinter()

    def GoToElectricCave(self):
        print("< 電気石の岩窟へ移動 >")
        self.press(Button.Y, wait=3.5)
        self.press(Direction.RIGHT, duration=5.0)
        self.press(Direction.DOWN, duration=5.0)
        self.press(Direction.LEFT, duration=3.5)
        self.press(Direction.UP, duration=2.3)
        self.wait(0.6)
        durationTimeLeft = 3.5
        durationTimeUp = 2.3
        count = 0
        while not self.isContainTemplate("SV/ItemPrinterAndLeaveHunt/FlySky.png", 0.83):
            print(f"Left:{durationTimeLeft}, Up:{durationTimeUp}")
            self.press(Direction.RIGHT, duration=5.0)
            self.press(Direction.DOWN, duration=5.0)
            self.press(Direction.LEFT, duration=durationTimeLeft)
            self.press(Direction.UP, duration=durationTimeUp)
            self.wait(0.6)
            if count % 2 == 0:
                durationTimeUp += 0.1
            else:
                durationTimeLeft += 0.1
            count += 1
        # そらをとぶ
        self.press(Button.A, wait=0.5)
        self.press(Button.A, wait=1.5)
        self.press(Button.A, wait=0.5)
        self.press(Button.A, wait=0.5)  # 入力抜け防止
        # 移動待ち
        self.wait(5.0)
        print("  移動完了待ち")
        while not self.isContainTemplate('SV/ItemPrinterAndLeaveHunt/menu_R.png', threshold=0.8, use_gray=True, show_value=False):
            self.press(Button.X, wait=1.0)
        self.press(Button.X, wait=2.5)
        self.press(Button.L, wait=0.5)
        self.press(Button.L, wait=1.0)  # 入力抜け防止
        self.press(Direction.UP, duration=1.0)

    def SynchroHunting(self):
        print("< シンクロで放置狩り >")
        self.press([Button.L, Button.R], 1.5)
        self.wait(7.0)

        # ぐるぐる回る
        self.press(Direction.UP, 4.5)   # 下に落ちておく
        self.startTime = time.time()
        self.press(Direction(Stick.RIGHT, 270), 0.5)
        self.hold([Direction(Stick.LEFT, 0), Direction(Stick.RIGHT, 180)])
        isSynchro = True
        while True:
            self.press(Button.LCLICK, 0.5)
            isBattle = False
            for i in range(10):
                if self.isContainTemplate('SV/ItemPrinterAndLeaveHunt/LostItem.png', threshold=0.8, use_gray=True, show_value=False):
                    isBattle = True
                if not self.isContainTemplate("SV/ItemPrinterAndLeaveHunt/Synchro.png", threshold=0.85):
                    isSynchro = False
                    break
                self.wait(0.5)
            # 10秒回って何も倒せなかったらちょっと前に進む
            if isBattle == False:
                self.holdEnd([Direction(Stick.LEFT, 0), Direction(Stick.RIGHT, 180)])
                self.press(Direction.UP, 1.0)
                self.hold([Direction(Stick.LEFT, 0), Direction(Stick.RIGHT, 180)])
            # 負けたりしてシンクロ解除されたら回復して再度シンクロする
            if isSynchro == False:
                print("  シンクロ解除された")
                self.holdEnd([Direction(Stick.LEFT, 0), Direction(Stick.RIGHT, 180)])
            # 経過時間チェック.
            self.nowTime = time.time()
            self.leaveMinute = int((self.nowTime - self.startTime) / 60)
            print(f"  経過時間：{self.leaveMinute}分{int((self.nowTime - self.startTime) % 60)}秒")
            if self.leaveMinute >= self.maxMinute:
                self.holdEnd([Direction(Stick.LEFT, 0), Direction(Stick.RIGHT, 180)])
                self.wait(0.5)
                print("-------------------------------------------------")
                print(f"指定時間が経過したのでシンクロ狩り終了します。")
                print(f"指定時間：{self.maxMinute}分, 経過時間：{self.leaveMinute}分{int((self.nowTime - self.startTime) % 60)}秒")
                print("-------------------------------------------------")
                break
            # 負けたりしてシンクロ解除されたら回復して再度シンクロする
            if isSynchro == False:
                print("  シンクロ再開")
                self.wait(3.0)
                while not self.isContainTemplate('SV/ItemPrinterAndLeaveHunt/menu_R.png', threshold=0.8, use_gray=True, show_value=False):
                    self.press(Button.X, wait=1.0)
                self.press(Direction.LEFT, 1.0, 0.5)
                self.press(Direction.UP, 2.0, 0.5)
                self.press(Button.MINUS, 0.5, 1.0)
                self.press(Button.X, wait=2.0)
                self.press([Button.L, Button.R], 1.5)
                self.wait(7.0)
                isSynchro = True
                self.press(Direction.UP, 4.5)   # 下に落ちておく
                self.press(Direction(Stick.RIGHT, 270), 0.5)
                self.hold([Direction(Stick.LEFT, 0), Direction(Stick.RIGHT, 180)])

        # シンクロ解除
        self.wait(1.0)
        self.press([Button.L, Button.R], 1.5)
        self.press(Button.A, wait=0.5)
        self.press(Button.A, wait=5.0)
        print("  シンクロ解除完了待ち")
        while not self.isContainTemplate('SV/ItemPrinterAndLeaveHunt/menu_R.png', threshold=0.8, use_gray=True, show_value=False):
            self.press(Button.X, wait=1.0)
        self.press(Button.X, wait=2.0)

    def GoToLeague(self):
        print("< リーグ部へ移動 >")
        self.press(Button.Y, wait=3.5)
        self.press(Direction.RIGHT, duration=5.0)
        self.press(Direction.DOWN, duration=5.0)
        self.press(Direction.LEFT, duration=0.4)
        self.press(Direction.UP, duration=0.4)
        self.wait(0.5)
        durationTimeLeft = 0.4
        durationTimeUp = 0.4
        count = 0
        while not self.isContainTemplate("SV/ItemPrinterAndLeaveHunt/FlySky.png", 0.83):
            self.press(Direction.RIGHT, duration=5.0)
            self.press(Direction.DOWN, duration=5.0)
            self.press(Direction.LEFT, duration=0.4)
            self.press(Direction.UP, duration=0.4)
            self.wait(0.5)
            if count % 2 == 0:
                durationTimeUp += 0.1
            else:
                durationTimeLeft += 0.1
            count += 1
        # そらをとぶ
        self.press(Button.A, wait=0.5)
        self.press(Button.A, wait=1.5)
        self.press(Button.A, wait=0.5)
        self.press(Button.A, wait=0.5)  # 入力抜け防止
        # 移動待ち
        self.wait(5.0)
        print("  移動完了待ち")
        while not self.isContainTemplate('SV/ItemPrinterAndLeaveHunt/menu_R.png', threshold=0.8, use_gray=True, show_value=False):
            self.press(Button.X, wait=1.0)
        self.press(Button.X, wait=2.0)
        self.press(Direction.RIGHT)
        self.press(Button.L, wait=0.5)
        self.press(Direction.UP, duration=0.6, wait=1.0)
        self.press(Direction.LEFT)
        self.press(Button.L, wait=0.5)
        self.press(Direction.UP, duration=1.5, wait=2.5)
        self.press(Direction.UP, wait=0.5)    # リーグ部選択
        self.press(Button.A, wait=8.0)
        print("  移動完了待ち")
        while not self.isContainTemplate('SV/ItemPrinterAndLeaveHunt/menu_R.png', threshold=0.8, use_gray=True, show_value=False):
            self.press(Button.X, wait=1.0)
        self.press(Button.X, wait=2.0)


    def ItemPrinter(self):
        print("< 道具プリンター開始 >")
        if self.maxCount == -1:
            print(f"  BPかおとしものが無くなるまで実行")
        else:
            print(f"  {self.maxCount}回実行")

        # 前に進んで話しかける
        self.press(Direction.UP, duration=1.0, wait=1.0)
        self.press(Button.A, wait=2.0)
        while not self.isContainTemplate('SV/ItemPrinterAndLeaveHunt/message.png', threshold=0.85):
            self.press(Direction.UP, duration=0.2, wait=1.0)
            self.press(Button.A, wait=2.0)
        self.press(Button.A, wait=1.0)
        self.press(Button.A, wait=3.0)

        if self.maxCount == -1:
            while True:
                self.ItemPrint10()
        else:
            for i in range(self.maxCount):
                self.ItemPrint10()

        self.press(Button.B, wait=1.0)
        self.press(Button.B, wait=3.0)
        print("< リーグ部からエントランスへ移動 >")
        self.press(Direction.DOWN, duration=3.0)
        self.wait(1.5)
        self.press(Button.A, wait=0.5)
        self.wait(8.0)
        print("  移動完了待ち")
        while not self.isContainTemplate('SV/ItemPrinterAndLeaveHunt/menu_R.png', threshold=0.8, use_gray=True, show_value=False):
            self.press(Button.X, wait=1.0)
        self.press(Button.X, wait=2.0)


    def ItemPrint10(self):
        # おとしもの選択
        while not self.isContainTemplate("SV/ItemPrinterAndLeaveHunt/bag.png", 0.85, True):
            self.wait(0.1)
        self.wait(1.5)
        self.press(Button.X, wait=0.5)
        self.press(Button.X, wait=2.0)  # 入力抜け防止
        self.press(Button.A, wait=0.5)
        self.press(Button.A, wait=1.0)
        self.wait(3.0)
        if self.isContainTemplate("SV/ItemPrinterAndLeaveHunt/bag.png", 0.85, True):
            print("  BPまたはおとしもの不足のため終了します")
            self.finish()

        # ハンドルを回す
        isRareBall = False
        while not self.isContainTemplate("SV/ItemPrinterAndLeaveHunt/Handle.png", 0.85, True):
            self.wait(0.1)
        if self.isContainTemplate("SV/ItemPrinterAndLeaveHunt/RareBall.png", 0.85, False):
            isRareBall = True
        self.press(Button.A)
        self.wait(10.0)
        while not self.isContainTemplate("SV/ItemPrinterAndLeaveHunt/Done.png", 0.85, True):
            self.wait(0.1)
        self.press(Button.A, wait=1.5)
        # ガチャ結果のキャプチャ
        if self.isRareBallCapture and isRareBall:
            self.camera.saveCapture()
        self.press(Button.A)
        self.wait(5.0)

