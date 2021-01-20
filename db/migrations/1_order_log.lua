function create_order_log_space()
    if box.space['order_log'] ~= box.NULL then
        box.space['order_log']:drop()
    end
    local order_log = box.schema.space.create('order_log',
                                              {engine='vinyl',
                                               if_not_exists = true})
    order_log:format(
            {
                {name = 'no', type = 'unsigned'},
                {name = 'order_no', type = 'unsigned'},
                {name = 'real_order_no', type = 'unsigned', is_nullable=true},
                {name = 'ticker', type = 'string'},
                {name = 'operation', type = 'string'},
                {name = 'type', type = 'string'},
                {name = 'datetime', type = 'number'},
                {name = 'action', type = 'string'},
                {name = 'price', type = 'number'},
                {name = 'volume', type = 'number'},
                {name = 'robot', type = 'string', is_nullable=true}
            }
    )
    if box.sequence['order_log_no'] ~= box.NULL then
        box.sequence['order_log_no']:drop()
    end
    box.schema.sequence.create('order_log_no')
    order_log:create_index(
            'no',
            {
                type = 'tree',
                unique = true,
                sequence = {'order_log_no'},
                if_not_exists = true
            }
    )
    order_log:create_index(
            'order_no',
            {
                type = 'tree',
                unique = false,
                parts = {'order_no'},
                if_not_exists = true
            }
    )
    order_log:create_index(
            'real_order_no',
            {
                type = 'tree',
                unique = false,
                parts = {'real_order_no'},
                if_not_exists = true
            }
    )
    order_log:create_index(
            'robot',
            {
                type = 'tree',
                unique = false,
                parts = {'robot'},
                if_not_exists = true
            }
    )
end

function add_to_order_log(order_no,
                          real_order_no,
                          sec_code,
                          operation,
                          type,
                          datetime,
                          action,
                          price,
                          volume,
                          robot)
    if action == 'delete' then
        if real_order_no ~= box.NULL then
            order_no = box.space['order_log'].index.real_order_no:select(real_order_no)[1][2]
        end
    elseif action == 'set' then
        local max_order_no = box.space['order_log'].index.order_no:max()
        order_no = (max_order_no and max_order_no[2] or 0) + 1
    end
    box.space['order_log']:insert({nil,
                                   order_no,
                                   real_order_no,
                                   sec_code,
                                   operation,
                                   type,
                                   datetime,
                                   action,
                                   price,
                                   volume,
                                   robot})
    return order_no
end