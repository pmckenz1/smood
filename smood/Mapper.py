#!/usr/bin/env python

from pygbif import species
from pygbif import occurrences as occ
import numpy as np
import os
import rasterio
from IPython.display import Image
from shutil import rmtree
from .Maxent import Maxent


class Mapper:
    """
    The object central to `smood` (simple mapping of occurrence data).
    """
    def __init__(
        self,
        sp_name=None,
        lat_range=None,
        lon_range=None,
        worldclim_layers=list(range(1, 20)),
        outputs_dir="maxent_outputs/",
        write_outputs=False,
        maxent_path=None,
        worldclim_dir=None,
        ):
        """
        The object central to `smood` (simple mapping of occurrence data).
        Users supply a species name, latitude range, and longitude range, and
        then they can run automated maxent sdms over this.


        Parameters:
        -----------
        species_name (str):
            The name of the species.
            e.g., "Monarda fistulosa"

        lat_range (list, tuple):
            A list of the latitude values, low and high, used as bounds for the map.
            e.g., (30, 50)
            Values must be from the range [-90,90]
            These values are sorted later on, so the order doesn't matter.

        lon_range (list, tuple):
            A list of the longitude values, low and high, used as bounds for the map.
            e.g., (-100, -50)
            Values must be from the range [-180,180]
            These values are sorted later on, so the order doesn't matter.

        worldclim_layers (list):
            A list of the layers to use from worldclim. By default, this list contains
            integers 1 through 19, corresponding to all 19 worldclime layers.

        """

        self.profile = {}
        if sp_name:
            self.profile['spname'] = sp_name
        else:
            self.profile['spname'] = None

        if lat_range:
            _ = np.sort(lat_range)
            self.profile['ymin'] = _[0]
            self.profile['ymax'] = _[1]
        else:
            self.profile['ymin'] = None
            self.profile['ymax'] = None

        if lon_range:
            _ = np.sort(lon_range)
            self.profile['xmin'] = _[0]
            self.profile['xmax'] = _[1]
        else:
            self.profile['xmin'] = None
            self.profile['xmax'] = None

        self.upper_package_level = os.path.join(
                                                os.path.dirname(
                                                                os.path.dirname(__file__)
                                                                )
                                                )
        if not maxent_path:
            # make the maxent path give the path to the .jar in the package directory...
            self.maxent_path = os.path.join(self.upper_package_level,
                                            'bins',
                                            'maxent.jar')
        else:
            self.maxent_path = maxent_path

        if not worldclim_dir:
            self.worldclim_dir = os.path.join(self.upper_package_level,
                                              'worldclim')
        else:
            self.worldclim_dir = worldclim_dir

        self.worldclim_dict = {
            1:  os.path.join(self.worldclim_dir, "wc2.0_bio_10m_01.tif"),
            2:  os.path.join(self.worldclim_dir, "wc2.0_bio_10m_02.tif"),
            3:  os.path.join(self.worldclim_dir, "wc2.0_bio_10m_03.tif"),
            4:  os.path.join(self.worldclim_dir, "wc2.0_bio_10m_04.tif"),
            5:  os.path.join(self.worldclim_dir, "wc2.0_bio_10m_05.tif"),
            6:  os.path.join(self.worldclim_dir, "wc2.0_bio_10m_06.tif"),
            7:  os.path.join(self.worldclim_dir, "wc2.0_bio_10m_07.tif"),
            8:  os.path.join(self.worldclim_dir, "wc2.0_bio_10m_08.tif"),
            9:  os.path.join(self.worldclim_dir, "wc2.0_bio_10m_09.tif"),
            10: os.path.join(self.worldclim_dir, "wc2.0_bio_10m_10.tif"),
            11: os.path.join(self.worldclim_dir, "wc2.0_bio_10m_11.tif"),
            12: os.path.join(self.worldclim_dir, "wc2.0_bio_10m_12.tif"),
            13: os.path.join(self.worldclim_dir, "wc2.0_bio_10m_13.tif"),
            14: os.path.join(self.worldclim_dir, "wc2.0_bio_10m_14.tif"),
            15: os.path.join(self.worldclim_dir, "wc2.0_bio_10m_15.tif"),
            16: os.path.join(self.worldclim_dir, "wc2.0_bio_10m_16.tif"),
            17: os.path.join(self.worldclim_dir, "wc2.0_bio_10m_17.tif"),
            18: os.path.join(self.worldclim_dir, "wc2.0_bio_10m_18.tif"),
            19: os.path.join(self.worldclim_dir, "wc2.0_bio_10m_19.tif"),
        }

        if worldclim_layers:
            self.profile['worldclim_layers'] = worldclim_layers

        # name folder for maxent outputs
        self.outputs_dir = outputs_dir

        # name folder for clipped/converted worldclim
        self.envfiles_dir = os.path.join(self.outputs_dir,
                                         "envfiles")

        self.key = None
        self.write_outputs = write_outputs

    def _get_gbif_occs(self):
        # get the gbif key for our species
        self.occfile = os.path.join(self.outputs_dir,
                                    self.profile['spname'].replace(" ",
                                                                   "_")+".csv")
        if not self.key:
            self.key = species.name_backbone(name=self.profile['spname'],
                                             rank='species')['usageKey']

        # make lists to fill
        self.lats = []
        self.lons = []

        # cycle through observations, filling lists of lat and lon
        curr_offset = 0
        end_records = False
        while not end_records:
            occ_records = occ.search(taxonKey=self.key,
                                     hasCoordinate=True,
                                     decimalLatitude=','.join([str(self.profile['ymin']),
                                                               str(self.profile['ymax'])]),
                                     decimalLongitude=','.join([str(self.profile['xmin']),
                                                                str(self.profile['xmax'])]),
                                     offset=curr_offset)
            end_records = occ_records['endOfRecords']
            curr_offset += occ_records['limit']

            self.lons.extend([i['decimalLongitude'] for i in occ_records['results']])
            self.lats.extend([i['decimalLatitude'] for i in occ_records['results']])

        # prepare array to write to csv
        csvarr = np.vstack([np.repeat(self.profile['spname'].replace(" ", "_"), len(self.lons)),
                            self.lons,
                            ["{}{}".format(a_, b_) for a_, b_ in zip(self.lats, 
                                                                     np.repeat('\n', 
                                                                               len(self.lats)
                                                                               )
                                                                     )
                             ]
                            ]).T
        # write occurrence data to csv
        with open(self.occfile, 'w') as f:
            f.write('Species,Longitude,Latitude\n')
            for line in csvarr:
                f.write(",".join(line))

        # make these easier to work with downstream
        self.lons = np.array(self.lons)
        self.lats = np.array(self.lats)

    def _write_env_rasters(self):
        """
        Looks at raw worldclim data, clips it to specified bounding box, and writes the result as ascii.
        """
        # loop through the worldclim master files
        for idx, filepath in enumerate([self.worldclim_dict[layer_int] for layer_int in self.profile['worldclim_layers']]):
            # open with rasterio
            envdata = rasterio.open(filepath, 'r')

            # define a window using lat and lon
            win1 = envdata.window(self.profile['xmin'],
                                  self.profile['ymin'],
                                  self.profile['xmax'],
                                  self.profile['ymax'])

            # read env data from the window
            windowarr = envdata.read(window=win1)[0]

            # get affine transform (this will be used to get cell size)
            aff = envdata.profile['transform']

            # get number of columns in the window
            ncols = windowarr.shape[1]

            # get number of rows in the window
            nrows = windowarr.shape[0]

            # define the lower left corner x coordinate (in degrees)
            xllcorner = self.profile['xmin']

            # define the lower left corner y coordinate (in degrees)
            yllcorner = self.profile['ymin']

            # save the cell size from the affine transform
            cellsize = aff.a

            # record the value corresponding to nodata
            nodata_value = envdata.profile['nodata']

            # save ascii file -- saving array with space delimiter, and metadata as a header
            np.savetxt(os.path.join(self.envfiles_dir,
                                    str(idx)+'.asc'),
                       windowarr,
                       delimiter=' ',
                       comments='',
                       header="".join(['ncols {}\n'.format(ncols),
                                       'nrows {}\n'.format(nrows),
                                       'xllcorner {}\n'.format(xllcorner),
                                       'yllcorner {}\n'.format(yllcorner),
                                       'cellsize {}\n'.format(cellsize),
                                       'nodata_value {}'.format(nodata_value)]))

    def run(self):
        """
        Runs gbif and maxent on the species name and bounds provided.
        """

        # make these directories
        os.mkdir(self.outputs_dir)
        os.mkdir(self.envfiles_dir)

        self._get_gbif_occs()
        self._write_env_rasters()

        # run maxent from command line

        mkseq = Maxent(self.maxent_path)
        mkseq.open_subprocess()
        mkseq.feed_maxent(self.envfiles_dir,
                          self.occfile,
                          self.outputs_dir,
                          )
        mkseq.close_subprocess()

        # save png output from maxent
        self.maxent_image = Image(os.path.join(self.outputs_dir,
                                               "plots",
                                               self.profile['spname'].replace(" ", "_")+".png"))

        # save raster output from maxent
        self.density_mat = np.genfromtxt(os.path.join(self.outputs_dir,
                                                      self.profile['spname'].replace(" ",
                                                                                     "_")+".asc"),
                                         delimiter=' ',
                                         skip_header=6)
        # remove the nans (maxent saves these as -9999)
        self.density_mat[self.density_mat == -9999] = np.nan

        # remove the outputs, we have what we need in memory
        if not self.write_outputs:
            rmtree(self.outputs_dir)
