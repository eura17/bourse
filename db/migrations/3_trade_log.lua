if box.schema.func.exists('create_trade_log_space') then
    box.schema.func.drop('create_trade_log_space')
end
box.schema.func.create('create_trade_log_space')
function create_trade_log_space()
    if box.space['trade_log'] ~= box.NULL then
        box.space['trade_log']:drop()
    end
    local trade_log = box.schema.space.create('trade_log',
                                              {engine='vinyl'})
    trade_log:format(
            {
                {name = 'trade_no', type = 'unsigned'},
                {name = 'ticker', type = 'string'},
                {name = 'datetime', type = 'number'},
                {name = 'buy_order_no', type = 'unsigned'},
                {name = 'buyer_robot', type = 'string', is_nullable=true},
                {name = 'sell_order_no', type = 'unsigned'},
                {name = 'seller_robot', type = 'string', is_nullable=true},
                {name = 'price', type = 'number'},
                {name = 'volume', type = 'number'},
            }
    )
    if box.sequence['trade_log_no'] ~= box.NULL then
        box.sequence['trade_log_no']:drop()
    end
    box.schema.sequence.create('trade_log_no')
    trade_log:create_index(
            'trade_no',
            {
                type = 'tree',
                unique = true,
                sequence = 'trade_log_no',
                if_not_exists = true
            }
    )
    trade_log:create_index(
            'ticker',
            {
                type = 'tree',
                unique = false,
                parts = {'ticker'},
                if_not_exists = true
            }
    )
    trade_log:create_index(
            'datetime',
            {
                type = 'tree',
                unique = false,
                parts = {'datetime'},
                if_not_exists = true
            }
    )
    trade_log:create_index(
            'buyer_robot',
            {
                type = 'tree',
                unique = false,
                parts = {'buyer_robot'},
                if_not_exists = true
            }
    )
    trade_log:create_index(
            'seller_robot',
            {
                type = 'tree',
                unique = false,
                parts = {'seller_robot'},
                if_not_exists = true
            }
    )
    box.schema.user.grant('broker', 'read', 'space', 'trade_log')
    box.schema.user.grant('robot', 'read', 'space', 'trade_log')
end

if box.schema.func.exists('add_trade_to_trade_log') then
    box.schema.func.drop('add_trade_to_trade_log')
end
box.schema.func.create('add_trade_to_trade_log')
function add_trade_to_trade_log(ticker,
                                datetime,
                                buy_order_no,
                                buyer_robot,
                                sell_order_no,
                                seller_robot,
                                price,
                                volume)
    box.space['trade_log']:insert({nil,
                                   ticker,
                                   datetime,
                                   buy_order_no,
                                   buyer_robot,
                                   sell_order_no,
                                   seller_robot,
                                   price,
                                   volume})
end

if box.schema.func.exists('get_last_trade_price_from_trade_log') then
    box.schema.func.drop('get_last_trade_price_from_trade_log')
end
box.schema.func.create('get_last_trade_price_from_trade_log')
function get_last_trade_price_from_trade_log(ticker)
    local last_trade_n = box.space['trade_log']:len()
    local last_trade
    while last_trade_n > 0 do
        last_trade = box.space['trade_log']:select(last_trade_n)[1]
        if last_trade[2] == ticker then
            return last_trade[8]
        end
        last_trade_n = last_trade_n - 1
    end
    return box.NULL
end

if box.schema.func.exists('get_candles_from_trade_log') then
    box.schema.func.drop('get_candles_from_trade_log')
end
box.schema.func.create('get_candles_from_trade_log')
function get_candles_from_trade_log(ticker, stop_dt, ofst)
    local first_trade = box.space['trade_log']:select(1)[1]
    if first_trade == nil then
        return {}
    end
    local first_trade_time = first_trade[3]
    if stop_dt + ofst < first_trade_time then
        stop_dt = first_trade_time
    end
    local all_trades = box.space['trade_log'].index.datetime:select(stop_dt, {iterator='GE'})
    local candles = {}
    local t, dt, price, vol
    local open, high, low, close, volume = box.NULL, box.NULL, box.NULL, box.NULL, 0
    for i, val in ipairs(all_trades) do
        t = val[2]
        if t == ticker then
            dt = val[3]
            price = val[8]
            vol = val[9]
            if open == box.NULL then
                open = price
            end
            if high == box.NULL then
                high = price
            end
            if low == box.NULL then
                low = price
            end
            if close == box.NULL then
                close = price
            end
            if price > high then
                high = price
            end
            if price < low then
                low = price
            end
            if stop_dt <= dt and dt <= stop_dt + ofst then
                volume = volume + vol
            elseif i == #all_trades then
                close = price
                volume = volume + vol
                table.insert(candles, {open, high, low, close, volume})
            elseif dt > stop_dt + ofst then
                close = price
                volume = volume + vol
                table.insert(candles, {open, high, low, close, volume})

                open, high, low, close, volume = box.NULL, box.NULL, box.NULL, box.NULL, 0
                stop_dt = stop_dt + ofst
            end
        end
    end
    return candles
end

if box.schema.func.exists('get_amount_of_trades_in_trade_log') then
    box.schema.func.drop('get_amount_of_trades_in_trade_log')
end
box.schema.func.create('get_amount_of_trades_in_trade_log')
function get_amount_of_trades_in_trade_log()
    return box.space['trade_log']:len()
end

if box.schema.func.exists('get_trades_from_trade_log') then
    box.schema.func.drop('get_trades_from_trade_log')
end
box.schema.func.create('get_trades_from_trade_log')
function get_trades_from_trade_log(start_no, end_no)
    return box.space['trade_log']:select(start_no, {iterator='GE', limit = end_no - start_no})
end
