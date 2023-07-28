import unittest
from unittest.mock import patch, Mock

from src.main.python.de.gbdmp.streaming_data_generator.Generator import produce_message

class TestMyKafkaProducer(unittest.TestCase):
    """
    Test the Kafka Producer
    """
    @patch('src.main.python.de.gbdmp.streaming_data_generator.Generator.produce_message')
    def test_produce_message(self, mock_produce_message):
        """
        Test the produce_message method
        """
        mock_produce_message.return_value = "test"
        self.assertEqual(produce_message(), "test")
