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
# Индексация пар из Factory (PairCreated)
python -m src.main index-pairs

# Индексация событий пар (Swap, Mint, Burn) по адресам из CSV
python -m src.main index-pair-events

# Справка
python -m src.main help
```

Рекомендуемый порядок: сначала `index-pairs` (создаёт `data/uniswap_v2_pairs.csv`), затем `index-pair-events` (читает этот CSV и сохраняет события в `data/uniswap_v2_pair_events.csv`).

## Структура проекта

```
src/
├── main.py              # CLI диспетчер
├── core/                # Конфиг, RPC
├── indexers/            # factory_indexer, pairs_indexer
├── decoders/            # event_decoder (PairCreated, Swap, Mint, Burn)
├── storage/             # CSV (пары, события пар)
└── commands/            # index_pairs, index_pair_events
```

## Команды

| Команда | Описание |
|--------|----------|
| `index-pairs` | Индексация пар из Factory (PairCreated), сохраняет в `data/uniswap_v2_pairs.csv` |
| `index-pair-events` | Индексация событий пар (Swap, Mint, Burn) по адресам из CSV, сохраняет в `data/uniswap_v2_pair_events.csv` |
| `help` | Справка по командам |

## Результаты

**Пары** — `data/uniswap_v2_pairs.csv`:

```csv
pair_address,token0,token1,pair_index,block_number,timestamp,transaction_hash
0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc,0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48,...
```

**События пар** — `data/uniswap_v2_pair_events.csv`:

```csv
event_type,pair_address,sender,amount0,amount1,amount0In,amount1In,amount0Out,amount1Out,to,block_number,transaction_hash,log_index
swap,0x...,0x...,,,1000000,0,0,500000,0x...,12345678,0xabc...,0
mint,0x...,0x...,1000,2000,,,,,,12345679,0xdef...,1
```

## Расширение

Добавьте новую команду в 3 шага:

1. Создайте `src/commands/your_command.py` с функцией `run()`
2. Зарегистрируйте в `src/main.py` (блок `if command == 'your-command':` и пункт в `print_help()`)
3. Запуск: `python -m src.main your-command`

## Технологии

Python 3.12+ • Web3.py • Pandas • Ethereum
