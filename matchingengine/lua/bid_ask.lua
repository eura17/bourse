function create_bid_ask_spaces(ticker)
    local bid_ask = {'bid', 'ask'}
    for _, value in pairs(bid_ask) do
        local space = value..'_'..ticker
        if box.space[space] ~= box.NULL then
            box.space[space]:drop()
        end
        local side = box.schema.space.create(space,
                                             {if_not_exists = true,
                                              temporary = true})
        side:format(
                {
                    {name = 'order_no', type = 'unsigned'},
                    {name = 'datetime', type = 'number'},
                    {name = 'price', type = 'number'},
                    {name = 'volume', type = 'number'},
                    {name = 'robot', type = 'string', is_nullable = true}
                }
        )
        side:create_index(
                'order_no',
                {
                    type = 'tree',
                    unique = true,
                    parts = {'order_no'},
                    if_not_exists = true
                }
        )
        side:create_index(
                'price',
                {
                    type = 'tree',
                    unique = false,
                    parts = {'price'},
                    if_not_exists = true
                }
        )
        side:create_index(
                'robot',
                {
                    type = 'tree',
                    unique = false,
                    parts = {'robot'},
                    if_not_exists = true
                }
        )
    end
end

function add_order(ticker,
                   operation,
                   order_no,
                   datetime,
                   price,
                   volume,
                   robot)
    local space = (operation == 'buy' and 'bid' or operation == 'sell' and 'ask')..'_'..ticker
    box.space[space]:insert{order_no,
                            datetime,
                            price,
                            volume,
                            robot}
end

function update_order(ticker,
                      operation,
                      order_no,
                      volume)
    local space = (operation == 'buy' and 'bid' or operation == 'sell' and 'ask')..'_'..ticker
    box.space[space]:update(order_no, {{'=', 'volume', volume}})
end

function delete_order(ticker,
                      operation,
                      order_no,
                      volume)
    local space = (operation == 'buy' and 'bid' or operation == 'sell' and 'ask')..'_'..ticker
    local order = box.space[space]:select(order_no)[1]
    if order == box.NULL then
        return
    end
    local current_volume = order[4]
    if volume >= current_volume then
        box.space[space]:delete(order_no)
    else
        box.space[space]:update(order_no, {{'=', 'volume', current_volume - volume}})
    end
end

function counter_orders_exist(ticker, operation)
    local space = (operation == 'buy' and 'ask' or operation == 'sell' and 'bid')..'_'..ticker
    return box.space[space]:len() > 0
end

function min_ask_price(ticker)
    local min_ask = box.space['ask_'..ticker].index.price:min()
    if min_ask ~= box.NULL then
        return min_ask[3]
    end
end

function min_ask_order(ticker)
    local min_ask = min_ask_price(ticker)
    min_ask = box.space['ask_'..ticker].index.price:select(min_ask,
                                                           {limit = 1})[1]
    local full_info = box.space['order_log'].index.order_no:select(min_ask[1])[1]
    return {full_info[2],
            full_info[3],
            full_info[4],
            full_info[5],
            full_info[6],
            full_info[7],
            full_info[8],
            full_info[9],
            min_ask[4],
            full_info[11]}
end

function max_bid_price(ticker)
    local max_bid = box.space['bid_'..ticker].index.price:max()
    if max_bid ~= box.NULL then
        return max_bid[3]
    end
end

function max_bid_order(ticker)
    local max_bid = max_bid_price(ticker)
    max_bid = box.space['bid_'..ticker].index.price:select(max_bid,
                                                           {limit = 1})[1]
    local full_info = box.space['order_log'].index.order_no:select(max_bid[1])[1]
    return {full_info[2],
            full_info[3],
            full_info[4],
            full_info[5],
            full_info[6],
            full_info[7],
            full_info[8],
            full_info[9],
            max_bid[4],
            full_info[11]}
end

function get_active_orders(robot, ticker, operation)
    local raw_orders = {}
    if operation == 'buy' then
        local bids = box.space['bid_'..ticker].index.robot:select(robot)[1]
        for _, order in pairs(bids) do
            table.insert(raw_orders, order)
        end
    elseif operation == 'sell' then
        local asks = box.space['ask_'..ticker].index.robot:select(robot)[1]
        for _, order in pairs(asks) do
            table.insert(raw_orders, order)
        end
    else
        local bids = box.space['bid_'..ticker].index.robot:select(robot)[1]
        for _, order in pairs(bids) do
            table.insert(raw_orders, order)
        end
        local asks = box.space['ask_'..ticker].index.robot:select(robot)[1]
        for _, order in pairs(asks) do
            table.insert(raw_orders, order)
        end
    end
    local orders = {}
    for _, order in pairs(raw_orders) do
        local full_info = box.space['order_log'].index.order_no:select(order[1])[1]
        table.insert(orders,
                {full_info[2],
                       full_info[3],
                       full_info[4],
                       full_info[5],
                       full_info[6],
                       full_info[7],
                       full_info[8],
                       full_info[9],
                       order[4],
                       full_info[11]})
    end
    return orders
end

function get_order_book(ticker)
    local raw_bids = box.space['bid_'..ticker]:select()[1]
    local bids = {}
    for _, val in pairs(raw_bids) do
        local price = val[3]
        local volume = val[4]
        if bids[price] == nil then
            bids[price] = 0
        end
        bids[price] = bids[price] + volume
    end
    local raw_asks = box.space['ask_'..ticker]:select()[1]
    local asks = {}
    for _, val in pairs(raw_asks) do
        local price = val[3]
        local volume = val[4]
        if asks[price] == nil then
            asks[price] = 0
        end
        asks[price] = asks[price] + volume
    end
    return {bids = bids, asks = asks}
end
