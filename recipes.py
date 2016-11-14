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

# thermal cycle ramp
ramp = [ { 'duration': '60:second', 'temperature': '{}:celsius'.format( 95 - i ) } for i in range( 70 ) ]

# solid media selection antibiotics
choices = {
    "kanamycin": "ki17rs7j799zc2",
    "ampicillin": "ki17sbb845ssx9",
}
