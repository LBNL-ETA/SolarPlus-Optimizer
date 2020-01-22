package main

import (
	"fmt"
	"github.com/gtfierro/xboswave/ingester/types"
	xbospb "github.com/gtfierro/xboswave/proto"
)

type add_fn func(types.ExtractedTimeseries) error

func has_device(msg xbospb.XBOS) bool {
	return msg.ParkerActuationMessage.Setpoints != nil
}

// This contains the mapping of each field's value to the unit
var device_units = map[string]string{
	"change_time":           "seconds",
	"setpoint":      "F",
	"differential":      "F",
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
		"prediction_time": fmt.Sprintf("%d", prediction_time/1e9),
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
	if msg.ParkerActuationMessage != nil {
        //fmt.Printf("hello")

        if msg.ParkerActuationMessage.ControlFlag != nil {
            controlFlag := float64(msg.ParkerActuationMessage.ControlFlag.Value)

            var extracted types.ExtractedTimeseries
            time := int64(msg.ParkerActuationMessage.Time)
            extracted.Values = append(extracted.Values, controlFlag)
            extracted.Times = append(extracted.Times, time)
            extracted.UUID = types.GenerateUUID(uri, []byte("control_flag"))
            extracted.Collection = fmt.Sprintf("xbos/%s", uri.Resource)
            extracted.Tags = map[string]string{
                "unit": "T/F",
                "name": "control_flag",
            }
            add(extracted)
        }

		if has_device(msg) {
			step := 1

			//Iterate through each hour of prediction from current to 48 hours from current
			for _, _prediction := range msg.ParkerActuationMessage.Setpoints {
				//This prediction contains all of the fields that were present in WeatherCurrent message
				//There is one for each hour that is retrieved from the DarkSky API
				// prediction := _prediction.Prediction

				//This will contain all the information necessary to send one prediction for one hour out of 0-48
				var extracted types.ExtractedTimeseries
				prediction_time := int64(_prediction.ChangeTime)

				//This is the xbos message time
				time := int64(msg.ParkerActuationMessage.Time)

				//This is the time that is being put into influx as the timestamp
				extracted.Times = append(extracted.Times, time)

				err := ingest_time_series(float64(_prediction.ChangeTime),
					"change_time", extracted, add, prediction_time, step, uri)
				if err != nil {
					return err
				}

				if _prediction.Setpoint != nil {
					err := ingest_time_series(float64(_prediction.Setpoint.Value),
						"setpoint", extracted, add, prediction_time, step, uri)
					if err != nil {
						return err
					}
				}
				if _prediction.Differential != nil {
					err := ingest_time_series(float64(_prediction.Differential.Value),
						"differential", extracted, add, prediction_time, step, uri)
					if err != nil {
						return err
					}
				}

				step++
			}
		}
	}
	return nil
}
