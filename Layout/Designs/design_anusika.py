from pya import *


def design_anusika(cell, cell_y, inst_wg1, inst_wg2, inst_wg3, waveguide_type):
    
    # load functions
    from SiEPIC.scripts import connect_pins_with_waveguide, connect_cell
    ly = cell.layout()
    library = ly.technology().name

    #####
    # designer circuit:

    # Create a physical text label so we can see under the microscope
    # How do we find out the PCell parameter variables?
    '''
    c = ly.create_cell('TEXT','Basic')
    [p.name for p in c.pcell_declaration().get_parameters() if c.is_pcell_variant]
    c.delete()
    '''
    # returns: ['text', 'font_name', 'layer', 'mag', 'inverse', 'bias', 'cspacing', 'lspacing', 'eff_cw', 'eff_ch', 'eff_lw', 'eff_dr', 'font']
    from SiEPIC.utils import get_technology_by_name
    TECHNOLOGY = get_technology_by_name(library)
    cell_text = ly.create_cell('TEXT', "Basic", {
        'text':cell.name,
        'layer': TECHNOLOGY['M1'],
        'mag': 30,
         })
    if not cell_text:
        raise Exception ('Cannot load text label cell; please check the script carefully.')
    cell.insert(CellInstArray(cell_text.cell_index(), Trans(Trans.R0, 25000,125000)))                

    # load the cells from the PDK
    # choose appropriate parameters
    cell_bragg = ly.create_cell('Bragg_grating', library, {
        'number_of_periods':30,
        'grating_period': 0.276,
        'corrugation_width': 0.05,
        'wg_width': 0.370,
        'sinusoidal': True})
    if not cell_bragg:
        raise Exception ('Cannot load Bragg grating cell; please check the script carefully.')
    

    cell_taper = ly.create_cell('taper', library, {
        'wg_width1': 0.35,
        'wg_width2': 0.37,
            })
    if not cell_taper:
        raise Exception ('Cannot load taper cell; please check the script carefully.')



    waveguide_type_370 = 'Strip 1310 nm, w=370 nm (core-clad)'

    # instantiate y-branch (attached to input waveguide)
    inst_y1 = connect_cell(inst_wg1, 'opt2', cell_y, 'opt2')


    #ybranch to taper
    inst_taper1 = connect_cell(inst_y1, 'opt1', cell_taper, 'pin1')

    # instantiate Bragg grating (attached to taper)
    inst_bragg1 = connect_cell(inst_taper1, 'pin2', cell_bragg, 'opt1')

    # instantiate Bragg grating (attached to the first Bragg grating)
    inst_bragg2 = connect_cell(inst_bragg1, 'opt2', cell_bragg, 'opt2')
    
    # move the Bragg grating to the right, and up
    inst_bragg2.transform(Trans(250000,130000))

    #####
    # Waveguides for the two outputs:
    connect_pins_with_waveguide(inst_y1, 'opt3', inst_wg3, 'opt1', waveguide_type=waveguide_type)


    #bragg to taper
    inst_taper2 = connect_cell(inst_bragg2, 'opt1', cell_taper, 'pin2')

    connect_pins_with_waveguide(inst_taper2, 'opt1', inst_wg2, 'opt1', waveguide_type=waveguide_type)
    
    '''
    make a long waveguide, back and forth,     
    >  = 2000 [microns]
    using "turtle" routing
    https://github.com/SiEPIC/SiEPIC-Tools/wiki/Scripted-Layout#adding-a-waveguide-between-components
    '''
    connect_pins_with_waveguide(inst_bragg1, 'opt2', inst_bragg2, 'opt2', waveguide_type=waveguide_type_370,
        turtle_A = [275,90,20,90,275,-90,20,-90,275,90,20,90,275,-90,20,-90, 275, 90, 20, 90, 275, -90, 20, -90] )

    return inst_wg1, inst_wg2, inst_wg3
