-- role: creator_of_spaces
if box.schema.role.exists('creator_of_spaces') then
    box.schema.role.drop('creator_of_spaces')
end
box.schema.role.create('creator_of_spaces')
-- create spaces
box.schema.role.grant('creator_of_spaces','create','space')
box.schema.role.grant('creator_of_spaces','write', 'space', '_schema')
box.schema.role.grant('creator_of_spaces','write', 'space', '_space')
-- create sequences and indexes
box.schema.role.grant('creator_of_spaces', 'create', 'sequence')
box.schema.role.grant('creator_of_spaces','read,write','space','_sequence')
box.schema.role.grant('creator_of_spaces','read,write','space','_space_sequence')
box.schema.role.grant('creator_of_spaces','write', 'space', '_index')

-- role: grantor_of_rights
if box.schema.role.exists('grantor_of_rights') then
    box.schema.role.drop('grantor_of_rights')
end
box.schema.role.create('grantor_of_rights')
box.schema.role.grant('grantor_of_rights', 'read', 'space', '_user')
box.schema.role.grant('grantor_of_rights', 'write', 'space', '_priv')

-- user: matching_engine
if box.schema.user.exists('matching_engine') then
    box.schema.user.drop('matching_engine')
end
box.schema.user.create('matching_engine', {password='matching_engine'})
box.schema.user.grant('matching_engine', 'creator_of_spaces')
box.schema.user.grant('matching_engine', 'grantor_of_rights')

-- user: broker
if box.schema.user.exists('broker') then
    box.schema.user.drop('broker')
end
box.schema.user.create('broker', {password='broker'})
box.schema.user.grant('broker', 'creator_of_spaces')
box.schema.user.grant('broker', 'grantor_of_rights')

-- user: data_provider
if box.schema.user.exists('data_provider') then
    box.schema.user.drop('data_provider')
end
box.schema.user.create('data_provider', {password='data_provider'})
box.schema.user.grant('data_provider', 'read,write,execute', 'universe')

-- user: robot
if box.schema.user.exists('robot') then
    box.schema.user.drop('robot')
end
box.schema.user.create('robot', {password='robot'})

-- user: web
if box.schema.user.exists('web') then
    box.schema.user.drop('web')
end
box.schema.user.create('web', {password='web'})
box.schema.user.grant('web', 'read,execute', 'universe')
