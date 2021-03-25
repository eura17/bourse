-- user: matching_engine
if box.schema.user.exists('matching_engine') then
    box.schema.user.drop('matching_engine')
end
box.schema.user.create('matching_engine', {password='matching_engine'})
box.schema.user.grant('matching_engine', 'read,write,alter,drop,create,execute', 'universe')

-- user: broker
if box.schema.user.exists('broker') then
    box.schema.user.drop('broker')
end
box.schema.user.create('broker', {password='broker'})
box.schema.user.grant('broker', 'read,write,alter,drop,create,execute', 'universe')

-- user: data_provider
if box.schema.user.exists('data_provider') then
    box.schema.user.drop('data_provider')
end
box.schema.user.create('data_provider', {password='data_provider'})
box.schema.user.grant('data_provider', 'read,write,alter,drop,create,execute', 'universe')

-- user: robot
if box.schema.user.exists('robot') then
    box.schema.user.drop('robot')
end
box.schema.user.create('robot', {password='robot'})
box.schema.user.grant('robot', 'read,write,alter,drop,create,execute', 'universe')

-- user: web
if box.schema.user.exists('web') then
    box.schema.user.drop('web')
end
box.schema.user.create('web', {password='web'})
box.schema.user.grant('web', 'read,execute', 'universe')
