package main

import (
	"fmt"
	"github.com/gtfierro/xboswave/ingester/types"
	xbospb "github.com/gtfierro/xboswave/proto"
)

type add_fn func(types.ExtractedTimeseries) error

func has_device(msg xbospb.XBOS) bool {
	return msg.Drsigpred != nil
}

// This contains the mapping of each field's value to the unit
var device_units = map[string]string {
    "time":                 "nanoseconds",
    "signal_type":          "int",
	"price_energy":         "$/kWh",
    "price_demand":         "$/kW",
	"power_limit":          "kW",
    "power_shed":           "kW",
    "power_shift":          "kW",
    "power_track":          "kW",
}

func ingest_time_series(value float64, name string, toInflux types.ExtractedTimeseries,
	pass_add add_fn, prediction_time int64, step int, uri types.SubscriptionURI) error {

    toInflux.Values = append(toInflux.Values, value)

	//This UUID is unique to each field in the message
	toInflux.UUID = types.GenerateUUID(uri, []byte(name))
	//The collection comes from the resource name of the driver
	toInflux.Collection = fmt.Sprintf("xbos/%s", uri.Resource)
	//These are the tags that will be used when the point is written
	toInflux.Tags = map[string]string{
		"unit":            device_units[name],
		"name":            name,
		//"prediction_time": fmt.Sprintf("%d", prediction_time/1e9),
		"prediction_time": fmt.Sprintf("%d", prediction_time),
		"prediction_step": fmt.Sprintf("%d", step),
	}
	//This add function is passed in from the ingester and when it is executed
	//a point is written into influx
	if err := pass_add(toInflux); err != nil {
		return err
	}
	return nil
}

func Extract(uri types.SubscriptionURI, msg xbospb.XBOS, add func(types.ExtractedTimeseries) error) error {

    if has_device(msg) {
        step := 1

        //Iterate through each hour of prediction from current to 48 hours from current
        for _, _prediction := range msg.Drsigpred.Predictions {

            //This is the xbos message time
            time := int64(msg.Drsigpred.Time)

            //This will contain all the information necessary to send one prediction for one hour out of 0-48
            var extracted types.ExtractedTimeseries
            prediction_time := int64(_prediction.ForecastTime)

            //This is the time that is being put into influx as the timestamp
            extracted.Times = append(extracted.Times, time)

            if _prediction.PriceEnergy != nil {
                err := ingest_time_series(float64(_prediction.PriceEnergy.Value),
                    "price_energy", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.PriceDemand != nil {
                err := ingest_time_series(float64(_prediction.PriceDemand.Value),
                    "price_demand", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.SignalType != nil {
                err := ingest_time_series(float64(_prediction.SignalType.Value),
                    "signal_type", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.PowerLimit != nil {
                err := ingest_time_series(float64(_prediction.PowerLimit.Value),
                    "power_limit", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            /*
            if _prediction.PowerShed != nil {
                err := ingest_time_series(float64(_prediction.PowerShed.Value),
                    "power_shed", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.PowerShift != nil {
                err := ingest_time_series(float64(_prediction.PowerShift.Value),
                    "power_shift", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }
            */

            if _prediction.PowerTrack != nil {
                err := ingest_time_series(float64(_prediction.PowerTrack.Value),
                    "power_track", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            step++
        }
    }
	return nil
}

