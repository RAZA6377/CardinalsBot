from termcolor import colored


class ColorPrint:
    @staticmethod
    def success(text: str):
        try:
            print(colored(text, "green", "on_black"))
        except Exception as e:
            print(f"Error in ColorPrint : {e}. Falling back to normal print")
            print(text)

    @staticmethod
    def failed(text: str):
        try:
            print(colored(text, "red", "on_black"))
        except Exception as e:
            print(f"Error in ColorPrint : {e}. Falling back to normal print")
            print(text)
