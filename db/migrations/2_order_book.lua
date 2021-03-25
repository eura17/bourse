if box.schema.func.exists('create_order_book_spaces') then
    box.schema.func.drop('create_order_book_spaces')
end
box.schema.func.create('create_order_book_spaces')
function create_order_book_spaces(ticker)
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
                    {name = 'real_order_no', type = 'unsigned', is_nullable = true},
                    {name = 'datetime', type = 'number'},
                    {name = 'price', type = 'number'},
                    {name = 'volume', type = 'unsigned'},
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
        box.schema.user.grant('broker', 'read', 'space', space)
        box.schema.user.grant('robot', 'read', 'space', space)
    end
end

if box.schema.func.exists('add_order_to_order_book') then
    box.schema.func.drop('add_order_to_order_book')
end
box.schema.func.create('add_order_to_order_book')
function add_order_to_order_book(ticker,
                                 operation,
                                 order_no,
                                 real_order_no,
                                 datetime,
                                 price,
                                 volume,
                                 robot)
    local space = (operation == 'buy' and 'bid' or operation == 'sell' and 'ask')..'_'..ticker
    box.space[space]:insert{order_no,
                            real_order_no,
                            datetime,
                            price,
                            volume,
                            robot}
end

if box.schema.func.exists('update_order_in_order_book') then
    box.schema.func.drop('update_order_in_order_book')
end
box.schema.func.create('update_order_in_order_book')
function update_order_in_order_book(ticker,
                                    operation,
                                    order_no,
                                    volume)
    local space = (operation == 'buy' and 'bid' or operation == 'sell' and 'ask')..'_'..ticker
    if volume <= 0 then
        box.space[space]:delete(order_no)
    else
        box.space[space]:update(order_no, {{'=', 'volume', volume}})
    end
end

if box.schema.func.exists('delete_order_from_order_book') then
    box.schema.func.drop('delete_order_from_order_book')
end
box.schema.func.create('delete_order_from_order_book')
function delete_order_from_order_book(ticker,
                                      operation,
                                      order_no,
                                      volume)
    local space = (operation == 'buy' and 'bid' or operation == 'sell' and 'ask')..'_'..ticker
    local order = box.space[space]:select(order_no)[1]
    if order == box.NULL then
        return
    end
    local current_volume = order[5]
    if volume >= current_volume then
        box.space[space]:delete(order_no)
    else
        box.space[space]:update(order_no, {{'=', 'volume', current_volume - volume}})
    end
end

if box.schema.func.exists('is_counter_orders_exist_in_order_book') then
    box.schema.func.drop('is_counter_orders_exist_in_order_book')
end
box.schema.func.create('is_counter_orders_exist_in_order_book')
function is_counter_orders_exist_in_order_book(ticker,
                                               operation)
    local space = (operation == 'buy' and 'ask' or operation == 'sell' and 'bid')..'_'..ticker
    return box.space[space]:len() > 0
end

if box.schema.func.exists('is_order_intersects_order_book') then
    box.schema.func.drop('is_order_intersects_order_book')
end
box.schema.func.create('is_order_intersects_order_book')
function is_order_intersects_order_book(ticker,
                                        operation,
                                        price)
    if operation == 'buy' then
        return get_min_ask_price_from_order_book(ticker) <= price
    elseif operation == 'sell' then
        return get_max_bid_price_from_order_book(ticker) >= price
    end
end

if box.schema.func.exists('get_min_ask_price_from_order_book') then
    box.schema.func.drop('get_min_ask_price_from_order_book')
end
box.schema.func.create('get_min_ask_price_from_order_book')
function get_min_ask_price_from_order_book(ticker)
    local min_ask = box.space['ask_'..ticker].index.price:min()
    if min_ask ~= box.NULL then
        return min_ask[4]
    else
        return box.NULL
    end
end

if box.schema.func.exists('get_min_ask_order_from_order_book') then
    box.schema.func.drop('get_min_ask_order_from_order_book')
end
box.schema.func.create('get_min_ask_order_from_order_book')
function get_min_ask_order_from_order_book(ticker)
    local min_ask = get_min_ask_price_from_order_book(ticker)
    if min_ask ~= box.NULL then
        min_ask = box.space['ask_'..ticker].index.price:select(min_ask, {limit=1})[1]
    else
        return box.NULL
    end
    if min_ask ~= box.NULL then
        return {
            min_ask[1],
            min_ask[2],
            ticker,
            'sell',
            'limit',
            min_ask[3],
            'set',
            min_ask[4],
            min_ask[5],
            min_ask[6]
        }
    else
        return box.NULL
    end
end

if box.schema.func.exists('get_max_bid_price_from_order_book') then
    box.schema.func.drop('get_max_bid_price_from_order_book')
end
box.schema.func.create('get_max_bid_price_from_order_book')
function get_max_bid_price_from_order_book(ticker)
    local max_bid = box.space['bid_'..ticker].index.price:max()
    if max_bid ~= box.NULL then
        return max_bid[4]
    else
        return box.NULL
    end
end

if box.schema.func.exists('get_max_bid_order_from_order_book') then
    box.schema.func.drop('get_max_bid_order_from_order_book')
end
box.schema.func.create('get_max_bid_order_from_order_book')
function get_max_bid_order_from_order_book(ticker)
    local max_bid = get_max_bid_price_from_order_book(ticker)
    if max_bid ~= box.NULL then
        max_bid = box.space['bid_'..ticker].index.price:select(max_bid, {limit = 1})[1]
    else
        return box.NULL
    end
    if max_bid ~= box.NULL then
        return {
            max_bid[1],
            max_bid[2],
            ticker,
            'buy',
            'limit',
            max_bid[3],
            'set',
            max_bid[4],
            max_bid[5],
            max_bid[6]
        }
    end
end

if box.schema.func.exists('get_active_orders_from_order_book') then
    box.schema.func.drop('get_active_orders_from_order_book')
end
box.schema.func.create('get_active_orders_from_order_book')
function get_active_orders_from_order_book(robot, ticker, operation)
    local raw_orders = {buy = {}, sell = {}}
    if operation == 'buy' then
        local bids = box.space['bid_'..ticker].index.robot:select(robot)
        if bids ~= box.NULL then
            for _, order in pairs(bids) do
                table.insert(raw_orders['buy'], order)
            end
        end
    elseif operation == 'sell' then
        local asks = box.space['ask_'..ticker].index.robot:select(robot)
        if asks ~= box.NULL then
            for _, order in pairs(asks) do
                table.insert(raw_orders['sell'], order)
            end
        end
    else
        local bids = box.space['bid_'..ticker].index.robot:select(robot)
        if bids ~= box.NULL then
            for _, order in pairs(bids) do
                table.insert(raw_orders['buy'], order)
            end
        end
        local asks = box.space['ask_'..ticker].index.robot:select(robot)
        if asks ~= box.NULL then
            for _, order in pairs(asks) do
                table.insert(raw_orders['sell'], order)
            end
        end
    end
    local orders = {}
    for side, orders_ in pairs(raw_orders) do
        for _, order in pairs(orders_) do
            table.insert(
                    orders,
                    {order[1],
                     order[2],
                     ticker,
                     side,
                     'limit',
                     order[3],
                     'set',
                     order[4],
                     order[5],
                     order[6]}
            )
        end
    end
    return orders
end

if box.schema.func.exists('get_order_book') then
    box.schema.func.drop('get_order_book')
end
box.schema.func.create('get_order_book')
function get_order_book(ticker)
    local raw_bids = box.space['bid_'..ticker]:select()
    local bids = {}
    for _, val in pairs(raw_bids) do
        local price = val[4]
        local volume = val[5]
        if bids[price] == nil then
            bids[price] = 0
        end
        bids[price] = bids[price] + volume
    end
    local raw_asks = box.space['ask_'..ticker]:select()
    local asks = {}
    for _, val in pairs(raw_asks) do
        local price = val[4]
        local volume = val[5]
        if asks[price] == nil then
            asks[price] = 0
        end
        asks[price] = asks[price] + volume
    end
    return {bids = bids, asks = asks}
end
