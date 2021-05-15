from argparse import ArgumentParser

from application.factories import vcf_handler_api
from application.infrastructure.configurations.models import Configuration

if __name__ == "__main__":
    argument_parser = ArgumentParser(description="VCF Handler API")

    argument_parser.add_argument(
        "--host",
        dest="host",
        type=str,
        default="127.0.0.1",
        help="The IP on which the application will bind.",
    )

    argument_parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=8000,
        help="The port on which the application will bind.",
    )

    arguments = argument_parser.parse_args()

    # Initialize the configuration instance.
    configuration = Configuration.initialize()

    vcf_handler_api(
        name="VCF Handler API",
        configuration=configuration,
    ).run(host=arguments.host, port=arguments.port)
