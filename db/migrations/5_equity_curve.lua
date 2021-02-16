if box.schema.func:exists('create_equity_curve_space') then
    box.schema.func.drop('create_equity_curve_space')
end
box.schema.func.create('create_equity_curve_space')
box.schema.user.grant('broker', 'execute', 'function', 'create_equity_curve_space')
function create_equity_curve_space(robot)
    local space = 'equity_curve_'..robot
    if box.space[space] ~= box.NULL then
        box.space[space]:drop()
    end
    local account = box.schema.space.create(space,
                                            {if_not_exists=true,
                                             temporary=true})
    account:format(
            {
                {name = 'datetime', type = 'number'},
                {name = 'liquidation_cost', type = 'number'}
            }
    )
    account:create_index(
            'datetime',
            {
                type = 'tree',
                unique = true,
                if_not_exists = true
            }
    )
end

if box.schema.func:exists('update_equity_curve_space') then
    box.schema.func.drop('update_equity_curve_space')
end
box.schema.func.create('update_equity_curve_space')
box.schema.user.grant('broker', 'execute', 'function', 'update_equity_curve_space')
function update_equity_curve_space(datetime, robot)
    local space = 'equity_curve_'..robot
    box.space[space]:insert({datetime, get_liquidation_cost_for_account(robot)})
end
