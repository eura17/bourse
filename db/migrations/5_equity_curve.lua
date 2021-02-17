if box.schema.func.exists('create_equity_curve_space') then
    box.schema.func.drop('create_equity_curve_space')
end
box.schema.func.create('create_equity_curve_space')
box.schema.user.grant('broker', 'execute', 'function', 'create_equity_curve_space')
function create_equity_curve_space(robot)
    local space = 'equity_curve_'..robot
    if box.space[space] ~= box.NULL then
        box.space[space]:drop()
    end
    local equity_curve = box.schema.space.create(space,
                                            {if_not_exists=true,
                                             temporary=true})
    equity_curve:format(
            {
                {name=  'id', type='unsigned'},
                {name = 'datetime', type = 'number'},
                {name = 'liquidation_cost', type = 'number'}
            }
    )
    local id = space..'_id'
    if box.sequence[id] ~= box.NULL then
        box.sequence[id]:drop()
    end
    box.schema.sequence.create(id)
    equity_curve:create_index(
            'no',
            {
                type = 'tree',
                unique = true,
                sequence = {id},
                if_not_exists = true
            }
    )
end

if box.schema.func.exists('update_equity_curve_space') then
    box.schema.func.drop('update_equity_curve_space')
end
box.schema.func.create('update_equity_curve_space')
box.schema.user.grant('broker', 'execute', 'function', 'update_equity_curve_space')
function update_equity_curve_space(datetime, robot)
    local space = 'equity_curve_'..robot
    box.space[space]:insert({nil, datetime, get_liquidation_cost_for_account(robot)})
end

if box.schema.func.exists('get_amount_of_records_in_equity_curve') then
    box.schema.func.drop('get_amount_of_records_in_equity_curve')
end
box.schema.func.create('get_amount_of_records_in_equity_curve')
box.schema.user.grant('broker', 'execute', 'function', 'get_amount_of_records_in_equity_curve')
function get_amount_of_records_in_equity_curve(robot)
    local space = 'equity_curve_'..robot
    return box.space[space]:len()
end

if box.schema.func.exists('get_records_from_equity_curve') then
    box.schema.func.drop('get_records_from_equity_curve')
end
box.schema.func.create('get_records_from_equity_curve')
box.schema.user.grant('broker', 'execute', 'function', 'get_records_from_equity_curve')
function get_records_from_equity_curve(robot, start_no, end_no)
    local space = 'equity_curve_'..robot
    return box.space[space]:select(start_no, {iterator = 'GE', limit = end_no-start_no})
end
