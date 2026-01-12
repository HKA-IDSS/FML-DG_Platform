from util.Util import arg_parser

server_args = arg_parser("TrainingConfiguration.yaml")
client_id_address_dict: dict = {}
last_client_number: int = 0
