ON = true

if box.schema.func.exists('off') then
    box.schema.func.drop('off')
end
box.schema.func.create('off')
box.schema.user.grant('data_provider', 'execute', 'function', 'off')
function off()
    ON = false
end

if box.schema.func.exists('is_on') then
    box.schema.func.drop('is_on')
end
box.schema.func.create('is_on')
box.schema.user.grant('web', 'execute', 'function', 'is_on')
function is_on()
    return ON
end
