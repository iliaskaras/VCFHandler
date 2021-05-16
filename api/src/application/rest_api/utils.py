from collections import OrderedDict


class ETagManager:

    @staticmethod
    def generate_etag(with_quotes: bool = False, **kwargs) -> str:
        """
        Generates an ETag using the provided kwargs. This method is also used for generating
        the ETag with quotes, for verifying the ETag.

        The generated ETag have the following format:
        With quotes - For checking ETag:        '"<param1>=<value1>&<param2>=<value2>&<param3>=<value3>"'
        Without quotes - For generating ETag:   '<param1>=<value1>&<param2>=<value2>&<param3>=<value3>'

        :param with_quotes: If we want to generate ETag string with quotes, useful when we are checking
        the ETag, because it is passed with the quotes.
        :param kwargs: The kwargs that will be used to format the ETag.
        :return:
        """
        ordered_kwargs: OrderedDict = OrderedDict(sorted(kwargs.items()))
        etag = "&".join(["{}={}".format(k, v) for k, v in ordered_kwargs.items()])

        if with_quotes:
            etag = '"%s"' % etag

        return etag
