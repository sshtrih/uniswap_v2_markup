# Uniswap V2 Indexer

Модульный индексатор для анализа данных Uniswap V2 на Ethereum.

## Быстрый старт

### 1. Установка

```bash
pip install -r requirements.txt
```

### 2. Конфигурация

Скопируйте `.env.example` в `.env` и добавьте ваш RPC URL:

```env
RPC_URL=https://eth-mainnet.g.alchemy.com/v3/YOUR_API_KEY
FACTORY_ADDRESS=0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f
START_BLOCK=10000835
BLOCK_RANGE=50000
BATCH_SIZE=2000
```

### 3. Запуск

```bash
# Индексация пар
python -m src.main

# Справка
python -m src.main help
```

## Структура проекта

```
src/
├── main.py              # CLI диспетчер
├── core/                # Базовые компоненты (config, rpc)
├── indexers/            # Индексаторы данных
├── decoders/            # Декодеры событий
├── storage/             # Хранение данных
└── commands/            # CLI команды
```

## Команды

- `index-pairs` - Индексация пар Uniswap V2 (по умолчанию)
- `help` - Справка

## Результат

Данные сохраняются в `uniswap_v2_pairs.csv`:

```csv
pair_address,token0,token1,pair_index,block_number,timestamp,transaction_hash
0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc,0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48,...
```

## Расширение

Добавьте новую команду в 3 шага:

1. Создайте `src/commands/your_command.py` с функцией `run()`
2. Зарегистрируйте в `src/main.py`
3. Используйте: `python -m src.main your-command`

См. примеры: `src/commands/index_transactions.py.example`

## Технологии

Python 3.12+ • Web3.py • Pandas • Ethereum
