from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from .models import Room
from django.http import parse_cookie
from datetime import datetime

def getcookie(scope):
        headers = scope.get('headers', [])
        cookies = {}
        for header_key, header_value in headers:
            if header_key == b'cookie':
                cookies.update(parse_cookie(header_value.decode('utf-8')))
        
        return cookies

def winCheck(board, player):
    winning_combinations = [
        # Rows
        ['1st', '2nd', '3rd'],
        ['4th', '5th', '6th'],
        ['7th', '8th', '9th'],
        # Columns
        ['1st', '4th', '7th'],
        ['2nd', '5th', '8th'],
        ['3rd', '6th', '9th'],
        # Diagonals
        ['1st', '5th', '9th'],
        ['3rd', '5th', '7th']
    ]
    flag = False
    for combo in winning_combinations:
        flag = True
        for position in combo:
            if position not in board.keys():
                flag = False
                break
            elif board[position] != player:
                flag = False
                break
        if flag:
            return True
    return False

def add_message(username,message,messages):
    timestamp = datetime.now()
    messages.append({
        'username': username,
        'message': message,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
    })
    messages = sorted(messages, key=lambda x: x['timestamp'])
    return messages

class MySyncConsumer(JsonWebsocketConsumer):

    def connect(self):
        self.roomname = self.scope['url_route']['kwargs']['roomname']
        self.username = self.scope['url_route']['kwargs']['name']

        async_to_sync(self.channel_layer.group_add)(self.roomname,self.channel_name)

        self.accept()

        room = Room.objects.filter(username = self.roomname).first()

        if room is None:
            return
        
        if len(room.users) == 0:
            room.delete()
            return
        
        self.send_json({
            'type': 'connection.message',
            'moves': room.moves,
            'scores': room.scores,
            'msges': room.messages,
            'name': self.username,
            'users': room.users
        })

    def receive_json(self,content,**kwargs):

        room = Room.objects.filter(username = content['room']).first()

        timestamp = datetime.now()

        res = {
            'type': None,
            'data': content,
            'ok': True,
            'action': content['action'],
            'won': 'none',
            'reason': None,
            'timestamp':timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

        if content['action'] == 'move':

            if content['name'] not in room.turns.keys():
                res['ok'] = False
                res['reason'] = f"Invalid turn by {content['name']}! He/she can only chat!!"

            elif content['id'] in room.moves.keys():
                res['ok'] = False
                res['reason'] = f"Invalid turn by {content['name']}!"
            
            elif room.turns[content['name']] != content['turn']:
                res['ok'] = False
                res['reason'] = f"Invalid turn by {content['name']}!"

            else:
                if content['id'] not in room.moves.keys():
                    room.undo_stack.append(content['id'])
                    room.moves[content['id']] = content['turn']

                if 'lastTurn' not in room.moves.keys():
                    room.moves['lastTurn'] = content['turn']
                
                else:
                    room.moves['lastTurn'] = content['turn']

        elif content['action'] == 'undo':
            if len(room.undo_stack) != 0:
                id = room.undo_stack.pop()
                content['id'] = id
                if id in room.moves.keys():
                    del room.moves[id]
                    room.moves['lastTurn'] = 'X' if room.moves['lastTurn'] == 'O' else 'O'

        elif content['action'] == 'reset':
            room.undo_stack = []
            room.moves = {}

        elif content['action'] == 'chat':
            room.messages = add_message(content['name'],content['msg'],room.messages)

        elif content['action'] == 'leave':
            if content['name'] in room.turns.keys():
                res['reason'] = 'reset'
                turn = room.turns[content['name']]
                idx = room.users.index(content['name']) + 1
                if idx != len(room.users):
                    if room.users[idx] in room.turns.keys():
                        idx += 1
                        if idx != len(room.users):
                            room.turns[room.users[idx]] = turn    
                    else:
                        room.turns[room.users[idx]] = turn
                del room.turns[content['name']]
            room.users.remove(content['name'])
            room.save()

        if winCheck(room.moves,'O'):
            res['won'] = 'O'
            room.scores['O'] += 1
        elif winCheck(room.moves,'X'):
            res['won'] = 'X'
            room.scores['X'] += 1
        elif len(room.moves) == 10:
            res['won'] = 'draw'

        res['type'] = 'game.play'
                    
        room.save()
        async_to_sync(self.channel_layer.group_send)(self.roomname,res)
    
    def game_play(self,event):
        self.send_json(event)

    def disconnect(self,close_code):
        async_to_sync(self.channel_layer.group_discard(self.roomname,self.channel_name))
        raise StopConsumer