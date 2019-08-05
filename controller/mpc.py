# -*- coding: utf-8 -*-
"""
This module contains the mpc controller class, which can be used to
solve the control optimization problem.

Currently, specific data sources other than csv files need to be coded
explicitly as appropriate.

"""

from mpcpy import exodata, models, optimization, variables, units, systems
import pandas as pd
from data_manager import Data_Manager
import process_data

class mpc(object):
    '''MPC controller.

    Parameters
    ----------
    model_config : dict()
        Dictionary of source information.
    opt_config : dict()
        Dictionary of source information..
    system_config : dict()
        Dictionary of source information.
    weather_config : dict()
        Dictionary of source information.
    control_config : dict()
        Dictionary of source information.
    setpoints_config: dict()
        Dictionary of source information.
    other_input_config : dict(), optional
        Dictionary of source information.
    constraint_config : dict(), optional
        Dictionary of source information.
    price_config : dict(), optional
        Dictionary of source information.
    data_manager_config : dict(), optional
        Dictionary of source information.
    tz_name ; str, optional
        Name of the time zone to use with the controller
        Default is 'UTC'.
    '''

    def __init__(self, model_config,
                       opt_config,
                       system_config,
                       weather_config,
                       control_config,
                       setpoints_config,
                       other_input_config = None,
                       constraint_config = None,
                       data_manager_config = None,
                       price_config = None,
                       tz_name = 'UTC'):
        '''Constructor.

        '''
        # Save configuration
        self.model_config = model_config
        self.opt_config = opt_config
        self.system_config = system_config
        self.weather_config = weather_config
        self.control_config = control_config
        self.setpoints_config = setpoints_config
        self.other_input_config = other_input_config
        self.constraint_config = constraint_config
        self.data_manager_config = data_manager_config
        self.price_config = price_config
        # Get timezone
        self.tz_name = tz_name
        # Initialize exodata
        self.data_manager = Data_Manager(data_manager_config=data_manager_config)
        self.weather = self._initialize_weather(self.weather_config)
        self.control = self._initialize_control(self.control_config)
        self.other_input = self._initialize_other_input(self.other_input_config)
        self.constraint = self._initialize_constraint(self.constraint_config)
        self.price = self._initialize_price(self.price_config)
        # Initialize model
        self.model, self.init_vm = self._initialize_model(self.model_config)
        # Initialize building measurements
        self.system = self._initialize_system(self.system_config)
        # Save optimization configuration
        self.opt_config = opt_config

    def optimize(self, start_time, final_time, init = True):
        '''Solve the control optimization problem.

        Parameters
        ----------
        start_time : pandas datetime
            Start time of optimization
        final_time : pandas datetime
            Final time of optimization
        init : bool, optional
            True if initial optimization.  Will instantiate optimization problem.

        Returns
        -------
        solution : DataFrame
            Solution of optimization problem for model measurements.
        statistics : tup
            Statistics of optimization solver.

        '''

        # Update system measurements
        self._update_system(start_time, final_time)
        # Estimate state
        self._estimate_state(start_time)
        # Update exodata
        for exo in [self.weather,
                    self.other_input,
                    self.constraint,
                    self.price]:
            self._update_exo(exo, start_time, final_time)
        # Instantiate problem and load initial control if initial
        if init:
            self._update_exo(self.control, start_time, final_time)
            self.opt_object = self._initialize_opt_problem(self.opt_config)
        # Solve problem
        self.opt_object.optimize(start_time, final_time, price_data=self.price.data)
        # Get solution and statistics
        control = self.control.display_data()
        measurements = self.opt_object.display_measurements('Simulated')
        other_outputs = pd.DataFrame(index=measurements.index)
        for key in self.other_outputs:
            other_outputs[key] = self.opt_object._package_type.res_opt['mpc_model.{0}'.format(key)]
        statistics = self.opt_object.get_optimization_statistics()

        return control, measurements, other_outputs, statistics

    def set_setpoints(self, control, measurements):
        '''Push the optimal setpoints to a DataFrame

        Parameters
        -----------
        control : DataFrame
            Solution of optimization problem
        measurements : DataFrame
            Solution of optimization problem for model measurements

        Returns
        -------
        setpoints : DataFrame
            Optimal setpoints obtained after the completion of simulation

        '''
        vm = self.setpoints_config['vm']
        setpoints_list = []
        for key in vm:
            if key in control.columns:
                setpoints_list.append(control[key])
            elif key in measurements.columns:
                setpoints_list.append(measurements[key])
            else:
                raise ValueError("{0} is not in control or measurements".format(key))
        setpoints = pd.concat(setpoints_list,axis=1)
        if 'Trtu' in setpoints.columns:
            setpoints['Trtu_cool'] = setpoints['Trtu']
            setpoints['Trtu_heat'] = setpoints['Trtu']
        self.data_manager.set_setpoints(setpoints)

        return setpoints

    def simulate(self, start_time, final_time, optimal=False):
        '''Simulate the model with an initial point from measurements.

        Parameters
        ----------
        start_time : pandas datetime
            Start time of simulation
        final_time : pandas datetime
            Final time of simulation
        optimal : bool, optional
            True if use exodata and control from already-solved optimizaton
            False to update exodata and control from sources
            Default is False

        Returns
        -------
        measurements : DataFrame
            Measurements of simulation.
        other_outputs : DataFrame
            Other outputs of the simulation

        '''

        # Update system measurements
        self._update_system(start_time, final_time)
        # Estimate state
        self._estimate_state(start_time)
        # Update exodata
        if not optimal:
            for exo in [self.weather,
                        self.control,
                        self.other_input,
                        self.constraint,
                        self.price]:
                self._update_exo(exo, start_time, final_time)
        # Solve problem
        self.model.simulate(start_time, final_time)
        # Get solution
        measurements = self.model.display_measurements('Simulated')
        other_outputs = pd.DataFrame(index=measurements.index)
        for key in self.other_outputs:
            other_outputs[key] = self.model._res[key]

        return measurements, other_outputs


    def _estimate_state(self, time):
        '''Estimate the states of the model.

        Parameters
        ----------
        time : pandas datetime
            Time at which to estimate state.

        Returns
        -------
        None

        '''

        # For each initial state
        for par in self.init_vm:
            # Get the estimated value
            # print(self.model.display_measurements('Measured'))
            # print(time)
            value = self.model.display_measurements('Measured').loc[time,self.init_vm[par]]
            # Set the value in the model
            self.model.parameter_data[par]['Value'].set_data(value)

        return None


    def _initialize_weather(self, weather_config):
        '''Instantiate an MPCPy weather object with the appropriate source.

        Parameters
        ----------
        weather_config : dict()
            If type is csv, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific
            source of DataFrame encoded.

        Returns
        -------
        weather : mpcpy.exodata.WeatherFrom[CSV][DF]
            Object to obtain and format weather data.

        '''

        weather_df = self.data_manager.init_data_from_config("weather")

        weather = exodata.WeatherFromDF(weather_df,
                                        weather_config['vm'],
                                        weather_config['geo'])

        return weather

    def _initialize_control(self, control_config):
        '''Instantiate an MPCPy control object with the appropriate source.

        Parameters
        ----------
        control_config : dict()
            If type is csv, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific
            source of DataFrame encoded.

        Returns
        -------
        control : mpcpy.exodata.ControlFrom[CSV][DF]
            Object to obtain and format control data.

        '''

        control_df = self.data_manager.init_data_from_config("control")
        control = exodata.ControlFromDF(control_df,
                                        control_config['vm'])
        return control

    def _initialize_other_input(self, other_input_config):
        '''Instantiate an MPCPy other input object with the appropriate source.

        Parameters
        ----------
        other_input_config : dict()
            If type is csv, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific
            source of DataFrame encoded.
            If None, then instantiated with empty data.

        Returns
        -------
        control : mpcpy.exodata.OtherInputFrom[CSV][DF]
            Object to obtain and format other input data.

        '''

        # Check if None
        if other_input_config:
            # # Instantiate object
            other_input_df = self.data_manager.init_data_from_config(other_input_config)
            other_input = exodata.OtherInputFromDF(other_input_df,
                                                    other_input_config['vm'])
        else:
                other_input = None

        return other_input

    def _initialize_price(self, price_config):
        '''Instantiate an MPCPy price object with the appropriate source.

        Parameters
        ----------
        price_config : dict()
            If type is csv, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific
            source of DataFrame encoded.
            If None, then instantiated with empty data.

        Returns
        -------
        price : mpcpy.exodata.PriceFrom[CSV][DF]
            Object to obtain and format price data.

        '''

        # Check if None
        if price_config:
            # # Instantiate object
            price_df = self.data_manager.init_data_from_config("price")
            price = exodata.PriceFromDF(price_df,
                                        price_config['vm'])
        else:
                price = None

        return price

    def _initialize_constraint(self, constraint_config):
        '''Instantiate an MPCPy constraint object with the appropriate source.

        Parameters
        ----------
        constraint_config : dict()
            If type is csv, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific
            source of DataFrame encoded.
            If None, then instantiated with empty data.

        Returns
        -------
        price : mpcpy.exodata.ConstraintFrom[CSV][DF]
            Object to obtain and format constraint data.

        '''

        # Check if None
        if constraint_config:
            # # Instantiate object
            constraint_df = self.data_manager.init_data_from_config("constraint")
            constraint = exodata.ConstraintFromDF(constraint_df,
                                                  constraint_config['vm'])
        else:
                constraint = None

        return constraint

    def _initialize_system(self, system_config):
        '''Instantiate an MPCPy systems object from the appropriate source.

        Parameters
        ----------
        system_config : dict()
            If type is csv, then instantiated as csv source.

        Returns
        -------
        system : mpcpy.systems.RealFromCSV
            Object to obtain and format system data.

        '''

        # # Instantiate object
        system_df = self.data_manager.init_data_from_config("system")
        system = systems.RealFromDF(system_df,
                                    self.model.measurements,
                                    system_config['vm'])

        return system

    def _initialize_model(self, model_config):
        '''Instantiate an MPCPy model object.

        Parameters
        ----------
        model_config : dict()
            Configruation of model.

        Returns
        -------
        model : mpcpy.models.Modelica
            Object to represent the MPC model.
        init_vm : dict
            Variable map for parameters representing initial state variables
            and their associated measurement variable.

        '''

        # Specify definition
        mopath = model_config['mopath']
        modelpath = model_config['modelpath']
        libraries = model_config['libraries']
        # Specify measurements
        meas_list = model_config['measurements']
        sample_rate = model_config['sample_rate'];
        measurements = dict()
        for meas in meas_list:
            measurements[meas] = {'Sample' : variables.Static('{0}_sample'.format(meas), sample_rate, units.s)};
        # Specify parameters
        pars = model_config['parameters']
        par_df = pd.DataFrame(pars).set_index('Name')
        self.parameter = exodata.ParameterFromDF(par_df)
        self.parameter.collect_data()
        # Specify initial parameter dictionary
        init_vm =  model_config['init_vm']
        # Instantiate object
        moinfo = (mopath, modelpath, libraries)
        model = models.Modelica(models.JModelica,
                                     models.RMSE,
                                     measurements,
                                     moinfo = moinfo,
                                     weather_data = self.weather.data,
                                     control_data = self.control.data,
                                     parameter_data = self.parameter.data,
                                     tz_name = self.weather.tz_name)
        # Check if other inputs present
        if self.other_input:
            model.other_inputs = self.other_input.data
        # Store other outputs
        self.other_outputs = model_config['other_outputs']

        return model, init_vm

    def _initialize_opt_problem(self, opt_config):
        '''Instantiate an MPCPy optimization object.

        Parameters
        ----------
        opt_config: dict()
            Configuration of optimization problem
        Returns
        -------
        opt_object : mpcpy.optimization.Optimization
            Object to represent the control optimization.

        '''

        # Specify objective
        objective = opt_config['problem']
        if objective is 'EnergyMin':
            problem = optimization.EnergyMin
        elif objective is 'EnergyCostMin':
            problem = optimization.EnergyCostMin
        else:
            raise ValueError('Objective "{0}" unknown or not available.'.format(objective))
        # Instantiate object
        opt_object = optimization.Optimization(self.model,
                                               problem,
                                               optimization.JModelica,
                                               opt_config['power_var'],
                                               constraint_data = self.constraint.data,
                                               tz_name = self.weather.tz_name)
        # Set default options
        opt_options = opt_object.get_optimization_options()
        opt_options['n_e'] = 24*4
        opt_options['IPOPT_options']['tol'] = 1e-10
        opt_object.set_optimization_options(opt_options)

        return opt_object

    def _update_exo(self, exo_object, start_time, final_time):
        '''Update the exodata object with data during the time period.

        If the object source is a .csv file, the .csv file will be used.
        Otherwise, the object source is a DataFrame, and the update of the
        DataFrame will occur as encoded.

        Parameters
        ----------
        exo_object : mpcpy.exodata.[object]
            The exodata object to update.
        start_time : pandas datetime in utc
            The start time of the update period.
        final_time : pandas datetime in utc
            The final time of the update period.

        Returns
        -------
        None

        '''

        # Update exodata
        if exo_object:
            if exo_object is self.weather:
                config_section = "weather"
            elif exo_object is self.control:
                config_section = "control"
            elif exo_object is self.other_input:
                config_section = "other_input"
            elif exo_object is self.constraint:
                config_section = "constraint"
            elif exo_object is self.price:
                config_section = "price"
            else:
                raise ValueError('Exodata object {0} unknown.'.format(exo_object))
            # Update data
            df = self.data_manager.get_data_from_config(config_section, start_time, final_time)

            if config_section == "control":
                df = process_data.process_control_df(df=df)

            exo_object._df = df
            exo_object.collect_data(start_time, final_time)

        return None

    def _update_system(self, start_time, final_time):
        '''Update the system object with data during the time period.

        If the object source is a .csv file, the .csv file will be used.

        Parameters
        ----------
        start_time : pandas datetime
            The start time of the update period.
        final_time : pandas datetime
            The final time of the update period.

        Returns
        -------
        None

        '''

        # Update exodata
        df = self.data_manager.get_data_from_config("system", start_time, final_time)
        self.system._df = df
        self.system.collect_measurements(start_time, final_time)

        return None
