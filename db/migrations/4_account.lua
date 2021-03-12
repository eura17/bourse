if box.schema.func.exists('create_account_space') then
    box.schema.func.drop('create_account_space')
end
box.schema.func.create('create_account_space')
box.schema.user.grant('broker', 'execute', 'function', 'create_account_space')
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
    box.schema.user.grant('robot', 'read', 'space', space)
end

if box.schema.func.exists('add_asset_to_account') then
    box.schema.func.drop('add_asset_to_account')
end
box.schema.func.create('add_asset_to_account')
box.schema.user.grant('broker', 'execute', 'function', 'add_asset_to_account')
function add_asset_to_account(robot,
                              asset,
                              price,
                              volume)
    box.space['account_'..robot]:insert({nil,
                                         asset,
                                         price,
                                         volume})
end

if box.schema.func.exists('get_asset_from_account') then
    box.schema.func.drop('get_asset_from_account')
end
box.schema.func.create('get_asset_from_account')
box.schema.user.grant('broker', 'execute', 'function', 'get_asset_from_account')
box.schema.user.grant('robot', 'execute', 'function', 'get_asset_from_account')
function get_asset_from_account(robot,
                                asset)
    local rec = box.space['account_'..robot].index.asset:select(asset)[1]
    return {rec[3], rec[4]}
end

if box.schema.func.exists('get_all_assets_from_account') then
    box.schema.func.drop('get_all_assets_from_account')
end
box.schema.func.create('get_all_assets_from_account')
box.schema.user.grant('broker', 'execute', 'function', 'get_all_assets_from_account')
box.schema.user.grant('robot', 'execute', 'function', 'get_all_assets_from_account')
function get_all_assets_from_account(robot)
    local rec = box.space['account_'..robot]:select()
    local assets = {}
    for _, val in pairs(rec) do
        assets[val[2]] = {val[3], val[4]}
    end
    return assets
end

if box.schema.func.exists('change_asset_in_account') then
    box.schema.func.drop('change_asset_in_account')
end
box.schema.func.create('change_asset_in_account')
box.schema.user.grant('broker', 'execute', 'function', 'change_asset_in_account')
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

if box.schema.func.exists('get_liquidation_cost_for_account') then
    box.schema.func.drop('get_liquidation_cost_for_account')
end
box.schema.func.create('get_liquidation_cost_for_account')
box.schema.user.grant('broker', 'execute', 'function', 'get_liquidation_cost_for_account')
box.schema.user.grant('robot', 'execute', 'function', 'get_liquidation_cost_for_account')
function get_liquidation_cost_for_account(robot)
    local assets = get_all_assets_from_account(robot)
    local liquidation_cost = 0
    local price, volume
    for asset, pv in pairs(assets) do
        if asset == 'CASH' then
            price = 1
        else
            price = get_last_trade_price_from_trade_log(asset)
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

if box.schema.func.exists('get_pedestal') then
    box.schema.func.drop('get_pedestal')
end
box.schema.func.create('get_pedestal')
function get_pedestal()
    local accounts = {}
    for k, _ in pairs(box.space) do
        k = tostring(k)
        local starts_with = 'account_'
        if k:sub(1, #starts_with) == starts_with then
            local account = k:sub(#starts_with+1, #k)
            accounts[account] = get_liquidation_cost_for_account(account)
        end
    end
    return accounts
end
