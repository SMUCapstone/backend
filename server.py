from youtubeAPI import youtubeAPI
import Database as db
import pika

class Consumer:
    def __init__(self):
        self.__url = '34.64.56.32'
        self.__port = 5672
        self.__vhost = 'youthat'
        self.__cred = pika.PlainCredentials('admin', 'capstoneVPC')
        self.__queue = 'pre-collect'

    def on_message(channel, method_frame, header_frame, recognize):
        recognize = str(recognize, 'utf-8')
        yt_url = db.search_request_state(recognize)
        print("message received 1", yt_url)
        video_id = yt_url.split('watch?v=')[-1]
        yt.get_comment_and_likes(recognize, video_id)
        print('finished')

    def consume(self):
        conn = pika.BlockingConnection(pika.ConnectionParameters(self.__url, self.__port, self.__vhost, self.__cred))
        chan = conn.channel()
        chan.basic_consume(
            queue = self.__queue, 
            on_message_callback = Consumer.on_message,
            auto_ack = True
        )
        chan.start_consuming()
        return


yt = youtubeAPI('발급받은 api키')
consumer = Consumer()
consumer.consume()