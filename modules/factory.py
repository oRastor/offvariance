from xgclient.client import ExpectedGoalsClient, Type


def create_client(config):
    rapid_key = config.get('RAPID_KEY')
    off_variance_key = config.get('OFF_VARIANCE_KEY')

    if rapid_key and len(rapid_key):
        return ExpectedGoalsClient(rapid_key)

    if off_variance_key and len(off_variance_key):
        return ExpectedGoalsClient(off_variance_key, api_type=Type.DIRECT)

    print("Please specify API key")
    exit(1)
