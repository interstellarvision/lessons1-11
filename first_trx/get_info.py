import inquirer # type: ignore

class GetInfo:
    def __init__(self):
        pass

    def get_user_action():
        questions = [
            inquirer.List(
                "action",
                message="Что вы хотите сделать?",
                choices=["Swap", "Send"]
            )
        ]
        return inquirer.prompt(questions)

    def get_exchange_details():
        questions = [
            inquirer.List("from_currency", message="Выберите валюту, которую хотите обменять:", choices=["USDC", "ETH"]),
            inquirer.List("to_currency", message="Выберите валюту, которую хотите получить:", choices=["USDC", "ETH"]),
            inquirer.Text("amount", message="Введите сумму для обмена:")
        ]
        return inquirer.prompt(questions)

    def get_transfer_details():
        questions = [
            inquirer.List("currency", message="Выберите валюту для отправки:", choices=["USDC", "ETH"]),
            inquirer.Text("recipient", message="Введите адрес получателя:"),
            inquirer.Text("amount", message="Введите сумму для отправки:")
        ]
        return inquirer.prompt(questions)