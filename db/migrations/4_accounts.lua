function create_account_space(robot)
    local space = 'account_'..robot
    if box.space[space] ~= box.NULL then
        box.space[space]:drop()
    end
    local account = box.schema.space.create(space,
                                            {if_not_exists=true,
                                             temporary=true})
    account:format(
            {
                {name = 'id', type = 'unsigned'},
                {name = 'asset', type = 'string'},
                {name = 'price', type = 'number'},
                {name = 'volume', type = 'number'},
            }
    )
    local id = space..'_id'
    if box.sequence[id] ~= box.NULL then
        box.sequence[id]:drop()
    end
    box.schema.sequence.create(id)
    account:create_index(
            'id',
            {
                type = 'tree',
                unique = true,
                sequence = id,
                if_not_exists = true
            }
    )
    account:create_index(
            'asset',
            {
                type = 'tree',
                unique = true,
                parts = {'asset'},
                if_not_exists = true
            }
    )
end

function add_asset_to_account(robot,
                              asset,
                              price,
                              volume)
    box.space['account_'..robot]:insert({nil,
                                         asset,
                                         price,
                                         volume})
end

function get_asset_from_account(robot,
                                asset)
    local rec = box.space['account_'..robot].index.asset:select(asset)[1]
    return {rec[3], rec[4]}
end

function get_all_assets_from_account(robot)
    local rec = box.space['account_'..robot]:select()
    local assets = {}
    for _, val in pairs(rec) do
        assets[val[2]] = {val[3], val[4]}
    end
    return assets
end

function change_asset_in_account(robot,
                                 asset,
                                 price,
                                 volume)
    local space = 'account_'..robot
    local id = box.space[space].index.asset:select(asset)[1][1]
    box.space[space]:update(id,
                            {{'=', 'price', price},
                             {'=', 'volume', volume}})
end

function get_liquidation_cost_for_account(robot)
    local assets = get_all_assets_from_account(robot)
    local liquidation_cost = 0
    local price, volume
    for asset, pv in pairs(assets) do
        if asset == 'CASH' then
            price = 1
        else
            price = get_last_trade_price(asset)
            if price == box.NULL then
                local min_ask = get_min_ask_price_from_order_book(asset)
                local max_bid = get_max_bid_price_from_order_book(asset)
                if min_ask == box.NULL or max_bid == box.NULL then
                    price = pv[1]
                else
                    price = (min_ask + max_bid) / 2
                end
            end
        end
        volume = pv[2]
        liquidation_cost = liquidation_cost + price * volume
    end
    return liquidation_cost
end
