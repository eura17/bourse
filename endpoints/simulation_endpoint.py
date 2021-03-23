import threading
from typing import Any, Dict, Tuple
import datetime as dt
from uuid import uuid4

from quart import Blueprint, request

from run import run_windows

blueprint = Blueprint('simulation', __name__, url_prefix='/',
                      strict_slashes=False)


@blueprint.route(rule='/run', methods=['POST'])
async def run() -> Tuple[Dict[str, Any], int]:
    data = await request.get_json()

    if data is None:
        return {
                   'error_code': 'bourse.request.invalid',
                   'error_message': 'Invalid request'
               }, 400

    tickers = data['tickers']
    dates = data['dates']
    strategies = data['strategies']
    start_account = data['start_account']
    leverage = data['leverage']
    commission_abs = data['commission_abs']
    commission_pct = data['commission_pct']
    discreteness = data['discreteness']
    port = data['port']

    if dates is None or strategies is None or start_account is None or \
            leverage is None or commission_abs is None or \
            commission_pct is None or discreteness is None or port is None or \
            tickers is None or len(tickers) == 0:
        return {
                   'error_code': 'bourse.request.invalid',
                   'error_message': 'Invalid request'
               }, 400

    test_id = uuid4()

    def run_async():
        run_windows(
            tickers=tickers,
            dates=[dt.date.fromisoformat(d) for d in dates],
            strategies=strategies,
            start_account=start_account,
            leverage=leverage,
            commission_abs=commission_abs,
            commission_pct=commission_pct,
            discreteness=dt.timedelta(seconds=discreteness),
            port=port
        )

    b = threading.Thread(name='background', target=run_async)

    b.start()

    return {
        'id': test_id
    }, 200
