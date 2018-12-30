import pika
import json
from time import sleep
from .settings import AMQP_SETTINGS

class AMQPPublisher(object):
    """
        This will establish a connection to a RabbitMQ instance.
        It will allow communication witht the biojs-builder module (https://github.com/biojs/biojs-builder)
        to get browserified packages of components where they are needed
        for example visualisations.
    """

    EXCHANGE = AMQP_SETTINGS['exchange']
    QUEUE = AMQP_SETTINGS['queue']
    ROUTING_KEY = AMQP_SETTINGS['routing_key']

    def __init__(self):
        self._connection = None
        self._channel = None
        self._url = AMQP_SETTINGS['url']

        # self._deliveries = None
        # self._acked = None
        # self._nacked = None

    def connect(self):
        print('Connecting to AMQP host %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                    on_open_callback=self.on_connection_open,
                                    on_close_callback=self.on_connection_closed,
                                    stop_ioloop_on_close=False)

    def on_connection_open(self, unused_connection):
        """

        :type unused_connection: pika.SelectConnection

        """
        print('Connection opened')
        self.open_channel()

    def on_connection_closed(self, connection, reply_code, reply_text):
        """

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        print('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
        self._connection.add_timeout(5, self._connection.ioloop.stop)

    def open_channel(self):

        print('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """

        :param pika.channel.Channel channel: The channel object

        """
        print('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(AMQP_SETTINGS['exchange'])

    def add_on_channel_close_callback(self):
        print('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """

        :param pika.channel.Channel channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        print('Channel was closed: (%s) %s', reply_code, reply_text)
        self._channel = None
        self._connection.close()

    def setup_exchange(self, exchange_name):
        """

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        print('Declaring exchange %s', exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       exchange_name,
                                       AMQP_SETTINGS['exchange_type'])

    def on_exchange_declareok(self, unused_frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """
        print('Exchange declared')
        self.setup_queue(AMQP_SETTINGS['queue'])

    def setup_queue(self, queue_name):
        """

        :param str|unicode queue_name: The name of the queue to declare.

        """
        print('Declaring queue %s', queue_name)
        self._channel.queue_declare(self.on_queue_declareok, queue_name)

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        print('Binding %s to %s with %s', self.QUEUE, self.EXCHANGE, self.ROUTING_KEY)
        self._channel.queue_bind(self.on_bindok, self.QUEUE, self.EXCHANGE, self.ROUTING_KEY)

    def on_bindok(self, unused_frame):
        """This method is invoked by pika when it receives the Queue.BindOk
        response from RabbitMQ. Since we know we're now setup and bound, it's
        time to start publishing."""
        # self.enable_delivery_confirmations()
        print('Queue bound - ready to publish')
        return

    def stop(self):
        print('Stopping')
        self._stopping = True
        self.close_channel()
        self.close_connection()

    def close_channel(self):
        """Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.

        """
        if self._channel is not None:
            print('Closing the channel')
            self._channel.close()

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        if self._connection is not None:
            print('Closing connection')
            self._connection.close()

    def publish(self, message_payload):
        print('Publishing %s', json.dumps(message_payload))
        # self._connection = self.connect()
        # self._channel.basic_publish(self.EXCHANGE, self.ROUTING_KEY,
                                    # json.dumps(message_payload))
        # return self._connection
        # self._connection.ioloop.start()

        parameters = pika.URLParameters(self._url)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.basic_publish(self.EXCHANGE,
                          self.ROUTING_KEY,
                          json.dumps(message_payload),
                          pika.BasicProperties(content_type='application/json',
                                               delivery_mode=1))
        connection.close()
