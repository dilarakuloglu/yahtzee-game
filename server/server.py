#!/usr/bin/env python3
"""
Yahtzee Sunucu Uygulaması
Konsol tabanlı, TCP socket ile çok istemcili destek
"""

import socket
import threading
import json
import random
import time
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5555
MAX_PLAYERS = 2

CATEGORIES = [
    "ones", "twos", "threes", "fours", "fives", "sixes",
    "three_of_a_kind", "four_of_a_kind", "full_house",
    "small_straight", "large_straight", "yahtzee", "chance"
]

CATEGORY_NAMES = {
    "ones": "Birler", "twos": "İkiler", "threes": "Üçler",
    "fours": "Dörder", "fives": "Beşler", "sixes": "Altılar",
    "three_of_a_kind": "3'lü Dizi", "four_of_a_kind": "4'lü Dizi",
    "full_house": "Full House", "small_straight": "Küçük Seri",
    "large_straight": "Büyük Seri", "yahtzee": "Yahtzee", "chance": "Şans"
}


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")


def calculate_score(category, dice):
    counts = [dice.count(i) for i in range(1, 7)]
    total = sum(dice)

    if category == "ones":   return dice.count(1) * 1
    if category == "twos":   return dice.count(2) * 2
    if category == "threes": return dice.count(3) * 3
    if category == "fours":  return dice.count(4) * 4
    if category == "fives":  return dice.count(5) * 5
    if category == "sixes":  return dice.count(6) * 6

    if category == "three_of_a_kind":
        return total if max(counts) >= 3 else 0
    if category == "four_of_a_kind":
        return total if max(counts) >= 4 else 0
    if category == "full_house":
        return 25 if (3 in counts and 2 in counts) else 0
    if category == "small_straight":
        s = set(dice)
        if {1,2,3,4}.issubset(s) or {2,3,4,5}.issubset(s) or {3,4,5,6}.issubset(s):
            return 30
        return 0
    if category == "large_straight":
        s = set(dice)
        if s == {1,2,3,4,5} or s == {2,3,4,5,6}:
            return 40
        return 0
    if category == "yahtzee":
        return 50 if max(counts) == 5 else 0
    if category == "chance":
        return total
    return 0


class GameRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = []       # [(conn, addr, name), ...]
        self.scores = {}        # name -> {category: score}
        self.current_turn = 0
        self.dice = [1, 1, 1, 1, 1]
        self.rolls_left = 3
        self.kept = [False] * 5
        self.game_started = False
        self.game_over = False
        self.lock = threading.Lock()

    def add_player(self, conn, addr, name):
        self.players.append((conn, addr, name))
        self.scores[name] = {}
        log(f"Oda {self.room_id}: '{name}' katıldı ({len(self.players)}/{MAX_PLAYERS})")

    def broadcast(self, message, exclude=None):
        data = json.dumps(message) + "\n"
        for conn, addr, name in self.players:
            if exclude and conn == exclude:
                continue
            try:
                conn.sendall(data.encode())
            except:
                pass

    def send_to(self, conn, message):
        data = json.dumps(message) + "\n"
        try:
            conn.sendall(data.encode())
        except:
            pass

    def current_player(self):
        return self.players[self.current_turn % len(self.players)]

    def start_game(self):
        if len(self.players) < MAX_PLAYERS:
            return
        self.game_started = True
        self.scores = {p[2]: {} for p in self.players}
        self.rolls_left = 3
        self.kept = [False] * 5
        self.dice = [random.randint(1, 6) for _ in range(5)]
        log(f"Oda {self.room_id}: Oyun başladı!")
        self.broadcast({
            "type": "game_start",
            "players": [p[2] for p in self.players],
            "current_player": self.current_player()[2]
        })
        self.send_turn_state()

    def send_turn_state(self):
        cp_conn, _, cp_name = self.current_player()
        state = {
            "type": "turn_state",
            "current_player": cp_name,
            "dice": self.dice,
            "kept": self.kept,
            "rolls_left": self.rolls_left,
            "scores": self.scores,
            "your_turn": False
        }
        for conn, addr, name in self.players:
            state["your_turn"] = (conn == cp_conn)
            self.send_to(conn, state)

    def handle_roll(self, conn, kept_indices):
        with self.lock:
            cp_conn, _, cp_name = self.current_player()
            if conn != cp_conn:
                self.send_to(conn, {"type": "error", "msg": "Sıra sizde değil!"})
                return
            if self.rolls_left <= 0:
                self.send_to(conn, {"type": "error", "msg": "Atış hakkınız kalmadı!"})
                return

            self.kept = [False] * 5
            for i in kept_indices:
                if 0 <= i < 5:
                    self.kept[i] = True

            for i in range(5):
                if not self.kept[i]:
                    self.dice[i] = random.randint(1, 6)

            self.rolls_left -= 1
            log(f"Oda {self.room_id}: {cp_name} zar attı → {self.dice}")
            self.send_turn_state()

    def handle_score(self, conn, category):
        with self.lock:
            cp_conn, _, cp_name = self.current_player()
            if conn != cp_conn:
                self.send_to(conn, {"type": "error", "msg": "Sıra sizde değil!"})
                return
            if category not in CATEGORIES:
                self.send_to(conn, {"type": "error", "msg": "Geçersiz kategori!"})
                return
            if category in self.scores[cp_name]:
                self.send_to(conn, {"type": "error", "msg": "Bu kategori zaten dolu!"})
                return

            score = calculate_score(category, self.dice)
            self.scores[cp_name][category] = score
            log(f"Oda {self.room_id}: {cp_name} → {CATEGORY_NAMES[category]}: {score} puan")

            # Sonraki tura geç
            self.current_turn += 1
            self.rolls_left = 3
            self.kept = [False] * 5
            self.dice = [random.randint(1, 6) for _ in range(5)]

            # Oyun bitti mi?
            all_done = all(
                len(self.scores[p[2]]) == len(CATEGORIES)
                for p in self.players
            )

            if all_done:
                self.end_game()
            else:
                self.broadcast({
                    "type": "score_update",
                    "player": cp_name,
                    "category": category,
                    "score": score,
                    "scores": self.scores
                })
                self.send_turn_state()

    def end_game(self):
        self.game_over = True
        totals = {}
        for name, cats in self.scores.items():
            upper = sum(cats.get(c, 0) for c in ["ones","twos","threes","fours","fives","sixes"])
            bonus = 35 if upper >= 63 else 0
            lower = sum(cats.get(c, 0) for c in CATEGORIES[6:])
            totals[name] = upper + bonus + lower

        winner = max(totals, key=totals.get)
        log(f"Oda {self.room_id}: Oyun bitti! Kazanan: {winner} ({totals[winner]} puan)")
        self.broadcast({
            "type": "game_over",
            "scores": self.scores,
            "totals": totals,
            "winner": winner
        })


class YahtzeeServer:
    def __init__(self):
        self.rooms = {}
        self.waiting_room = None
        self.lock = threading.Lock()

    def _join_room(self, conn, addr, name):
        with self.lock:
            if self.waiting_room and len(self.waiting_room.players) < MAX_PLAYERS:
                room = self.waiting_room
            else:
                room_id = len(self.rooms) + 1
                room = GameRoom(room_id)
                self.rooms[room_id] = room
                self.waiting_room = room
            room.add_player(conn, addr, name)
            should_start = len(room.players) == MAX_PLAYERS
            if should_start:
                self.waiting_room = None
            return room, should_start

    def _leave_room(self, room, conn, name):
        with self.lock:
            room.players = [(c, a, n) for c, a, n in room.players if c != conn]
            if not room.game_started and name in room.scores:
                del room.scores[name]
            if not room.players:
                if room.room_id in self.rooms:
                    del self.rooms[room.room_id]
                if self.waiting_room == room:
                    self.waiting_room = None
                log(f"Oda {room.room_id} kapatıldı.")

    def handle_client(self, conn, addr):
        log(f"Yeni bağlantı: {addr}")
        buffer = ""
        room = None
        player_name = None

        try:
            data = conn.recv(1024).decode()
            msg = json.loads(data.strip())
            if msg.get("type") != "join":
                conn.close()
                return

            player_name = msg.get("name", "Oyuncu")[:20]
            room, should_start = self._join_room(conn, addr, player_name)

            room.send_to(conn, {
                "type": "joined",
                "name": player_name,
                "room_id": room.room_id,
                "players": [p[2] for p in room.players],
                "waiting": not should_start
            })

            if should_start:
                room.start_game()
                if not room.game_started:
                    with self.lock:
                        self.waiting_room = room
                    room.broadcast({
                        "type": "waiting",
                        "players": [p[2] for p in room.players],
                        "msg": "Bir oyuncu bağlantısı kesildi. Yeni oyuncu bekleniyor..."
                    })
            else:
                room.broadcast({
                    "type": "waiting",
                    "players": [p[2] for p in room.players],
                    "msg": f"{player_name} bekleme odasına katıldı. {MAX_PLAYERS - len(room.players)} oyuncu bekleniyor..."
                }, exclude=conn)

            while True:
                chunk = conn.recv(4096).decode()
                if not chunk:
                    break
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    try:
                        msg = json.loads(line)
                        mtype = msg.get("type")
                        if mtype == "roll":
                            room.handle_roll(conn, msg.get("kept", []))
                        elif mtype == "score":
                            room.handle_score(conn, msg.get("category", ""))
                        elif mtype == "restart":
                            self.handle_restart(room, conn, player_name)
                    except json.JSONDecodeError:
                        pass

        except Exception as e:
            log(f"Hata ({addr}): {e}")
        finally:
            log(f"Bağlantı kapandı: {addr} ({player_name})")
            if room and player_name:
                if room.game_started and not room.game_over:
                    room.game_over = True
                    room.broadcast({
                        "type": "player_left",
                        "name": player_name,
                        "msg": f"{player_name} oyundan ayrıldı. Oyun sona erdi."
                    }, exclude=conn)
                else:
                    room.broadcast({
                        "type": "player_left",
                        "name": player_name,
                        "msg": f"{player_name} lobiden ayrıldı."
                    }, exclude=conn)
                self._leave_room(room, conn, player_name)
                if not room.game_started and room.players:
                    room.broadcast({
                        "type": "waiting",
                        "players": [p[2] for p in room.players],
                        "msg": "Yeni oyuncu bekleniyor..."
                    })
            conn.close()

    def handle_restart(self, room, conn, player_name):
        with room.lock:
            if not hasattr(room, 'restart_votes'):
                room.restart_votes = set()
            room.restart_votes.add(player_name)
            room.broadcast({
                "type": "restart_vote",
                "voter": player_name,
                "count": len(room.restart_votes),
                "needed": MAX_PLAYERS
            })
            if len(room.restart_votes) == MAX_PLAYERS:
                room.restart_votes = set()
                room.scores = {p[2]: {} for p in room.players}
                room.current_turn = 0
                room.game_over = False
                room.start_game()

    def run(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(10)
        log(f"Yahtzee Sunucusu başlatıldı → {HOST}:{PORT}")
        log(f"Maksimum oyuncu/oda: {MAX_PLAYERS}")
        log("Bağlantı bekleniyor...\n")

        try:
            while True:
                conn, addr = server_sock.accept()
                t = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                t.start()
        except KeyboardInterrupt:
            log("Sunucu kapatılıyor...")
        finally:
            server_sock.close()


if __name__ == "__main__":
    YahtzeeServer().run()
