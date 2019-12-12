package main

import (
	"fmt"
	"github.com/gtfierro/xboswave/ingester/types"
	xbospb "github.com/gtfierro/xboswave/proto"
)

func has_device(msg xbospb.XBOS) bool {
	return msg.ParkerState != nil
}

var device_units = map[string]string{
    "p3": "",
    "r3": "",
    "c2": "",
    "c3": "",
    "c4": "",
    "c5": "",
    "c6": "",
    "c7": "",
    "c8": "",
    "c9": "",
    "d1": "",
    "d2": "",
    "d4": "",
    "d9": "C",
    "da": "minutes",
    "compressor_working_hours": "hours",
    "clear_compressor_working_hours": "",
    "buzzer_control": "",
    "defrost_control": "",
    "start_resistors": "",
    "on_standby_status": "",
    "light_status": "",
    "aux_output_status": "",
    "next_defrost_counter": "seconds",
    "door_switch_input_status": "",
    "multipurpose_input_status": "",
    "compressor_status": "",
    "output_defrost_status": "",
    "fans_status": "",
    "output_k4_status": "",
    "cabinet_temperature": "C",
    "evaporator_temperature": "C",
    "auxiliary_temperature": "C",
    "probe1_failure_alarm": "",
    "probe2_failure_alarm": "",
    "probe3_failure_alarm": "",
    "minimum_temperature_alarm": "",
    "maximum_temperture_alarm": "",
    "condensor_temperature_failure_alarm": "",
    "condensor_pre_alarm": "",
    "door_alarm": "",
    "multipurpose_input_alarm": "",
    "compressor_blocked_alarm": "",
    "power_failure_alarm": "",
    "rtc_error_alarm": "",
    "energy_saving_regulator_flag": "",
    "energy_saving_real_time_regulator_flag": "",
    "service_request_regulator_flag": "",
    "on_standby_regulator_flag": "",
    "new_alarm_to_read_regulator_flag": "",
    "defrost_status_regulator_flag": "",
    "active_setpoint": "C",
    "time_until_defrost": "seconds",
    "current_defrost_counter": "seconds",
    "compressor_delay": "seconds",
    "num_alarms_in_history": "",
    "energy_saving_status": "",
    "service_request_status": "",
    "resistors_activated_by_aux_key_status": "",
    "evaporator_valve_state": "",
    "output_defrost_state": "",
    "output_lux_state": "",
    "output_aux_state": "",
    "resistors_state": "",
    "output_alarm_state": "",
    "second_compressor_state": "",
    "setpoint": "",
    "p2": "",
    "r0": "C",
    "r1": "C",
    "r2": "C",
    "r4": "",
    "c0": "minutes",
    "c1": "minutes",
    "d0": "hours",
    "d3": "minutes",
    "d5": "minutes",
    "d7": "minutes",
    "d8": "",
    "a0": "",
    "a1": "C",
    "a2": "",
    "a3": "",
    "a4": "C",
    "a5": "",
    "a6": "minutes",
    "a7": "minutes",
    "a8": "minutes",
    "a9": "minutes",
    "f0": "",
    "f1": "C",
    "f2": "",
    "f3": "minutes",
    "hd1": "minutes",
    "hd2": "minutes",
    "hd3": "minutes",
    "hd4": "minutes",
    "hd5": "minutes",
    "hd6": "minutes ",
}
var device_lookup = map[string]func(msg xbospb.XBOS) (float64, bool){
    "p3": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.P3 != nil {
            return float64(msg.ParkerState.P3.Value), true
        }
        return 0, false
    },
    "r3": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.R3 != nil {
            return float64(msg.ParkerState.R3.Value), true
        }
        return 0, false
    },
    "c2": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.C2 != nil {
            return float64(msg.ParkerState.C2.Value), true
        }
        return 0, false
    },
    "c3": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.C3 != nil {
            return float64(msg.ParkerState.C3.Value), true
        }
        return 0, false
    },
    "c4": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.C4 != nil {
            return float64(msg.ParkerState.C4.Value), true
        }
        return 0, false
    },
    "c5": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.C5 != nil {
            return float64(msg.ParkerState.C5.Value), true
        }
        return 0, false
    },
    "c6": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.C6 != nil {
            return float64(msg.ParkerState.C6.Value), true
        }
        return 0, false
    },
    "c7": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.C7 != nil {
            return float64(msg.ParkerState.C7.Value), true
        }
        return 0, false
    },
    "c8": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.C8 != nil {
            return float64(msg.ParkerState.C8.Value), true
        }
        return 0, false
    },
    "c9": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.C9 != nil {
            return float64(msg.ParkerState.C9.Value), true
        }
        return 0, false
    },
    "d1": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.D1 != nil {
            return float64(msg.ParkerState.D1.Value), true
        }
        return 0, false
    },
    "d2": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.D2 != nil {
            return float64(msg.ParkerState.D2.Value), true
        }
        return 0, false
    },
    "d4": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.D4 != nil {
            return float64(msg.ParkerState.D4.Value), true
        }
        return 0, false
    },
    "d9": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.D9 != nil {
            return float64(msg.ParkerState.D9.Value), true
        }
        return 0, false
    },
    "da": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.Da != nil {
            return float64(msg.ParkerState.Da.Value), true
        }
        return 0, false
    },
    "compressor_working_hours": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.CompressorWorkingHours != nil {
            return float64(msg.ParkerState.CompressorWorkingHours.Value), true
        }
        return 0, false
    },
    "clear_compressor_working_hours": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.ClearCompressorWorkingHours != nil {
            return float64(msg.ParkerState.ClearCompressorWorkingHours.Value), true
        }
        return 0, false
    },
    "buzzer_control": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.BuzzerControl != nil {
            return float64(msg.ParkerState.BuzzerControl.Value), true
        }
        return 0, false
    },
    "defrost_control": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.DefrostControl != nil {
            return float64(msg.ParkerState.DefrostControl.Value), true
        }
        return 0, false
    },
    "start_resistors": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.StartResistors != nil {
            return float64(msg.ParkerState.StartResistors.Value), true
        }
        return 0, false
    },
    "on_standby_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.OnStandbyStatus != nil {
            return float64(msg.ParkerState.OnStandbyStatus.Value), true
        }
        return 0, false
    },
    "light_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.LightStatus != nil {
            return float64(msg.ParkerState.LightStatus.Value), true
        }
        return 0, false
    },
    "aux_output_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.AuxOutputStatus != nil {
            return float64(msg.ParkerState.AuxOutputStatus.Value), true
        }
        return 0, false
    },
    "next_defrost_counter": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.NextDefrostCounter != nil {
            return float64(msg.ParkerState.NextDefrostCounter.Value), true
        }
        return 0, false
    },
    "door_switch_input_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.DoorSwitchInputStatus != nil {
            return float64(msg.ParkerState.DoorSwitchInputStatus.Value), true
        }
        return 0, false
    },
    "multipurpose_input_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.MultipurposeInputStatus != nil {
            return float64(msg.ParkerState.MultipurposeInputStatus.Value), true
        }
        return 0, false
    },
    "compressor_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.CompressorStatus != nil {
            return float64(msg.ParkerState.CompressorStatus.Value), true
        }
        return 0, false
    },
    "output_defrost_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.OutputDefrostStatus != nil {
            return float64(msg.ParkerState.OutputDefrostStatus.Value), true
        }
        return 0, false
    },
    "fans_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.FansStatus != nil {
            return float64(msg.ParkerState.FansStatus.Value), true
        }
        return 0, false
    },
    "output_k4_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.OutputK4Status != nil {
            return float64(msg.ParkerState.OutputK4Status.Value), true
        }
        return 0, false
    },
    "cabinet_temperature": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.CabinetTemperature != nil {
            return float64(msg.ParkerState.CabinetTemperature.Value), true
        }
        return 0, false
    },
    "evaporator_temperature": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.EvaporatorTemperature != nil {
            return float64(msg.ParkerState.EvaporatorTemperature.Value), true
        }
        return 0, false
    },
    "auxiliary_temperature": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.AuxiliaryTemperature != nil {
            return float64(msg.ParkerState.AuxiliaryTemperature.Value), true
        }
        return 0, false
    },
    "probe1_failure_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.Probe1FailureAlarm != nil {
            return float64(msg.ParkerState.Probe1FailureAlarm.Value), true
        }
        return 0, false
    },
    "probe2_failure_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.Probe2FailureAlarm != nil {
            return float64(msg.ParkerState.Probe2FailureAlarm.Value), true
        }
        return 0, false
    },
    "probe3_failure_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.Probe3FailureAlarm != nil {
            return float64(msg.ParkerState.Probe3FailureAlarm.Value), true
        }
        return 0, false
    },
    "minimum_temperature_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.MinimumTemperatureAlarm != nil {
            return float64(msg.ParkerState.MinimumTemperatureAlarm.Value), true
        }
        return 0, false
    },
    "maximum_temperture_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.MaximumTempertureAlarm != nil {
            return float64(msg.ParkerState.MaximumTempertureAlarm.Value), true
        }
        return 0, false
    },
    "condensor_temperature_failure_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.CondensorTemperatureFailureAlarm != nil {
            return float64(msg.ParkerState.CondensorTemperatureFailureAlarm.Value), true
        }
        return 0, false
    },
    "condensor_pre_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.CondensorPreAlarm != nil {
            return float64(msg.ParkerState.CondensorPreAlarm.Value), true
        }
        return 0, false
    },
    "door_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.DoorAlarm != nil {
            return float64(msg.ParkerState.DoorAlarm.Value), true
        }
        return 0, false
    },
    "multipurpose_input_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.MultipurposeInputAlarm != nil {
            return float64(msg.ParkerState.MultipurposeInputAlarm.Value), true
        }
        return 0, false
    },
    "compressor_blocked_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.CompressorBlockedAlarm != nil {
            return float64(msg.ParkerState.CompressorBlockedAlarm.Value), true
        }
        return 0, false
    },
    "power_failure_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.PowerFailureAlarm != nil {
            return float64(msg.ParkerState.PowerFailureAlarm.Value), true
        }
        return 0, false
    },
    "rtc_error_alarm": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.RtcErrorAlarm != nil {
            return float64(msg.ParkerState.RtcErrorAlarm.Value), true
        }
        return 0, false
    },
    "energy_saving_regulator_flag": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.EnergySavingRegulatorFlag != nil {
            return float64(msg.ParkerState.EnergySavingRegulatorFlag.Value), true
        }
        return 0, false
    },
    "energy_saving_real_time_regulator_flag": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.EnergySavingRealTimeRegulatorFlag != nil {
            return float64(msg.ParkerState.EnergySavingRealTimeRegulatorFlag.Value), true
        }
        return 0, false
    },
    "service_request_regulator_flag": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.ServiceRequestRegulatorFlag != nil {
            return float64(msg.ParkerState.ServiceRequestRegulatorFlag.Value), true
        }
        return 0, false
    },
    "on_standby_regulator_flag": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.OnStandbyRegulatorFlag != nil {
            return float64(msg.ParkerState.OnStandbyRegulatorFlag.Value), true
        }
        return 0, false
    },
    "new_alarm_to_read_regulator_flag": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.NewAlarmToReadRegulatorFlag != nil {
            return float64(msg.ParkerState.NewAlarmToReadRegulatorFlag.Value), true
        }
        return 0, false
    },
    "defrost_status_regulator_flag": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.DefrostStatusRegulatorFlag != nil {
            return float64(msg.ParkerState.DefrostStatusRegulatorFlag.Value), true
        }
        return 0, false
    },
    "active_setpoint": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.ActiveSetpoint != nil {
            return float64(msg.ParkerState.ActiveSetpoint.Value), true
        }
        return 0, false
    },
    "time_until_defrost": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.TimeUntilDefrost != nil {
            return float64(msg.ParkerState.TimeUntilDefrost.Value), true
        }
        return 0, false
    },
    "current_defrost_counter": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.CurrentDefrostCounter != nil {
            return float64(msg.ParkerState.CurrentDefrostCounter.Value), true
        }
        return 0, false
    },
    "compressor_delay": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.CompressorDelay != nil {
            return float64(msg.ParkerState.CompressorDelay.Value), true
        }
        return 0, false
    },
    "num_alarms_in_history": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.NumAlarmsInHistory != nil {
            return float64(msg.ParkerState.NumAlarmsInHistory.Value), true
        }
        return 0, false
    },
    "energy_saving_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.EnergySavingStatus != nil {
            return float64(msg.ParkerState.EnergySavingStatus.Value), true
        }
        return 0, false
    },
    "service_request_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.ServiceRequestStatus != nil {
            return float64(msg.ParkerState.ServiceRequestStatus.Value), true
        }
        return 0, false
    },
    "resistors_activated_by_aux_key_status": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.ResistorsActivatedByAuxKeyStatus != nil {
            return float64(msg.ParkerState.ResistorsActivatedByAuxKeyStatus.Value), true
        }
        return 0, false
    },
    "evaporator_valve_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.EvaporatorValveState != nil {
            return float64(msg.ParkerState.EvaporatorValveState.Value), true
        }
        return 0, false
    },
    "output_defrost_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.OutputDefrostState != nil {
            return float64(msg.ParkerState.OutputDefrostState.Value), true
        }
        return 0, false
    },
    "output_lux_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.OutputLuxState != nil {
            return float64(msg.ParkerState.OutputLuxState.Value), true
        }
        return 0, false
    },
    "output_aux_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.OutputAuxState != nil {
            return float64(msg.ParkerState.OutputAuxState.Value), true
        }
        return 0, false
    },
    "resistors_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.ResistorsState != nil {
            return float64(msg.ParkerState.ResistorsState.Value), true
        }
        return 0, false
    },
    "output_alarm_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.OutputAlarmState != nil {
            return float64(msg.ParkerState.OutputAlarmState.Value), true
        }
        return 0, false
    },
    "second_compressor_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.SecondCompressorState != nil {
            return float64(msg.ParkerState.SecondCompressorState.Value), true
        }
        return 0, false
    },
    "setpoint": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.Setpoint != nil {
            return float64(msg.ParkerState.Setpoint.Value), true
        }
        return 0, false
    },
    "p2": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.P2 != nil {
            return float64(msg.ParkerState.P2.Value), true
        }
        return 0, false
    },
    "r0": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.R0 != nil {
            return float64(msg.ParkerState.R0.Value), true
        }
        return 0, false
    },
    "r1": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.R1 != nil {
            return float64(msg.ParkerState.R1.Value), true
        }
        return 0, false
    },
    "r2": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.R2 != nil {
            return float64(msg.ParkerState.R2.Value), true
        }
        return 0, false
    },
    "r4": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.R4 != nil {
            return float64(msg.ParkerState.R4.Value), true
        }
        return 0, false
    },
    "c0": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.C0 != nil {
            return float64(msg.ParkerState.C0.Value), true
        }
        return 0, false
    },
    "c1": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.C1 != nil {
            return float64(msg.ParkerState.C1.Value), true
        }
        return 0, false
    },
    "d0": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.D0 != nil {
            return float64(msg.ParkerState.D0.Value), true
        }
        return 0, false
    },
    "d3": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.D3 != nil {
            return float64(msg.ParkerState.D3.Value), true
        }
        return 0, false
    },
    "d5": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.D5 != nil {
            return float64(msg.ParkerState.D5.Value), true
        }
        return 0, false
    },
    "d7": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.D7 != nil {
            return float64(msg.ParkerState.D7.Value), true
        }
        return 0, false
    },
    "d8": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.D8 != nil {
            return float64(msg.ParkerState.D8.Value), true
        }
        return 0, false
    },
    "a0": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.A0 != nil {
            return float64(msg.ParkerState.A0.Value), true
        }
        return 0, false
    },
    "a1": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.A1 != nil {
            return float64(msg.ParkerState.A1.Value), true
        }
        return 0, false
    },
    "a2": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.A2 != nil {
            return float64(msg.ParkerState.A2.Value), true
        }
        return 0, false
    },
    "a3": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.A3 != nil {
            return float64(msg.ParkerState.A3.Value), true
        }
        return 0, false
    },
    "a4": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.A4 != nil {
            return float64(msg.ParkerState.A4.Value), true
        }
        return 0, false
    },
    "a5": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.A5 != nil {
            return float64(msg.ParkerState.A5.Value), true
        }
        return 0, false
    },
    "a6": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.A6 != nil {
            return float64(msg.ParkerState.A6.Value), true
        }
        return 0, false
    },
    "a7": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.A7 != nil {
            return float64(msg.ParkerState.A7.Value), true
        }
        return 0, false
    },
    "a8": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.A8 != nil {
            return float64(msg.ParkerState.A8.Value), true
        }
        return 0, false
    },
    "a9": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.A9 != nil {
            return float64(msg.ParkerState.A9.Value), true
        }
        return 0, false
    },
    "f0": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.F0 != nil {
            return float64(msg.ParkerState.F0.Value), true
        }
        return 0, false
    },
    "f1": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.F1 != nil {
            return float64(msg.ParkerState.F1.Value), true
        }
        return 0, false
    },
    "f2": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.F2 != nil {
            return float64(msg.ParkerState.F2.Value), true
        }
        return 0, false
    },
    "f3": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.ParkerState.F3 != nil {
            return float64(msg.ParkerState.F3.Value), true
        }
        return 0, false
    },
}

func build_device(uri types.SubscriptionURI, name string, msg xbospb.XBOS) types.ExtractedTimeseries {

	if extractfunc, found := device_lookup[name]; found {
		if value, found := extractfunc(msg); found {
			var extracted types.ExtractedTimeseries
			time := int64(msg.ParkerState.Time)
			extracted.Values = append(extracted.Values, value)
			extracted.Times = append(extracted.Times, time)
			extracted.UUID = types.GenerateUUID(uri, []byte(name))
			extracted.Collection = fmt.Sprintf("xbos/%s", uri.Resource)
			extracted.Tags = map[string]string{
				"unit": device_units[name],
				"name": name,
			}
			return extracted
		}
	}
	return types.ExtractedTimeseries{}
}

func Extract(uri types.SubscriptionURI, msg xbospb.XBOS, add func(types.ExtractedTimeseries) error) error {
	if msg.ParkerState != nil {
		if has_device(msg) {
			// Go through each Field in the Xbos Message
			for name := range device_lookup {
				extracted := build_device(uri, name, msg)
				//add function takes in an extracted timeseries and adds it to database
				if err := add(extracted); err != nil {
					return err
				}
			}
		}
	}
	return nil
}
