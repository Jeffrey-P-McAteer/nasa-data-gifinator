
import os
import sys

# Always run in location of this script, even is CWD started out as something different
os.chdir(
  os.path.dirname(__file__)
)

# Relative import
import data_fetcher


def main(args=sys.argv):

  if (not 'EARTHDATA_USERNAME' in os.environ) or (not 'EARTHDATA_PASSWORD' in os.environ):
    print('Asking for credentials b/c EARTHDATA_USERNAME and EARTHDATA_PASSWORD are not set')
    data_fetcher.earthaccess.login()

  #data_fetcher.earthaccess.
  results = data_fetcher.earthaccess.search_data(
      short_name='SEA_SURFACE_HEIGHT_ALT_GRIDS_L4_2SATS_5DAY_6THDEG_V_JPL2205',
      cloud_hosted=True,
      bounding_box=(-10, 20, 10, 50),
      temporal=("2018-02", "2019-03"),
      count=10
  )
  print(f'results = {results}')




if __name__ == '__main__':
  main()
