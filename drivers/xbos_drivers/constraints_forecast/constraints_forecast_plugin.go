package main

import (
	"fmt"
	"github.com/gtfierro/xboswave/ingester/types"
	xbospb "github.com/gtfierro/xboswave/proto"
    // For logging purposes. logrus.info("...")
    // logrus "github.com/sirupsen/logrus"
)

type add_fn func(types.ExtractedTimeseries) error

func has_device(msg xbospb.XBOS) bool {
	return msg.ConstraintsForecast != nil
}

// This contains the mapping of each field's value to the unit
var device_units = map[string]string {
	"Time":                 "nanoseconds",
    "ForecastTime":         "nanoseconds",
    "TRtuMax":              "",
    "TRtuMin":              "",
    "TRefMax":              "",
    "TRefMin":              "",
    "TFreMax":              "",
    "TFreMin":              "",
    "SOCMax":               "",
    "SOCMin":               "",
    "UCoolMin":             "",
    "UCoolMax":             "",
    "UHeatMin":             "",
    "UHeatMax":             "",
    "UChargeMin":           "",
    "UChargeMax":           "",
    "UDischargeMax":        "",
    "UDischargeMin":        "",
    "URefMin":              "",
    "URefMax":              "",
    "UFreCoolMin":          "",
    "UFreCoolMax":          "",
    "Demand":               "",
    "UBatteryMin":          "",
    "UBatteryMax":          "",
    "PMin":                 "",
    "PMax":                 "",
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
        for _, _prediction := range msg.ConstraintsForecast.ConstraintsPredictions {

            //This is the xbos message time
            time := int64(msg.ConstraintsForecast.Time)

            //This will contain all the information necessary to send one prediction for one hour out of 0-48
            var extracted types.ExtractedTimeseries
            prediction_time := int64(_prediction.ForecastTime)

            //This is the time that is being put into influx as the timestamp
            extracted.Times = append(extracted.Times, time)

            if _prediction.TRtuMax != nil {
                err := ingest_time_series(float64(_prediction.TRtuMax.Value),
                    "TRtuMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.TRtuMin != nil {
                err := ingest_time_series(float64(_prediction.TRtuMin.Value),
                    "TRtuMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.TRefMax != nil {
                err := ingest_time_series(float64(_prediction.TRefMax.Value),
                    "TRefMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.TRefMin != nil {
                err := ingest_time_series(float64(_prediction.TRefMin.Value),
                    "TRefMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.TFreMax != nil {
                err := ingest_time_series(float64(_prediction.TFreMax.Value),
                    "TFreMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.TFreMin != nil {
                err := ingest_time_series(float64(_prediction.TFreMin.Value),
                    "TFreMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.SOCMax != nil {
                err := ingest_time_series(float64(_prediction.SOCMax.Value),
                    "SOCMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.SOCMin != nil {
                err := ingest_time_series(float64(_prediction.SOCMin.Value),
                    "SOCMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UCoolMin != nil {
                err := ingest_time_series(float64(_prediction.UCoolMin.Value),
                    "UCoolMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UCoolMax != nil {
                err := ingest_time_series(float64(_prediction.UCoolMax.Value),
                    "UCoolMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UHeatMin != nil {
                err := ingest_time_series(float64(_prediction.UHeatMin.Value),
                    "UHeatMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UHeatMax != nil {
                err := ingest_time_series(float64(_prediction.UHeatMax.Value),
                    "UHeatMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UChargeMin != nil {
                err := ingest_time_series(float64(_prediction.UChargeMin.Value),
                    "UChargeMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UChargeMax != nil {
                err := ingest_time_series(float64(_prediction.UChargeMax.Value),
                    "UChargeMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UDischargeMax != nil {
                err := ingest_time_series(float64(_prediction.UDischargeMax.Value),
                    "UDischargeMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UDischargeMin != nil {
                err := ingest_time_series(float64(_prediction.UDischargeMin.Value),
                    "UDischargeMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.URefMin != nil {
                err := ingest_time_series(float64(_prediction.URefMin.Value),
                    "URefMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.URefMax != nil {
                err := ingest_time_series(float64(_prediction.URefMax.Value),
                    "URefMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UFreCoolMin != nil {
                err := ingest_time_series(float64(_prediction.UFreCoolMin.Value),
                    "UFreCoolMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UFreCoolMax != nil {
                err := ingest_time_series(float64(_prediction.UFreCoolMax.Value),
                    "UFreCoolMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.Demand != nil {
                err := ingest_time_series(float64(_prediction.Demand.Value),
                    "Demand", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UBatteryMin != nil {
                err := ingest_time_series(float64(_prediction.UBatteryMin.Value),
                    "UBatteryMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.UBatteryMax != nil {
                err := ingest_time_series(float64(_prediction.UBatteryMax.Value),
                    "UBatteryMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.PMin != nil {
                err := ingest_time_series(float64(_prediction.PMin.Value),
                    "PMin", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            if _prediction.PMax != nil {
                err := ingest_time_series(float64(_prediction.PMax.Value),
                    "PMax", extracted, add, prediction_time, step, uri)
                if err != nil {
                    return err
                }
            }

            step++
        }
    }
	return nil
}

