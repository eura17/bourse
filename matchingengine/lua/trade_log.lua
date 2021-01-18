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
end

function add_to_trade_log(ticker,
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

function get_last_trade_price(ticker)
    local all_deals = box.space['trade_log'].index.ticker:select(ticker)
    local last_trade = all_deals[#all_deals]
    if last_trade ~= box.NULL then
        return last_trade[8]
    end
end

function get_candles(ticker, stop_dt, ofst)
    local all_trades = box.space['trade_log'].index.datetime:select(stop_dt, {iterator='GE'})[1]
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
            if stop_dt <= dt and dt <= stop_dt + ofst then
                if price > high then
                    high = price
                end
                if price < low then
                    low = price
                end
                volume = volume + vol
            elseif i == #all_trades then
                close = price
                volume = volume + vol
                table.insert(candles, {open, high, low, close, volume})
            else
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