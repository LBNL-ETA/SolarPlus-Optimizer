# -*- coding: utf-8 -*-
"""
This module contains the mpc controller class, which can be used to 
solve the control optimization problem.

Currently, specific parameters, such as models, variable maps, and data
sources other than csv files need to be coded explicitly as appropriate.

"""

from mpcpy import exodata, models, optimization, variables, units, systems
import pandas as pd

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
    other_input_config : dict()
        Dictionary of source information.
    constraint_config : dict()
        Dictionary of source information.
    price_config : dict()
        Dictionary of source information.

    '''

    def __init__(self, model_config,
                       opt_config, 
                       system_config,
                       weather_config,
                       control_config,
                       other_input_config=None,
                       constraint_config=None,                       
                       price_config=None):
        '''Constructor.

        '''

        # Initialize exodata
        self.weather = self._initialize_weather(weather_config)
        self.control = self._initialize_control(control_config)
        if other_input_config:
            self.other_input = self._initialize_other_input(other_input_config)
        else:
            self.other_input = None
        if constraint_config:
            self.constraint = self._initialize_constraint(constraint_config)
        else:
            self.constraint = None
        if price_config:
            self.price = self._initialize_price(price_config)
        else:
            self.price = None
        # Initialize model
        self.model, self.init_vm = self._initialize_model(model_config)
        # Initialize building measurements
        self.system = self._initialize_system(system_config)
        # Instantiate optimization object
        self.opt_object = self._initialize_opt_problem(opt_config)

    def optimize(self, start_time, final_time):
        '''Solve the control optimization problem.
        
        Parameters
        ----------
        start_time : str
            Start time of optimization
        final_time : str
            Final time of optimization
        
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
                    self.control, 
                    self.other_input, 
                    self.constraint, 
                    self.price]:
            self._update_exo(exo, start_time, final_time)
        # Solve problem
        self.opt_object.optimize(start_time, final_time, price_data=self.prices.data)
        # Get solution and statistics
        solution = self.opt_object.display_measurements('Simulated')
        statistics = self.opt_object.get_optimization_statistics()
        
        return solution, statistics

    def _estimate_state(self, time):
        '''Estimate the states of the model.
        
        Parameters
        ----------
        time : str
            Time at which to estimate state.

        Returns
        -------
        None

        '''

        # For each initial state
        for par in self.init_vm:
            # Get the estimated value
            value = self.model.measurements.display_data('Measured').loc[time,self.init_vm[par]]
            # Set the value in the model
            self.model.parameter_data[par] = dict()
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

        # Instantiate object
        if weather_config['type'] is 'csv':
            weather = exodata.WeatherFromCSV(weather_config['path'],
                                             weather_config['vm'],
                                             weather_config['geo'])
        else:
            weather_df = pd.DataFrame()
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

        # Instantiate object
        if control_config['type'] is 'csv':
            control = exodata.ControlFromCSV(control_config['path'],
                                             control_config['vm'])
        else:
            control_df = pd.DataFrame()
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

        Returns
        -------
        control : mpcpy.exodata.OtherInputFrom[CSV][DF]
            Object to obtain and format other input data.
            
        '''

        # Instantiate object
        if other_input_config['type'] is 'csv':
            other_input = exodata.OtherInputFromCSV(other_input_config['path'],
                                                    other_input_config['vm'])
        else:
            other_input_df = pd.DataFrame()
            other_input = exodata.OtherInputFromDF(other_input_df,
                                                   other_input_config['vm'])

        return other_input
                                                        
    def _initialize_price(self, price_config):
        '''Instantiate an MPCPy price object with the appropriate source.
        
        Parameters
        ----------
        price_config : dict()
            If type is csv, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific 
            source of DataFrame encoded.
            
        Returns
        -------
        price : mpcpy.exodata.PriceFrom[CSV][DF]
            Object to obtain and format price data.

        '''

        # Instantiate object
        if price_config['type'] is 'csv':
            price = exodata.PriceFromCSV(price_config['path'],
                                         price_config['vm'])
        else:
            price_df = pd.DataFrame()
            price = exodata.PriceFromDF(price_df,
                                        price_config['vm'])

        return price

    def _initialize_constraint(self, constraint_config):
        '''Instantiate an MPCPy constraint object with the appropriate source.
        
        Parameters
        ----------
        constraint_config : dict()
            If type is csv, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific 
            source of DataFrame encoded.
            
        Returns
        -------
        price : mpcpy.exodata.ConstraintFrom[CSV][DF]
            Object to obtain and format constraint data.

        '''

        # Instantiate object
        if constraint_config['type'] is 'csv':
            constraint = exodata.ConstraintFromCSV(constraint_config['path'],
                                                   constraint_config['vm'])
        else:
            constraint_df = pd.DataFrame()
            constraint = exodata.ConstraintFromDF(constraint_df,
                                                  constraint_config['vm'])

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

        # Instantiate object
        if system_config['type'] is 'csv':
            # Instantiate csv source
            system = systems.RealFromCSV(system_config['path'],
                                         self.model.measurements,
                                         system_config['vm'])
        else:
            raise ValueError('System data must come from csv source.')

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
        if self.other_input:
            model.other_input_data = self.other_input.data

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
        start_time : str
            The start time of the update period.
        final_time : str
            The final time of the update period.
            
        Returns
        -------
        None

        '''            
         
        # Update exodata
        if 'from_csv' in exo_object.name:
            exo_object.collect_data(start_time, final_time)
        else:
            exo_object._df = pd.DataFrame()
            exo_object.collect_data(start_time, final_time)
            
        return None
        
    def _update_system(self, start_time, final_time):
        '''Update the system object with data during the time period.
        
        If the object source is a .csv file, the .csv file will be used.
        
        Parameters
        ----------
        start_time : str
            The start time of the update period.
        final_time : str
            The final time of the update period.
            
        Returns
        -------
        None

        '''            
         
        # Update exodata
        self.system.collect_measurements(start_time, final_time)
            
        return None
        