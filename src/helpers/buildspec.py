import yaml


class BuildSpecHelper:
    @staticmethod
    def get_buildspec(file_location: str):
        with open(file_location, "r") as buildspec_file:
            return yaml.load(buildspec_file.read(), Loader=yaml.FullLoader)
