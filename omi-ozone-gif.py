
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
dateparser = data_fetcher.dateparser
dateutil = data_fetcher.dateutil
cv2 = data_fetcher.cv2


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

def read_date_from_metadata(core_metadata_str):
  for line in core_metadata_str.splitlines(keepends=False):
    tokens = line.split()
    for token in tokens:
      token = token.replace('"', '').replace('Z', '').strip()
      if len(token) > 0 and not token[0].isdigit():
        continue # performance bump skipping non-numeric tokens

      try:
        maybe_date = datetime.datetime.strptime(token.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        if not (maybe_date is None):
          return maybe_date
      except:
        #traceback.print_exc()
        pass

      # try:
      #   maybe_date = dateutil.parser.isoparse(token)
      #   if not (maybe_date is None):
      #     return maybe_date
      # except:
      #   #traceback.print_exc()
      #   pass

      # try:
      #   maybe_date = dateparser.parse(token)
      #   if not (maybe_date is None):
      #     return maybe_date
      # except:
      #   #traceback.print_exc()
      #   pass

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
      temporal=(f'{now_year-4}-{now_month:02d}', f'{now_year}-{now_month:02d}'),
      count=9000000
  )

  for i, r in enumerate(results[:5]):
    print(f'results[{i}] = {results[i]}')

  print('=' * 24)

  #data_dir = os.path.join(os.path.abspath('.'), 'data')
  data_dir = os.environ.get('DATA_DIR', '/mnt/scratch/science-data/MOPITT')
  print(f'Storing all data in DATA_DIR = {data_dir}')
  os.makedirs(data_dir, exist_ok=True)
  downloaded_files = data_fetcher.earthaccess.download(
    results,
    local_path=data_dir,
  )
  print(f'Downloaded {len(downloaded_files)} files, such as {downloaded_files[:2]}')
  print()

  # We store a list of [(date-time, image)] so we can sort later by timestamp before joining into final gif
  data_images = []
  for data_file in downloaded_files:
    hdf = h5py.File(data_file, 'r')
    #print(f'UNKNOWN {data_file} = {hdf}, keys = {hdf.keys()}')
    #print_recursive_hdf_tree(hdf)

    #struct_metadata = hdf['HDFEOS INFORMATION']['StructMetadata.0']
    #print(f'struct_metadata = {struct_metadata}')

    core_metadata = hdf['HDFEOS INFORMATION']['coremetadata.0']
    core_metadata_array_or_single_string = core_metadata.asstr()[()]
    if isinstance(core_metadata_array_or_single_string, list) or isinstance(core_metadata_array_or_single_string, tuple):
      core_metadata_str = '\n'.join(core_metadata_array_or_single_string)
    elif isinstance(core_metadata_array_or_single_string, numpy.ndarray):
      core_metadata_str = ''.join([row_str for row_str in core_metadata_array_or_single_string])
    else:
      core_metadata_str = core_metadata_array_or_single_string

    #print(f'core_metadata_str = {core_metadata_str}')
    data_capture_date = read_date_from_metadata(core_metadata_str)
    if data_capture_date is None:
      print(f'core_metadata_str = {core_metadata_str}')
      input('STOP, data_capture_date is None! Inspect & fix me pls -_-')
    #print(f'data_capture_date = {data_capture_date}')

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

    # Add date time to lower-left of image
    draw = PIL.ImageDraw.Draw(final_img)
    timestamp_str = f'{data_capture_date}'

    text_height_px = 16
    text_width_px = 136

    draw.rectangle(
      ((0, final_img.height - text_height_px), (text_width_px, final_img.height)), fill=(250,250,250)
    )
    draw.text((0, final_img.height - text_height_px), timestamp_str, fill=(9,9,9), font_size=14)

    # Also add a title on all frames
    draw.rectangle(
      ((0, 0), (240, 16)), fill=(250,250,250)
    )
    draw.text(
      (9, 0),
      'Retrieved CO Surface Mixing Ratio Night',
      fill=(0,0,0),
      font_size=14
    )
    draw.text(
      (10, 0),
      'Retrieved CO Surface Mixing Ratio Night',
      fill=(128,128,128),
      font_size=14
    )

    draw = None

    # Finally turn all TRULY BLACK pixels transpatent, b/c that's what the data says.
    pixdata = final_img.load()
    width, height = final_img.size
    for y in range(height):
        for x in range(width):
            if (pixdata[x, y][0] + pixdata[x, y][1] + pixdata[x, y][2]) <= 3:
                pixdata[x, y] = (0, 0, 0, 0) # make black & alpha

    pixdata = None

    # final_img.show()
    # input('Enter for next')

    data_images.append(
      (data_capture_date, final_img)
    )

    print('.', end='', flush=True)

    #img.save('yourimage.thumbnail', 'JPEG')
    #img.show()
    #input('Press Enter to continue')

  # Use the date to sort oldest -> newest
  data_images.sort(key=lambda val: val[0])

  # Then get rid of the dates
  data_images = [val[1] for val in data_images]

  print()
  # Save to gif
  print(f'Saving {len(data_images)} frames to out.gif')
  img = data_images[0]
  img.save(
    fp='out.gif',
    format='GIF',
    append_images=data_images,
    save_all=True,
    transparency=0,
    duration=180, # ms to display a single frame for
    loop=0,
    optimize=False,
    lossless=True
  )

  # Also save to .avi file on the assumption quality will be far better somehow
  print(f'Saving {len(data_images)} frames to out.avi')
  FPS = 8
  frame_repeats = 1
  fourcc = cv2.VideoWriter.fourcc(*'MJPG')
  out = cv2.VideoWriter('out.avi', fourcc, FPS, (img.width, img.height))

  # Just paste from 0..i and call that the image
  image = PIL.Image.new('RGBA', data_images[0].size)
  for i in range(0, len(data_images)):
    image.alpha_composite(data_images[i])

    #image.show()
    #input('Next frame')

    cv_img = cv2.cvtColor(numpy.array( image.convert('RGB') ), cv2.COLOR_RGB2BGR)
    for _ in range(0, frame_repeats):
      out.write(cv_img)

  out.release()







if __name__ == '__main__':
  main()
