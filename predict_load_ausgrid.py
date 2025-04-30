from datetime import datetime, timedelta

from netload.substation_model import SubstationModel

import matplotlib.pyplot as plt

plt.close('all')

node_data = [
    ('Adamstown 132', (-32.93490969062761, 151.7364111591307)),
#      ('Broadmeadow 132', (-32.91742111204283, 151.73184867499018)),
#      ('Cardiff 33', (-32.941661895591686, 151.6534628948583)),
#      ('Charlestown 132', (-32.958684874625284, 151.6940820739581)),
#      ('Gateshead 33', (-32.983996882802224, 151.69326131694598)),
#      ('Jesmond 132', (-32.898767842329306, 151.68494548321712)),
#      ('Kotara 33', (-32.937930862419485, 151.7123859120546)),
#      ('Mayfield West 132', (-32.892075276835016, 151.72253625252856)),
#      ('Mt Hutton 33', (-32.98473498536307, 151.66198208136797)),
#      ('Newcastle CBD 33', (-32.92931782266567, 151.77520269442377)),
#      ('Pelican 33', (-33.06297816847511, 151.65244145438717)),
#      ('Swansea 33', (-33.0971327086669766, 151.63799946232353))
]

start_date = datetime(2021, 1, 1, 23) + timedelta(hours=16)
end_date = datetime(2022, 1, 1, 23) + timedelta(hours=16)

sub_model = SubstationModel('model6', node_data,
                            start_date,
                            end_date)

sub_model.forecast_node('Adamstown 132')
