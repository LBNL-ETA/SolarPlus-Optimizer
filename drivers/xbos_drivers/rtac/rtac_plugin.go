package main

import (
	"fmt"
	"github.com/gtfierro/xboswave/ingester/types"
	xbospb "github.com/gtfierro/xboswave/proto"
)

func has_device(msg xbospb.XBOS) bool {
	return msg.RtacState != nil
}

var device_units = map[string]string{
    "heartbeat": "",
    "real_power_setpoint": "W",
    "reactive_power_setpoint": "VAR",
    "target_real_power": "W",
    "target_reactive_power": "VAR",
    "battery_total_capacity": "Wh",
    "battery_current_stored_energy": "Wh",
    "total_actual_real_power": "W",
    "total_actual_reactive_power": "VAR",
    "total_actual_apparent_power": "VA",
    "active_power_output_limit": "W",
    "current_power_production": "W",
    "ac_current_phase_a": "A",
    "ac_current_phase_b": "A",
    "ac_current_phase_c": "A",
    "ac_voltage_ab": "V",
    "ac_voltage_bc": "V",
    "ac_voltage_ca": "V",
    "ac_frequency": "Hz",
    "islanding_state": "T/F",
    "island_type": "T/F",
    "bess_availability": "T/F",
    "fault_condition": "",
    "pge_state": "T/F",
    "pcc_breaker_state": "T/F",
    "pge_voltage": "V",
    "pge_frequency": "Hz",
    "bess_pv_breaker_state": "T/F",
}
var device_lookup = map[string]func(msg xbospb.XBOS) (float64, bool){
    "heartbeat": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.Heartbeat != nil {
            return float64(msg.RtacState.Heartbeat.Value), true
        }
        return 0, false
    },
    "real_power_setpoint": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.RealPowerSetpoint != nil {
            return float64(msg.RtacState.RealPowerSetpoint.Value), true
        }
        return 0, false
    },
    "reactive_power_setpoint": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.ReactivePowerSetpoint != nil {
            return float64(msg.RtacState.ReactivePowerSetpoint.Value), true
        }
        return 0, false
    },
    "target_real_power": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.TargetRealPower != nil {
            return float64(msg.RtacState.TargetRealPower.Value), true
        }
        return 0, false
    },
    "target_reactive_power": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.TargetReactivePower != nil {
            return float64(msg.RtacState.TargetReactivePower.Value), true
        }
        return 0, false
    },
    "battery_total_capacity": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.BatteryTotalCapacity != nil {
            return float64(msg.RtacState.BatteryTotalCapacity.Value), true
        }
        return 0, false
    },
    "battery_current_stored_energy": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.BatteryCurrentStoredEnergy != nil {
            return float64(msg.RtacState.BatteryCurrentStoredEnergy.Value), true
        }
        return 0, false
    },
    "total_actual_real_power": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.TotalActualRealPower != nil {
            return float64(msg.RtacState.TotalActualRealPower.Value), true
        }
        return 0, false
    },
    "total_actual_reactive_power": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.TotalActualReactivePower != nil {
            return float64(msg.RtacState.TotalActualReactivePower.Value), true
        }
        return 0, false
    },
    "total_actual_apparent_power": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.TotalActualApparentPower != nil {
            return float64(msg.RtacState.TotalActualApparentPower.Value), true
        }
        return 0, false
    },
    "active_power_output_limit": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.ActivePowerOutputLimit != nil {
            return float64(msg.RtacState.ActivePowerOutputLimit.Value), true
        }
        return 0, false
    },
    "current_power_production": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.CurrentPowerProduction != nil {
            return float64(msg.RtacState.CurrentPowerProduction.Value), true
        }
        return 0, false
    },
    "ac_current_phase_a": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.AcCurrentPhaseA != nil {
            return float64(msg.RtacState.AcCurrentPhaseA.Value), true
        }
        return 0, false
    },
    "ac_current_phase_b": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.AcCurrentPhaseB != nil {
            return float64(msg.RtacState.AcCurrentPhaseB.Value), true
        }
        return 0, false
    },
    "ac_current_phase_c": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.AcCurrentPhaseC != nil {
            return float64(msg.RtacState.AcCurrentPhaseC.Value), true
        }
        return 0, false
    },
    "ac_voltage_ab": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.AcVoltageAb != nil {
            return float64(msg.RtacState.AcVoltageAb.Value), true
        }
        return 0, false
    },
    "ac_voltage_bc": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.AcVoltageBc != nil {
            return float64(msg.RtacState.AcVoltageBc.Value), true
        }
        return 0, false
    },
    "ac_voltage_ca": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.AcVoltageCa != nil {
            return float64(msg.RtacState.AcVoltageCa.Value), true
        }
        return 0, false
    },
    "ac_frequency": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.AcFrequency != nil {
            return float64(msg.RtacState.AcFrequency.Value), true
        }
        return 0, false
    },
    "islanding_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.IslandingState != nil {
            return float64(msg.RtacState.IslandingState.Value), true
        }
        return 0, false
    },
    "island_type": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.IslandType != nil {
            return float64(msg.RtacState.IslandType.Value), true
        }
        return 0, false
    },
    "bess_availability": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.BessAvailability != nil {
            return float64(msg.RtacState.BessAvailability.Value), true
        }
        return 0, false
    },
    "fault_condition": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.FaultCondition != nil {
            return float64(msg.RtacState.FaultCondition.Value), true
        }
        return 0, false
    },
    "pge_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.PgeState != nil {
            return float64(msg.RtacState.PgeState.Value), true
        }
        return 0, false
    },
    "pcc_breaker_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.PccBreakerState != nil {
            return float64(msg.RtacState.PccBreakerState.Value), true
        }
        return 0, false
    },
    "pge_voltage": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.PgeVoltage != nil {
            return float64(msg.RtacState.PgeVoltage.Value), true
        }
        return 0, false
    },
    "pge_frequency": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.PgeFrequency != nil {
            return float64(msg.RtacState.PgeFrequency.Value), true
        }
        return 0, false
    },
    "bess_pv_breaker_state": func(msg xbospb.XBOS) (float64, bool) {
        if has_device(msg) && msg.RtacState.BessPvBreakerState != nil {
            return float64(msg.RtacState.BessPvBreakerState.Value), true
        }
        return 0, false
    },
}

func build_device(uri types.SubscriptionURI, name string, msg xbospb.XBOS) types.ExtractedTimeseries {

	if extractfunc, found := device_lookup[name]; found {
		if value, found := extractfunc(msg); found {
			var extracted types.ExtractedTimeseries
			time := int64(msg.RtacState.Time)
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
	if msg.RtacState != nil {
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
