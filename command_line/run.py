from __future__ import division

from iotbx.detectors import ImageFactory
from cctbx.array_family import flex
from cctbx import uctbx, sgtbx
from iotbx import ccp4_map, phil
import recviewer
import math

# FIXME: make this into a class!

def fill_voxels(image, grid, cnts, S, xy, reverse_phi=False, rec_range=0.1):
    raw = image.get_raw_data()
    npoints = grid.all()[0]
    step = 2 * rec_range / npoints
    axis = image.get_goniometer().get_rotation_axis()
    osc_range = image.get_scan().get_oscillation_range()
    print " Oscillation range:", osc_range
    angle = (osc_range[0] + osc_range[1]) / 2 / 180 * math.pi # should take the average?
    if (reverse_phi == False):
      angle *= -1
    rotated_S = S.rotate_around_origin(axis, angle)

    recviewer.fill_voxels(image.get_raw_data(), grid, cnts, rotated_S, xy, rec_range)

def main(filenames, map_file, npoints=192, max_resolution=6, reverse_phi=False):
    rec_range = 1 / max_resolution

    image = ImageFactory(filenames[0])
    panel = image.get_detector()[0]
    beam = image.get_beam()
    s0 = beam.get_s0()
    pixel_size = panel.get_pixel_size()
    
    xlim, ylim = image.get_raw_data().all()
    
    xy = recviewer.get_target_pixels(panel, s0, xlim, ylim, max_resolution)
    
    s1 = panel.get_lab_coord(xy * pixel_size[0]) # FIXME: assumed square pixel
    s1 = s1 / s1.norms() * (1 / beam.get_wavelength()) # / is not supported...
    S = s1 - s0
    
    grid = flex.double(flex.grid(npoints, npoints, npoints), 0)
    cnts = flex.int(flex.grid(npoints, npoints, npoints), 0)
    
    for filename in filenames:
        print "Processing image", filename
        try:
            fill_voxels(ImageFactory(filename), grid, cnts, S, xy, reverse_phi, rec_range)
        except:
            print " Failed to process. Skipped this."
        
    recviewer.normalize_voxels(grid, cnts)
    
    uc = uctbx.unit_cell((npoints, npoints, npoints, 90, 90, 90))
    ccp4_map.write_ccp4_map(map_file, uc, sgtbx.space_group("P1"), 
                            (0, 0, 0), grid.all(), grid, 
                            flex.std_string(["cctbx.miller.fft_map"]))
    return
    from scitbx import fftpack
    fft = fftpack.complex_to_complex_3d(grid.all())
    grid_complex = flex.complex_double(
                            reals=flex.pow2(grid),
                            imags=flex.double(grid.size(), 0))
    grid_transformed = flex.abs(fft.backward(grid_complex))
    print flex.max(grid_transformed), flex.min(grid_transformed), grid_transformed.all()
    ccp4_map.write_ccp4_map(map_file, uc, sgtbx.space_group("P1"), 
                            (0, 0, 0), grid.all(), grid_transformed,
                            flex.std_string(["cctbx.miller.fft_map"]))
#    self.grid_real = flex.pow2(fft.forward(grid_transformed))
    


if __name__ == '__main__':
    import sys

# TODO use phil
    master_phil=phil.parse("""
recviewer
  .short_caption = Reciprocal space viewer
{
  map_file = None
    .type = path
    .optional = False
    .multiple=True
    .short_caption = Map file
  max_resolution = 6
    .type = float
    .optional = True
    .short_caption = Resolution limit
  grid_size = 192
    .type = int
    .optional = True
}
""")
    
#    working_phil = master_phil.command_line_argument_interpreter().process(sys.argv[1])
#    working_phil.show()
#    params = working_phil.extract()
#    print params
#    print params.recviewer.map_file
#    print params.recviewer.max_resolution

    from optparse import *
    parser = OptionParser("recviewer.run --map_file output.ccp4 [--max_resolution 6] [--grid_size 192] [--reverse_phi] images.cbf")

    parser.add_option("", "--map_file",  type="string", help="output filename")
    parser.add_option("", "--max_resolution", type="float", default=6, help="maximum resolution")
    parser.add_option("", "--grid_size", type="int", default=192, help="map grid size")
    parser.add_option("", "--reverse_phi", action="store_true", default=False, help="Reverse PHI")
    (options, args) = parser.parse_args()

    if not options.map_file:
        parser.error("Requires output map file.")
        os.exit()

    if not args:
        parser.error("Requires input images.")
        os.exit()

    main(filenames=args, npoints=options.grid_size, max_resolution=options.max_resolution, 
         reverse_phi=options.reverse_phi, map_file=options.map_file)
