from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from .models import User
from django.http import parse_cookie

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


class MySyncConsumer(JsonWebsocketConsumer):
    channel_values = {}

    def connect(self):
        self.roomname = self.scope['url_route']['kwargs']['roomname']

        if self.roomname not in self.channel_values.keys():
            self.channel_values[self.roomname] = {}

        cookies = getcookie(self.scope)
        print('coll',cookies)

        if len(cookies):
            if len(self.channel_values[self.roomname]) < 2 and cookies['jwt'] not in self.channel_values[self.roomname].keys():
                self.channel_values[self.roomname][cookies['jwt']] = self.assign_value(self.roomname)

        async_to_sync(self.channel_layer.group_add)(self.roomname,self.channel_name)

        self.accept()

        room = User.objects.filter(username = self.roomname).first()

        if room is None:
            return
        
        self.send_json({
            'type': 'connection.message',
            'moves': room.moves,
            'scores': room.scores
        })

    def receive_json(self,content,**kwargs):

        room = User.objects.filter(username = content['room']).first()

        cookies = getcookie(self.scope)

        if len(cookies):
            if len(self.channel_values[self.roomname]) < 2 and cookies['jwt'] not in self.channel_values[self.roomname].keys():
                self.channel_values[self.roomname][cookies['jwt']] = self.assign_value(self.roomname)

        res = {
            'type': None,
            'data': content,
            'ok': True,
            'action': content['action'],
            'won': 'none'
        }

        if content['action'] == 'move':
            
            if self.channel_values[self.roomname][cookies['jwt']] != content['turn']:
                res['ok'] = False

            else:
                if content['id'] not in room.moves.keys():
                    room.undo_stack.append(content['id'])
                    room.moves[content['id']] = content['turn']
                else:
                    res['ok'] = False

                if 'lastTurn' not in room.moves.keys():
                    room.moves['lastTurn'] = content['turn']
                
                else:
                    room.moves['lastTurn'] = content['turn']

        elif content['action'] == 'undo':
            id = room.undo_stack.pop()
            content['id'] = id
            if id in room.moves.keys():
                del room.moves[id]
                room.moves['lastTurn'] = 'X' if room.moves['lastTurn'] == 'O' else 'O'

        elif content['action'] == 'reset':
            room.undo_stack = []
            room.moves = {}

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
    
    def assign_value(self, rmname):
        d = self.channel_values.get(rmname, {})
        if len(d) == 0:
            return 'O'
        elif len(d) == 1:
            for key in d.keys():
                if d[key] == 'O':
                    return 'X'
                else:
                    return 'O'