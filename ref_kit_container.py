from autoprotocol.container import Container
from autoprotocol.protocol import Ref

def ref_kit_container( protocol, index, kit_id ):
    name = 'agar_{}'.format( index )
    kit_item = Container( None, protocol.container_type( '6-flat'), storage='cold_4' )
    protocol.refs[ name ] = Ref( name, { 'reserve': kit_id, 'store': 'cold_4' } , kit_item ) # jesus transcriptic
    return( kit_item )
