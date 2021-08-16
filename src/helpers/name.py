class NameHelper:
    @staticmethod
    def to_pascal_case(name: str) -> str:
        return "".join(char for char in name.title() if char.isalpha())
