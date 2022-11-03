from web3 import Web3
import asyncio
import config as cfg

alchemy_url = 'https://eth-mainnet.g.alchemy.com/v2/' + cfg.alchemy_api_key
w3 = Web3(Web3.HTTPProvider(alchemy_url))

class Listener:
    def __init__(self, token_from, token_to, aggregator_address, aggregator_abi):
        self.token_from = token_from
        self.token_to = token_to
        self.contract = w3.eth.contract(address=aggregator_address, abi=aggregator_abi)
    
    def _get_price_by_event(self, event):
        json_data = event['args']['current']
        return round(float(json_data) / (10.0 ** self.contract.functions.decimals().call()), 6)
    
    def _handle_event(self, event):
        price = self._get_price_by_event(event)
        print('{}/{} new price is {}'.format(self.token_from, self.token_to, price))

    async def listen(self, poll_interval=2.0):
        event_filter = self.contract.events.AnswerUpdated.createFilter(fromBlock='latest')

        while True:
            for pair_created in event_filter.get_new_entries():
                self._handle_event(pair_created)
            await asyncio.sleep(poll_interval)


eth_usd_listener = Listener(
    token_from='ETH',
    token_to='USD',
    aggregator_address=cfg.eth_usd_aggregator_address,
    aggregator_abi=cfg.eth_usd_aggregator_abi,
)

link_eth_listener = Listener(
    token_from='LINK',
    token_to='ETH',
    aggregator_address=cfg.link_eth_aggregator_address,
    aggregator_abi=cfg.link_eth_aggregator_abi,
)

usdt_eth_listener = Listener(
    token_from='USDT',
    token_to='ETH',
    aggregator_address=cfg.usdt_eth_aggregator_address,
    aggregator_abi=cfg.usdt_eth_aggregator_abi,
)

async def listen():
    listeners = [
        eth_usd_listener,
        link_eth_listener,
        usdt_eth_listener,
    ]
    tasks = []
    for listener in listeners:
        tasks.append(asyncio.create_task(listener.listen()))
    await asyncio.gather(*tasks)

asyncio.run(listen())
