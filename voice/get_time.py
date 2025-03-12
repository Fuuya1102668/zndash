import datetime

def get_time():
    now = datetime.datetime.now()
    return [now.month, now.day, now.hour, now.minute]

if __name__=="__main__":
    print(get_time())
