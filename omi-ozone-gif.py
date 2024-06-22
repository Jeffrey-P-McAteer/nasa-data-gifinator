
import os
import sys
import datetime

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
  print(f'Downloaded {len(downloaded_files)} files, such as {downloaded_files[:3]}')
  print()




if __name__ == '__main__':
  main()
