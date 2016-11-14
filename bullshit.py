from recipes import recipe_kinase_mix, recipe_polymerase_mix, ramp, choices
from ref_kit_container import ref_kit_container

def bull_shit( p, params ):
    selection_antibiotic = params[ 'selection_antibiotic' ]
    mutants = eval( params[ 'mutants' ] ) # yeah, wow

    # ravel the fucking oligos
    oligos = []
    for mutant, oligo_list in mutants.items():
        for oligo in oligo_list:
            oligos.append( oligo )

    # the god damn metadata
    n_oligos = len( oligos )
    n_mutants = len( mutants )
    oligo_indexes = list( range( n_oligos ) )
    mutant_indexes = list( range( n_mutants ) )

    # synthesize oligos into tubes
    oligo_order = []
    oligo_tubes = [] # for resuspend and spinning
    for i in oligo_indexes:
        my_tube = p.ref( 'oligo_{}'.format( i ), None, 'micro-2.0', storage='cold_20' )
        oligo_tubes.append( my_tube )
        oligo_order.append( { 'sequence': oligos[ i ], 'destination': my_tube.well( 0 ), 'scale': '25nm' } )
    p.oligosynthesize( oligo_order )

    # provision kinase mix
    # into micro tube
    kin_mx = p.ref( 'kinase_mix', None, 'micro-2.0', discard=True )
    for ts_name, ts_id, vol in recipe_kinase_mix:
        # introducing this idiom for provisioning from recipes
        p.provision( ts_id, kin_mx.well(0), '{}:microliter'.format( vol * n_oligos ) )

    # new plate for kinasing
    kin_pt = p.ref( 'kinase_plate', None, '96-pcr', discard=True )
    p.distribute( kin_mx.well(0), kin_pt.wells( oligo_indexes ), '23:microliter' )
    for i in oligo_indexes:
        p.transfer( oligo_tubes[ i ].well( 0 ), kin_pt.well( i ), '7:microliter' )
    p.seal( kin_pt )
    p.incubate( kin_pt, 'warm_37', '1:hour' )

    # dilute and mix together oligos
    p.unseal( kin_pt )
    dil_pt = p.ref( 'dilute_plate', None, '96-flat', discard=True )
    p.dispense_full_plate( dil_pt, 'water', '200:microliter' )

    # for singles:
    if n_oligos == n_mutants:
        p.stamp( kin_pt, dil_pt, '2:microliter' )
    # for other than singles:
    else:
        for i in mutant_indexes:
            for j in oligo_indexes:
                p.transfer( oligo_tubes[ oligo_index ].well( 0 ), dil_pt.well( mutant_index ), '2:microliter' )
    p.cover( dil_pt )
    p.spin( dil_pt, '2000:g', '10:second' )

    # anneal
    # make anneal master mix, create yet another new plate
    ann_pt = p.ref( 'anneal_plate', None, '384-pcr', storage='cold_20' )
    p.transfer( params[ 'dna_aliquot' ], ann_pt.wells( mutant_indexes ), '2:microliter' )
    p.stamp( dil_pt, ann_pt, '2:microliter', mix_after=True )
    p.seal( ann_pt )
    p.spin( ann_pt, '2000:g', '10:second' )
    p.thermocycle( ann_pt, [{ 'cycles': 1, 'steps': ramp }] )

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
    p.provision( "rs16pbjc4r7vvz", tr_pt.wells( mutant_indexes ), "25:microliter")
    p.stamp( ann_pt, tr_pt, '2:microliter' )
    p.seal( tr_pt )
    p.incubate( tr_pt, 'cold_4', '10:minute' )
    p.unseal( tr_pt )
    p.dispense_full_plate( tr_pt, 'soc', '75:microliter' )
    p.seal( tr_pt )
    p.incubate( tr_pt, 'warm_37', '60:minute', shaking=True )
    p.seal( ann_pt )

    # plate
    agar_pts = [ ref_kit_container( p, i//6, choices['kanamycin'] ) for i in range( 0, n_mutants, 6 ) ]
    for m_index in mutant_indexes:
        p.spread( tr_pt.well( m_index ), agar_pts[ m_index // 6 ].well( m_index % 6 ), '100:microliter' )
    for i, agar_pt in enumerate( agar_pts ):
        p.incubate( agar_pt, 'warm_37', '8:hour' )
        p.image_plate( agar_pt, mode='top', dataref='agar_{}'.format( i ) )

if __name__ == '__main__':
    from autoprotocol.harness import run
    run( bull_shit, 'bull_shit' )
