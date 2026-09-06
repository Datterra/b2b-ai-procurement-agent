import os
import json
from anthropic import Anthropic


# 1. Инициализируем клиента безопасно через переменную окружения
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


# 1. Инициализируем клиента (Вставьте ваш ключ здесь)
# client = Anthropic (api_key="ВАШ_КЛЮЧ_ЖЕЗ_sk-ant-...")


# Наша складская база данных (B2B Inventory)
INVENTORY_DB = {
    "стальная труба 50мм": {"status": "в наличии", "quantity": 150, "price_eur": 25.0},
    "медный фитинг": {"status": "мало", "quantity": 12, "price_eur": 4.5},
    "пластиковый разводчик": {"status": "нет на складе", "quantity": 0, "price_eur": 12.0}
}


# 2. Функция проверки склада
def check_inventory(item_name: str) -> str:
    print (f"📦 [Система]: Вызвана функция check_inventory для товара: '{item_name}'")
    item_lower = item_name.lower ()

    for key, data in INVENTORY_DB.items ():
        if key in item_lower or item_lower in key:
            return json.dumps ({
                "item": key,
                "status": data["status"],
                "available_stock": data["quantity"],
                "price_per_unit": data["price_eur"]
            }, ensure_ascii=False)

    return json.dumps ({"error": f"Товар '{item_name}' не найден в каталоге."}, ensure_ascii=False)


# Входящее письмо (2 товара)
raw_buyer_email = "Привет! Нам нужно 20 стальных труб 50мм и 15 медных фитингов. Срочно!"

# 3. Спецификация инструмента
tools_specification = [
    {
        "name": "check_inventory",
        "description": "Checks the real-time stock availability and unit price for a specific B2B component by its name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "The name of the material or part to check (e.g., 'стальная труба 50мм')"
                }
            },
            "required": ["item_name"]
        }
    }
]

print ("⏳ Шаг 1: Отправляем запрос клиента в Claude 3.5 Sonnet...")

# 4. Первый вызов API
response = client.messages.create (
    model="claude-sonnet-4-6",
    max_tokens=1000,
    system="You are an elite B2B platform agent. You MUST use tools to verify inventory for EACH item mentioned before answering.",
    tools=tools_specification,
    messages=[{"role": "user", "content": raw_buyer_email}]
)

# 5. Проверяем вызовы инструментов
if response.stop_reason == "tool_use":
    print ("🤖 [Claude]: Решил проверить данные по складу...")

    # Собираем ответы для ВСЕХ вызовов инструментов, которые сгенерировал Claude
    tool_results_blocks = []

    for block in response.content:
        if block.type == "tool_use":
            tool_name = block.name
            tool_input = block.input
            tool_id = block.id

            print (f"👉 Запуск инструмента '{tool_name}' для параметров: {tool_input}")

            if tool_name == "check_inventory":
                result_str = check_inventory (tool_input["item_name"])

                # Формируем блок результата в строгом соответствии с API Anthropic
                tool_results_blocks.append ({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": result_str
                })

    # 6. Финальный вызов API — передаем ВСЕ результаты работы инструментов
    print ("⏳ Шаг 2: Передаем собранные данные обратно в Claude для анализа дефицита...")
    final_response = client.messages.create (
        model="claude-sonnet-4-6",
        max_tokens=1000,
        system=(
            "You are an AI B2B Platform Manager. Review the tool execution data. "
            "CRITICAL BUSINESS RULE: If the customer requests MORE than what is available in 'available_stock', "
            "you must explicitly inform them about the shortage for that specific item, offer to ship the available amount immediately, "
            "and propose options. Be professional and transaction-oriented."
        ),
        tools=tools_specification,
        messages=[
            {"role": "user", "content": raw_buyer_email},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": tool_results_blocks  # Передаем массив со всеми ответами
            }
        ]
    )

    print ("\n🏁 Финальный ответ ИИ-агента для клиента:")
    print (final_response.content[0].text)
else:
    print ("\nИИ ответил напрямую:")
    print (response.content[0].text)
