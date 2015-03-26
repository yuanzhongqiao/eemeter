from eemeter.meter import PRISMMeter
from eemeter.models import TemperatureSensitivityModel
from eemeter.generator import ConsumptionGenerator
from eemeter.generator import generate_periods
from eemeter.consumption import ConsumptionHistory

from fixtures.weather import gsod_722880_2012_2014_weather_source
from fixtures.weather import tmy3_722880_weather_source

from numpy.testing import assert_allclose
import numpy as np

from datetime import datetime

RTOL = 1e-2
ATOL = 1e-2

import pytest

@pytest.fixture(params=[([-1, 1,14.5,8,17.8],True,6119.297438069778,0,"degC"),
                        ([10,2,15.5,1,19.5],True,4927.478974253085,0,"degC"),
                        ([0,2,18.8,7,22.2],True,3616.249477948155,0,"degC"),
                        ([0,2,65,3,71],True,4700.226534599519,0,"degF"),
                        ])
def prism_outputs_1(request):
    model = TemperatureSensitivityModel(cooling=True,heating=True)
    params = {
        "base_consumption": request.param[0][0],
        "heating_slope": request.param[0][1],
        "heating_reference_temperature": request.param[0][2],
        "cooling_slope": request.param[0][3],
        "cooling_reference_temperature": request.param[0][4]
    }
    start = datetime(2012,1,1)
    end = datetime(2014,12,31)
    retrofit_start_date = datetime(2013,6,1)
    retrofit_completion_date = datetime(2013,8,1)

    periods = generate_periods(start,end,jitter_intensity=0)
    gen = ConsumptionGenerator("electricity", "kWh", request.param[4], model, params)
    consumptions = gen.generate(gsod_722880_2012_2014_weather_source(), periods)
    fixture = ConsumptionHistory(consumptions), model.param_dict_to_list(params), \
            request.param[1], request.param[2], \
            request.param[3], request.param[4], \
            retrofit_start_date, retrofit_completion_date
    return fixture

@pytest.mark.slow
def test_princeton_scorekeeping_method(prism_outputs_1,
                                       gsod_722880_2012_2014_weather_source,
                                       tmy3_722880_weather_source):
    ch, elec_params, elec_presence, \
            elec_annualized_usage, elec_error, temp_unit, \
            retrofit_start_date, retrofit_completion_date = prism_outputs_1

    meter = PRISMMeter(temperature_unit_str=temp_unit)

    result = meter.evaluate(consumption_history=ch,
                            weather_source=gsod_722880_2012_2014_weather_source,
                            weather_normal_source=tmy3_722880_weather_source,
                            retrofit_start_date=retrofit_start_date,
                            retrofit_completion_date=retrofit_completion_date)

    assert_allclose(result['annualized_usage_electricity_post'], elec_annualized_usage, rtol=RTOL, atol=ATOL)
    assert_allclose(result['annualized_usage_electricity_pre'], elec_annualized_usage, rtol=RTOL, atol=ATOL)
    assert_allclose(result['cdd_65_tmy_post'], 1248.4575, rtol=RTOL, atol=ATOL)
    assert_allclose(result['cdd_65_tmy_pre'], 1248.4575, rtol=RTOL, atol=ATOL)
    assert result['consumption_history_no_estimated_post'] is not None
    assert result['consumption_history_no_estimated_pre'] is not None
    assert result['consumption_history_post'] is not None
    assert result['consumption_history_pre'] is not None
    assert result['cvrmse_electricity_post'] < 1e-2
    assert result['cvrmse_electricity_pre'] < 1e-2
    assert np.isnan(result['cvrmse_natural_gas_post'])
    assert np.isnan(result['cvrmse_natural_gas_pre'])
    assert result['daily_standard_error_electricity_post'] < 1e-2
    assert result['daily_standard_error_electricity_pre'] < 1e-2
    assert result['electricity_presence_post'] == True
    assert result['electricity_presence_pre'] == True
    assert result['has_enough_cdd_electricity_post'] == True
    assert result['has_enough_cdd_electricity_pre'] == True
    assert result['has_enough_cdd_natural_gas_post'] == True
    assert result['has_enough_cdd_natural_gas_pre'] == True
    assert result['has_enough_data_electricity_post'] == True
    assert result['has_enough_data_electricity_pre'] == True
    assert result['has_enough_data_natural_gas_post'] == False
    assert result['has_enough_data_natural_gas_pre'] == False
    assert result['has_enough_hdd_cdd_electricity_post'] == True
    assert result['has_enough_hdd_cdd_electricity_pre'] == True
    assert result['has_enough_hdd_cdd_natural_gas_post'] == False
    assert result['has_enough_hdd_cdd_natural_gas_pre'] == False
    assert result['has_enough_hdd_electricity_post'] == True
    assert result['has_enough_hdd_electricity_pre'] == True
    assert result['has_enough_hdd_natural_gas_post'] == False
    assert result['has_enough_hdd_natural_gas_pre'] == False
    assert result['has_enough_periods_with_high_cdd_per_day_electricity_post'] == True
    assert result['has_enough_periods_with_high_cdd_per_day_electricity_pre'] == True
    assert result['has_enough_periods_with_high_cdd_per_day_natural_gas_post'] == True
    assert result['has_enough_periods_with_high_cdd_per_day_natural_gas_pre'] == True
    assert result['has_enough_periods_with_high_hdd_per_day_electricity_post'] == True
    assert result['has_enough_periods_with_high_hdd_per_day_electricity_pre'] == True
    assert result['has_enough_periods_with_high_hdd_per_day_natural_gas_post'] == False
    assert result['has_enough_periods_with_high_hdd_per_day_natural_gas_pre'] == False
    assert result['has_enough_periods_with_low_cdd_per_day_electricity_post'] == True
    assert result['has_enough_periods_with_low_cdd_per_day_electricity_pre'] == True
    assert result['has_enough_periods_with_low_cdd_per_day_natural_gas_post'] == True
    assert result['has_enough_periods_with_low_cdd_per_day_natural_gas_pre'] == True
    assert result['has_enough_periods_with_low_hdd_per_day_electricity_post'] == True
    assert result['has_enough_periods_with_low_hdd_per_day_electricity_pre'] == True
    assert result['has_enough_periods_with_low_hdd_per_day_natural_gas_post'] == False
    assert result['has_enough_periods_with_low_hdd_per_day_natural_gas_pre'] == False
    assert result['has_enough_total_cdd_electricity_post'] == True
    assert result['has_enough_total_cdd_electricity_pre'] == True
    assert result['has_enough_total_cdd_natural_gas_post'] == True
    assert result['has_enough_total_cdd_natural_gas_pre'] == True
    assert result['has_enough_total_hdd_electricity_post'] == True
    assert result['has_enough_total_hdd_electricity_pre'] == True
    assert result['has_enough_total_hdd_natural_gas_post'] == False
    assert result['has_enough_total_hdd_natural_gas_pre'] == False
    assert result['has_recent_reading_electricity_post'] == True
    assert result['has_recent_reading_electricity_pre'] == True
    assert result['has_recent_reading_natural_gas_post'] == False
    assert result['has_recent_reading_natural_gas_pre'] == False
    assert_allclose(result['hdd_65_tmy_post'], 1578.58826087, rtol=RTOL, atol=ATOL)
    assert_allclose(result['hdd_65_tmy_pre'], 1578.58826087, rtol=RTOL, atol=ATOL)
    assert result['meets_cvrmse_limit_electricity_post'] == True
    assert result['meets_cvrmse_limit_electricity_pre'] == True
    assert result['meets_cvrmse_limit_natural_gas_post'] == False
    assert result['meets_cvrmse_limit_natural_gas_pre'] == False
    assert result['meets_model_calibration_utility_bill_criteria_electricity_post'] == True
    assert result['meets_model_calibration_utility_bill_criteria_electricity_pre'] == True
    assert result['meets_model_calibration_utility_bill_criteria_natural_gas_post'] == False
    assert result['meets_model_calibration_utility_bill_criteria_natural_gas_pre'] == False
    assert result['n_periods_high_cdd_per_day_electricity_post'] > 0
    assert result['n_periods_high_cdd_per_day_electricity_pre'] > 0
    assert result['n_periods_high_hdd_per_day_electricity_post'] > 0
    assert result['n_periods_high_hdd_per_day_electricity_pre'] > 0
    assert result['n_periods_low_cdd_per_day_electricity_post'] > 0
    assert result['n_periods_low_cdd_per_day_electricity_pre'] > 0
    assert result['n_periods_low_hdd_per_day_electricity_post'] > 0
    assert result['n_periods_low_hdd_per_day_electricity_pre'] > 0
    assert result['n_periods_high_cdd_per_day_natural_gas_post'] == 0
    assert result['n_periods_high_cdd_per_day_natural_gas_pre'] == 0
    assert result['n_periods_high_hdd_per_day_natural_gas_post'] == 0
    assert result['n_periods_high_hdd_per_day_natural_gas_pre'] == 0
    assert result['n_periods_low_cdd_per_day_natural_gas_post'] == 0
    assert result['n_periods_low_cdd_per_day_natural_gas_pre'] == 0
    assert result['n_periods_low_hdd_per_day_natural_gas_post'] == 0
    assert result['n_periods_low_hdd_per_day_natural_gas_pre'] == 0
    assert result['natural_gas_presence_post'] == False
    assert result['natural_gas_presence_pre'] == False
    assert result['spans_183_days_and_has_enough_hdd_cdd_electricity_post'] == True
    assert result['spans_183_days_and_has_enough_hdd_cdd_electricity_pre'] == True
    assert result['spans_183_days_and_has_enough_hdd_cdd_natural_gas_post'] == False
    assert result['spans_183_days_and_has_enough_hdd_cdd_natural_gas_pre'] == False
    assert result['spans_184_days_electricity_post'] == True
    assert result['spans_184_days_electricity_pre'] == True
    assert result['spans_184_days_natural_gas_post'] == False
    assert result['spans_184_days_natural_gas_pre'] == False
    assert result['spans_330_days_electricity_post'] == True
    assert result['spans_330_days_electricity_pre'] == True
    assert result['spans_330_days_natural_gas_post'] == False
    assert result['spans_330_days_natural_gas_pre'] == False
    assert_allclose(result['temp_sensitivity_params_electricity_post'], elec_params, rtol=RTOL, atol=ATOL)
    assert_allclose(result['temp_sensitivity_params_electricity_pre'], elec_params, rtol=RTOL, atol=ATOL)
    assert result['time_span_electricity_post'] == 480
    assert result['time_span_electricity_pre'] == 510
    assert result['time_span_natural_gas_post'] == 0
    assert result['time_span_natural_gas_pre'] == 0
    assert_allclose(result['total_cdd_electricity_post'], 2317.3998872, rtol=RTOL, atol=ATOL)
    assert_allclose(result['total_cdd_electricity_pre'], 1564.799914, rtol=RTOL, atol=ATOL)
    assert result['total_cdd_natural_gas_post'] == 0
    assert result['total_cdd_natural_gas_pre'] == 0
    assert_allclose(result['total_hdd_electricity_post'], 979.6000792, rtol=RTOL, atol=ATOL)
    assert_allclose(result['total_hdd_electricity_pre'], 2269.400118, rtol=RTOL, atol=ATOL)
    assert result['total_hdd_natural_gas_post'] == 0
    assert result['total_hdd_natural_gas_pre'] == 0

def test_prism_bad_temp_unit():

    with pytest.raises(ValueError):
        meter = PRISMMeter(temperature_unit_str="bad_unit")
