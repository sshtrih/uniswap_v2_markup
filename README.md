# Multi-Protocol Blockchain Indexer

Модульный индексатор для анализа данных различных DeFi протоколов на Ethereum. Поддерживает Uniswap V2, Uniswap V3 и легко расширяется для других протоколов.

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
# Индексация пар из Factory (PairCreated) - по умолчанию uniswap_v2
python -m src.main index-pairs

# Индексация с указанием протокола
python -m src.main --protocol uniswap_v2 index-pairs
python -m src.main -p uniswap_v3 index-pairs

# Индексация событий пар (Swap, Mint, Burn) по адресам из CSV
python -m src.main index-pair-events
python -m src.main -p uniswap_v2 index-pair-events

# Справка
python -m src.main --help
python -m src.main help
```


## Структура проекта

```
src/
├── main.py                    # CLI диспетчер с 
└── protocols/                 # Реализации протоколов
    ├── uniswap_v2/
    │   ├── commands/          # Команды (index_pairs, index_pair_events)
    │   ├── core/              # Конфиг, RPC
    │   ├── decoders/          # Декодеры событий
    │   ├── indexers/          # Индексаторы (factory, pairs)
    │   └── storage/           # Сохранение в CSV
    └── uniswap_v3/            # (в разработке)
```

## Команды

| Команда | Описание |
|--------|----------|
| `index-pairs` | Индексация пар из Factory (PairCreated), сохраняет в `data/{protocol}/{protocol}_pairs.csv` |
| `index-pair-events` | Индексация событий пар (Swap, Mint, Burn) по адресам из CSV, сохраняет в `data/{protocol}/{protocol}_pair_events.csv` |
| `help` | Справка по командам |

## Опции

| Опция | Описание |
|-------|----------|
| `-p, --protocol NAME` | Выбор протокола (по умолчанию: `uniswap_v2`). Доступно: `uniswap_v2`, `uniswap_v3` |

## Результаты

Данные сохраняются в `data/{protocol}/` для каждого протокола отдельно.

**Пары** — `data/uniswap_v2/uniswap_v2_pairs.csv`:

```csv
pair_address,token0,token1,pair_index,block_number,timestamp,transaction_hash
0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc,0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48,...
```

**События пар** — `data/uniswap_v2/uniswap_v2_pair_events.csv`:

```csv
event_type,pair_address,sender,amount0,amount1,amount0In,amount1In,amount0Out,amount1Out,to,block_number,transaction_hash,log_index
swap,0x...,0x...,,,1000000,0,0,500000,0x...,12345678,0xabc...,0
mint,0x...,0x...,1000,2000,,,,,,12345679,0xdef...,1
```

## Расширение

### Добавление нового протокола

1. Создайте структуру в `src/protocols/{protocol_name}/`:
   ```
   src/protocols/{protocol_name}/
   ├── __init__.py
   ├── commands/
   │   ├── __init__.py
   │   ├── index_pairs.py      # с функцией run()
   │   └── index_pair_events.py # с функцией run()
   ├── core/
   │   ├── __init__.py
   │   ├── config.py
   │   └── rpc.py
   ├── decoders/
   ├── indexers/
   └── storage/
   ```

2. Добавьте протокол в список `PROTOCOLS` в `src/main.py`

3. Реализуйте команды по аналогии с `uniswap_v2`

### Добавление новой команды

1. Создайте `src/protocols/{protocol}/commands/your_command.py` с функцией `run()`
2. Добавьте команду в `choices` аргумента `command` в `src/main.py`
3. Добавьте обработку в `main()`: `if args.command == 'your-command':`

## Технологии

Python 3.12+ • Web3.py • Pandas • Ethereum
