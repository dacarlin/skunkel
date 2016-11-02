# some bull shit protocol

def bull_shit( p, params ):

    selection_antibiotic = params[ 'selection_antibiotic' ]
    mutants = params[ 'mutants' ]

    # some bull shit recipes

    recipe_kinase_mix = [
        ( 'PNK_buffer', 'rs16pc9rd5sg5d', 3 ),
        ( 'water', 'rs17gmh5wafm5p', 18 ),
        ( 'polynucleotide_kinase', 'rs16pc9rd5hsf6', 1 ),
        ( '100mM_ATP', 'rs16pccshb6cb4', 1 ),
    ]

    recipe_anneal_mix = [
        ( 'DNA', params[ 'dna_aliquot'], ),
        ( '')
    ]

    recipe_polymerase_mix = [
        ( '', '', ),

            # reagents = {"buffer": {"resource_id": 'rs17sh5rzz79ct', "reagent_ratio": 0.6},
            #             "t4ligase": {"resource_id": 'rs16pc8krr6ag7', "reagent_ratio": 0.4},
            #             "t7polymerase": {"resource_id": 'rs16pca2urcz74', "reagent_ratio": 0.4},
            #             "dntp": {"resource_id": 'rs16pcb542c5rd', "reagent_ratio": 0.4}
            #             }
    ]

    # synthesize oligos into 96-well plate
    # minimum 24 mutants

    # synthetize oligos into tubes
    # and reformat into plate
    # expensive? more expensive then ordering dummy oligos?

    n_oligos = len( oligos )

    # provision kinase mix
    # into micro tube
    kin_mx = p.ref( 'kinase_mix', None, 'micro-2.0', discard=True )
    for ts_name, ts_id, vol in recipe_kinase_mix:
        p.provision( kin_mx.well(0), ts_id, '{}:microliter'.format( vol * n_oligos ) )

    # new plate for kinasing?
    kin_pt = p.ref( 'kinase_plate', None, 'micro-2.0', discard=True )
    wells_to_kinase = range( n_oligos )
    p.transfer( kin_mx, wells_to_kinase, '23:microliter' )
    p.stamp( oligo_pt, kin_pt, '7:microliter' )

    p.seal( kin_pt )
    p.incubate( kin_pt, 'warm_37', '1:hour' )

    # dilute and mix together oligos
    p.unseal( kinase_pt )
    dil_pt = p.ref( 'dilute_plate', None, '96-flat', discard=True )
    p.dispense_full_plate( dil_pt, 'water', '200:microliter' )
    #p.stamp( kin_pt, dil_pt, '2:microliter' ) for singles only!
    # for multiples, we have to do
    for mutant_label, oligos in mutants:
        for oligo_index in oligos:
            p.transfer( oligo_pt.well( ol_index ), dilute_pt.well( mutant_index ), '2:microliter' )
            # how annoying
    p.cover( dil_pt )
    p.spin( dil_pt, '2000:g', '10:second' )

    # anneal
    # make anneal master mix
    # create yet another new plate
    ann_pt = p.ref( 'anneal_plate', None, '384-pcr', storage='cold_20' )
    p.transfer( params[ 'dna_aliquot' ].well( 0 ), ann_pt.wells( range( n_mutants ) ), '2:microliter' )
    p.stamp( dil_pt, ann_pt, '2:microliter', mix_after=True )
    p.seal( ann_pt )
    p.spin( ann_pt, '2000:g', '10:second' )
    ramp = # a thermocylce ramp
    p.thermocycle( ann_pt, [{ 'cycles': 1, 'steps': ramp, 'volume': '5:microliter' }] )

    # polymerize
    p.unseal( ann_pt )
    p_mx = p.ref( 'polymerize_mix', None, 'micro-2.0', discard=True )
    for ts_name, ts_id, vol in recipe_kinase_mix:
        p.provision( p_mx.well(0), ts_id, '{}:microliter'.format( vol * n_oligos ) )
    p.transfer( p_mx.well(0), ann_pt.wells( range( n_mutants ) ), '2:microliter' )
    p.incubate( ann_pt, 'ambient', '90:minute' )

    # transform
    tr_pt = p.ref( "transformation_plate", None, "96-pcr", discard=True )
    p.incubate( tr_pt, "cold_20", "10:minute" )
    p.provision( "rs16pbjc4r7vvz", tr_pt.wells( range( n_mutants ) ), "10:microliter")
    p.stamp( ann_pt, tr_pt, '2:microliter' )
    p.seal( tr_pt )
    p.incubate( tr_pt, 'cold_4', '20:minute' )
    p.unseal( tr_pt )
    p.dispense_full_plate( transformation_plate, 'soc', '40:microliter' )
    p.seal( tr_pt )
    p.incubate( tr_pt, 'warm_37', '60:minute', shaking=True )

    # plate
    agar_plates = []
    agar_wells = WellGroup([])
    for well in range(0, len(transformation_wells), 6):
        agar_plate = ref_kit_container(p,
                                       "agar-%s_%s" % (len(agar_plates), printdatetime(time=False)),
                                       "6-flat",
                                       return_agar_plates(6)[params['growth_media']],
                                       discard=False, store='cold_4')
        agar_plates.append(agar_plate)
        for i, w in enumerate(transformation_wells[well:well + 6]):
            p.spread(w, agar_plate.well(i), "100:microliter")
            agar_wells.append(agar_plate.well(i).set_name(w.name))

    for agar_p in agar_plates:
        p.incubate( agar_p, 'warm_37', '12:hour' )
        p.image_plate( agar_p, mode='top', dataref=agar_p.name )

if __name__ == '__main__':
    from autoprotocol.harness import run
    run( bull_shit, 'bull_shit' )
