ON = true

if box.schema.func.exists('off') then
    box.schema.func.drop('off')
end
box.schema.func.create('off')
function off()
    ON = false
end

if box.schema.func.exists('is_on') then
    box.schema.func.drop('is_on')
end
box.schema.func.create('is_on')
function is_on()
    return ON
end
