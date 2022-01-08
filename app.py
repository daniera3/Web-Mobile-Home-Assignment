from flask import Flask, request, escape
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from datetime import datetime

db_connect = create_engine('sqlite:///ProjectDB.db')
app = Flask(__name__)
api = Api(app)


@app.route('/')
def index():
    return "wellcome to message app"


class writeMassge(Resource):
    def post(self):
        try:
            sender = escape(request.json.get('sender'))
            receiver = escape(request.json.get('receiver'))
            message = escape(request.json.get('message'))
            subject = escape(request.json.get('subject'))
            conn = db_connect.connect()
            conn.execute("insert into message (sender, receiver, subject, message, date) values(?, ?, ?, ?, ?)",
                         (sender, receiver, subject, message, datetime.now()))
            return {'info': "message saved"}, 201
        except:
            return {'info': "ERROR, sorry we can save your message new try agine later"}, 500


class messagePerUser(Resource):
    def get(self):
        try:
            receiver = escape(request.args.get('receiver', default='', type=str))
            conn = db_connect.connect()
            res = conn.execute("SELECT *  FROM message WHERE receiver = ?",
                               (receiver))
            conn.execute("UPDATE message SET read = ? WHERE receiver = ?", (1, receiver))
            des = []
            for row in res:
                messageId = row['messageId']
                sender = row['sender']
                receiver = row['receiver']
                subject = row['subject']
                message = row['message']
                date = row['date']
                des.append({'messageId': messageId, 'sender': sender, 'receiver': receiver, 'message': message,
                            'subject': subject, 'date': date})
            return {'info': "Get message success", 'data': des}, 200
        except:
            return {'info': "ERROR, sorry we can get your message new"}, 500


class messagePerUserUnread(Resource):
    def get(self):
        try:
            receiver = escape(request.args.get('receiver', default='', type=str))
            conn = db_connect.connect()
            res = conn.execute("SELECT * FROM message WHERE receiver = ? AND read = ?", (receiver, 0))
            conn.execute("UPDATE message SET read = ? WHERE receiver = ? AND read = ?", (1, receiver, 0))
            des = []
            for row in res:
                messageId = row['messageId']
                sender = row['sender']
                receiver = row['receiver']
                subject = row['subject']
                message = row['message']
                date = row['date']
                des.append({'messageId': messageId, 'sender': sender, 'receiver': receiver, 'message': message,
                            'subject': subject, 'date': date})
            return {'info': "Get message success", 'data': des}, 200
        except:
            return {'info': "ERROR, sorry we can get your message new"}, 500


class readmessage(Resource):
    def get(self):
        try:
            receiver = escape(request.args.get('receiver', default='', type=str))
            conn = db_connect.connect()
            res = conn.execute("SELECT * FROM message WHERE receiver = ? AND read = ?", (receiver, 0))
            message = False
            for row in res:
                messageId = row['messageId']
                sender = row['sender']
                receiver = row['receiver']
                subject = row['subject']
                message = row['message']
                date = row['date']
                message = {'messageId': messageId, 'sender': sender, 'receiver': receiver, 'message': message,
                           'subject': subject, 'date': date}
                break
            if message:
                conn.execute("UPDATE message SET read = ? WHERE messageId = ? ", (1, message.get('messageId')))
            else:
                return {'info': "User read all has message"}, 200
            return {'info': "Get message success", 'data': message}, 200
        except:
            return {'info': "ERROR, sorry we can get your message new"}, 500


class deletemessage(Resource):
    def delete(self):
        try:
            messageId = escape(request.json.get('messageId'))
            user = escape(request.json.get('user'))
            conn = db_connect.connect()
            res = conn.execute("DELETE FROM message where messageId = ? AND (receiver = ? OR sender = ? )",
                               (messageId, user, user))
            if res.rowcount:
                return {'info': "Message with message id {} success deleted".format(messageId)}, 202
            return {'info': "Message with message id {} and sender or receiver {} not detect".format(messageId,
                                                                                                     user)}, 200
        except:
            return {'info': "ERROR, sorry cant delete this message"}, 500


api.add_resource(writeMassge, '/message', methods={'POST'})  # create new message
api.add_resource(messagePerUser, '/message', methods={'GET'})  # get all message sent to user
api.add_resource(messagePerUserUnread, '/messageUnread', methods={'GET'})  # get all message sent to user unread
api.add_resource(readmessage, '/readMessage', methods={'GET'})  # get one message sent to user unread
api.add_resource(deletemessage, '/deleteMessage', methods={'DELETE'})  # create new message

if __name__ == '__main__':
    app.run()
