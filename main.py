
from application import app,socketio

if __name__=="__main__":
    socketio.run(app, debug=True,port=5050)