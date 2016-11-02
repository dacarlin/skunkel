# some bull shit protocol

def bull_shit( p, params ):

    selection_antibiotic = params[ 'selection_antibiotic' ] # this is for solid media only
    mutants = eval( params[ 'mutants' ] ) # yeah, wow

    # two bull shit recipes and 1 thermal cycle ramp

    recipe_kinase_mix = [
        ( 'PNK_buffer', 'rs16pc9rd5sg5d', 3 ),
        ( 'water', 'rs17gmh5wafm5p', 18 ),
        ( 'polynucleotide_kinase', 'rs16pc9rd5hsf6', 1 ),
        ( '100mM_ATP', 'rs16pccshb6cb4', 1 ),
    ]

    recipe_polymerase_mix = [
        ( 'T4_ligase_buffer_10X', 'rs17sh5rzz79ct', 0.6 ),
        ( 'T4_ligase', 'rs16pc8krr6ag7', 0.4 ),
        ( 'T7_pol', 'rs16pca2urcz74', 0.4 ),
        ( 'dNTPs', 'rs16pcb542c5rd', 0.4 ),
    ]

    ramp = [ { 'duration': '60:second', 'temperature': '{}:celsius'.format( 95 - i ) } for i in range( 70 ) ]

    # wrangle the fucking oligos

    # synthetize oligos into tubes
    # and reformat into plate
    # expensive? more expensive then ordering dummy oligos?
    oligo_pt = p.ref( 'oligo_pt', None, '96-pcr', storage='cold_20' )
    oligos = []
    i = 0
    for mutant, oligo_list in mutants.items():
        for oligo in oligo_list:
            my_tube = p.ref( 'oligo_{}'.format( i ), None, 'micro-2.0', storage='cold_20' )
            i += 1
            oligos.append( { 'oligo_label': oligo, 'sequence': oligo, 'destination': oligo_pt.well( i ), 'scale': '25nm' } )
    p.oligosynthesize( oligos )

    # save for later, will use these a lot
    n_oligos = len( oligos )
    n_mutants = len( mutants )
    oligo_indexes = list( range( n_oligos ) )
    mutant_indexes = list( range( n_mutants ) )

    # provision kinase mix
    # into micro tube
    kin_mx = p.ref( 'kinase_mix', None, 'micro-2.0', discard=True )
    for ts_name, ts_id, vol in recipe_kinase_mix: # idiom for provisioning from recipes
        p.provision( ts_id, kin_mx.well(0), '{}:microliter'.format( vol * n_oligos ) )

    # new plate for kinasing?
    kin_pt = p.ref( 'kinase_plate', None, '96-pcr', discard=True )
    p.distribute( kin_mx.well(0), kin_pt.wells( oligo_indexes ), '23:microliter' )
    p.stamp( oligo_pt, kin_pt, '7:microliter' )
    p.seal( kin_pt )
    p.incubate( kin_pt, 'warm_37', '1:hour' )

    # dilute and mix together oligos
    p.unseal( kin_pt )
    dil_pt = p.ref( 'dilute_plate', None, '96-flat', discard=True )
    p.dispense_full_plate( dil_pt, 'water', '200:microliter' )
    #p.stamp( kin_pt, dil_pt, '2:microliter' ) for singles only!
    # for multiples, we have to do
    for mutant_index, __ in enumerate( mutants ):
        for oligo_index, __ in enumerate( oligos ):
            p.transfer( oligo_pt.well( oligo_index ), dil_pt.well( mutant_index ), '2:microliter' )
            # how annoying
    p.cover( dil_pt )
    p.spin( dil_pt, '2000:g', '10:second' )

    # anneal
    # make anneal master mix
    # create yet another new plate
    ann_pt = p.ref( 'anneal_plate', None, '384-pcr', storage='cold_20' )
    p.transfer( params[ 'dna_aliquot' ], ann_pt.wells( mutant_indexes ), '2:microliter' )
    p.stamp( dil_pt, ann_pt, '2:microliter', mix_after=True )
    p.seal( ann_pt )
    p.spin( ann_pt, '2000:g', '10:second' )
    p.thermocycle( ann_pt, [{ 'cycles': 1, 'steps': ramp, 'volume': '5:microliter' }] )

    # polymerize
    p.unseal( ann_pt )
    p_mx = p.ref( 'polymerize_mix', None, 'micro-2.0', discard=True )
    for ts_name, ts_id, vol in recipe_kinase_mix:
        p.provision( ts_id, p_mx.well(0), '{}:microliter'.format( vol * n_oligos ) )
    p.transfer( p_mx.well(0), ann_pt.wells( mutant_indexes ), '2:microliter' )
    p.incubate( ann_pt, 'ambient', '90:minute' )

    # transform
    tr_pt = p.ref( "transformation_plate", None, "96-pcr", discard=True )
    p.incubate( tr_pt, "cold_20", "10:minute" )
    p.provision( "rs16pbjc4r7vvz", tr_pt.wells( mutant_indexes ), "10:microliter")
    p.stamp( ann_pt, tr_pt, '2:microliter' )
    p.seal( tr_pt )
    p.incubate( tr_pt, 'cold_4', '20:minute' )
    p.unseal( tr_pt )
    p.dispense_full_plate( tr_pt, 'soc', '40:microliter' )
    p.seal( tr_pt )
    p.incubate( tr_pt, 'warm_37', '60:minute', shaking=True )

    # plate
    # possible selection antibiotics:
    choices = {
        "kanamycin": "ki17rs7j799zc2",
        "ampicillin": "ki17sbb845ssx9"
    }

    # Transcriptic provisioning bull shit
    # from autoprotocol.container import Container
    # from autoprotocol.protocol import Ref
    #
    # agar_plates = []
    # for plate_index in range( n_mutants, 6 ):
    #     pt_name = '{}_{}'
    #     kit_item = Container( None, p.container_type( '6-flat' ) )
    #     the_pt = Ref( pt_name, { "reserve": choices[ selection_antibiotic ], "store": { "where": 'cold_4' }}, kit_item )
    #     p.refs[ pt_name ] = the_pt # dumb
    #
    #     agar_plates.append( the_pt )
    #     for i, w in enumerate( mutant_indexes[ plate_index : plate_index + 6 ] ):
    #         p.spread( w, agar_plate.well(i), '100:microliter' )
    #
    # for agar_p in agar_plates:
    #     p.incubate( agar_p, 'warm_37', '12:hour' )
    #     p.image_plate( agar_p, mode='top', dataref=agar_p.name )

if __name__ == '__main__':
    from autoprotocol.harness import run
    run( bull_shit, 'bull_shit' )
