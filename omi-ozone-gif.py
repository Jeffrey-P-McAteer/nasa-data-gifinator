
import os
import sys
import datetime
import traceback

# Always run in location of this script, even is CWD started out as something different
os.chdir(
  os.path.dirname(__file__)
)

# Relative import
import data_fetcher

earthaccess = data_fetcher.earthaccess
h5py = data_fetcher.h5py
numpy = data_fetcher.numpy
PIL = data_fetcher.PIL

def print_recursive_hdf_tree(hdf, indent_str=''):
  try:
    for key in hdf.keys():
      print(f'{indent_str}{key}')
      print_recursive_hdf_tree(hdf[key], indent_str=indent_str+'>')
  except:
    if not 'object has no attribute' in traceback.format_exc():
      traceback.print_exc()
    else:
      print(f'{indent_str}{hdf}')


def hdf_dataset_by_name(hdf, dataset_name):
  try:
    for key in hdf.keys():
      if key.lower() == dataset_name.lower():
        return hdf[key]

      recursive_val = hdf_dataset_by_name(hdf[key], dataset_name)
      if not (recursive_val is None):
        return recursive_val
  except:
    if not 'object has no attribute' in traceback.format_exc():
      traceback.print_exc()
  return None


def main(args=sys.argv):

  if (not 'EARTHDATA_USERNAME' in os.environ) or (not 'EARTHDATA_PASSWORD' in os.environ):
    print('Asking for credentials b/c EARTHDATA_USERNAME and EARTHDATA_PASSWORD are not set')
    data_fetcher.earthaccess.login()

  dt_now = datetime.datetime.now()
  now_year = dt_now.year
  now_month = dt_now.month

  #data_fetcher.earthaccess.
  datasets = data_fetcher.earthaccess.search_datasets(
      keyword='Pollution Troposphere',
      cloud_hosted=False,
      temporal=(f'{now_year-1}-{now_month:02d}', f'{now_year}-{now_month:02d}'),
      count=100
  )

  mopitt_dataset = None
  for i, dataset in enumerate(datasets):
    #print(f'datasets[{i}] = {dataset}')
    dataset_native_id = dataset.get('meta', dict()).get('native-id', '')

    print('Dataset', i, '=', dataset_native_id)

    if 'MOPITT' in dataset_native_id and 'gridded daily means' in dataset_native_id:
      mopitt_dataset = dataset

  if mopitt_dataset is None:
    print(f'Error: Cannot find MOPITT from {len(datasets)} datasets searched!')
    return

  print('=' * 24)
  mopitt_native_id = mopitt_dataset.get('meta', dict()).get('native-id', '')
  print(f'mopitt_native_id = {mopitt_native_id}')
  concept_id = mopitt_dataset.get('meta', dict()).get('concept-id', '')
  print(f'concept_id={concept_id}')
  short_name = mopitt_dataset.get('umm', dict()).get('ShortName', '')
  print(f'short_name={short_name}')

  results = data_fetcher.earthaccess.search_data(
      # concept_id = concept_id,
      short_name = short_name,
      cloud_hosted = True,
      bounding_box = (-180, -90, 180, 90),
      temporal=(f'{now_year-1}-{now_month:02d}', f'{now_year}-{now_month:02d}'),
      count=100
  )

  for i, r in enumerate(results[:5]):
    print(f'results[{i}] = {results[i]}')

  print('=' * 24)

  data_dir = os.path.join(os.path.abspath('.'), 'data')
  os.makedirs(data_dir, exist_ok=True)
  downloaded_files = data_fetcher.earthaccess.download(
    results,
    local_path=data_dir,
  )
  print(f'Downloaded {len(downloaded_files)} files, such as {downloaded_files[:2]}')
  print()

  data_images = []
  for data_file in downloaded_files:
    hdf = h5py.File(data_file, 'r')
    #print(f'UNKNOWN {data_file} = {hdf}, keys = {hdf.keys()}')
    #print_recursive_hdf_tree(hdf)

    # Ought to be shaped (360, 180)
    RetrievedCOSurfaceMixingRatioDay = hdf_dataset_by_name(hdf, 'RetrievedCOSurfaceMixingRatioDay')
    RetrievedCOSurfaceMixingRatioNight = hdf_dataset_by_name(hdf, 'RetrievedCOSurfaceMixingRatioNight')

    # these two arrays use -9999 to indicate "no value", which we use with PIL for a transparency mask
    NumberofPixelsDay = hdf_dataset_by_name(hdf, 'NumberofPixelsDay')
    #print(f'NumberofPixelsDay = {NumberofPixelsDay[:]}')
    NumberofPixelsNight = hdf_dataset_by_name(hdf, 'NumberofPixelsNight')
    #print(f'NumberofPixelsNight = {NumberofPixelsNight[:]}')

    visible_px_measures = NumberofPixelsNight[:]
    visible_px_measures = numpy.rot90(visible_px_measures)

    img_array = RetrievedCOSurfaceMixingRatioNight[:]
    # Flip the img_array so 0,0 is the -180,90 degrees
    img_array = numpy.rot90(img_array)

    visible_px_mask = []
    for y in range(0, len(visible_px_measures)):
      visible_px_mask.append([])
      for x in range(0, len(visible_px_measures[y])):
        if int(visible_px_measures[y][x]) > -9999:
          visible_px_mask[y].append(0)
        else:
          visible_px_mask[y].append(254)

    measurements_img = PIL.Image.fromarray(img_array.astype('uint8'), 'L') # L = 8 bit grayscale, see https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
    measurements_img = measurements_img.convert('RGBA')

    transparency = PIL.Image.new('RGBA', (measurements_img.width, measurements_img.height), (0, 0, 0, 255))

    visible_px_img = PIL.Image.fromarray(numpy.array(visible_px_mask).astype('uint8'), 'L')

    final_img = PIL.Image.composite(transparency, measurements_img, visible_px_img)

    data_images.append(final_img)

    print('.', end='', flush=True)

    #img.save('yourimage.thumbnail', 'JPEG')
    #img.show()
    #input('Press Enter to continue')

  print()
  # Save to gif
  print(f'Saving {len(data_images)} frames to out.gif')
  img = data_images[0]
  img.save(fp='out.gif', format='GIF', append_images=data_images, save_all=True, transparency=0, duration=200, loop=0)





if __name__ == '__main__':
  main()
