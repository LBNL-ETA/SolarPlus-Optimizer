# -*- coding: utf-8 -*-
"""
This module contains the mpc controller class, which can be used to 
solve the control optimization problem.

Currently, specific parameters, such as models, variable maps, and data
sources other than csv files need to be coded explicitly as appropriate.

"""

from mpcpy import exodata, models, optimization, variables, units, systems
import pandas as pd
import os

class mpc(object):
    '''MPC controller.

    Parameters
    ----------
    weather_source : str
        Source of weather data.
    control_source : str
        Source of control data.
    other_input_source : str
        Source of other input data.
    constraint_source : str
        Source of constraint data.
    price_source : str
        Source of price data.
    system_source : str
        Source of system data.
    objective : str
        Control optimization problem objective.

    '''

    def __init__(self, weather_source,
                       control_source,
                       other_input_source,
                       constraint_source,                       
                       price_source,
                       system_source,
                       objective):
        '''Constructor.

        '''

        # Initialize exodata
        self.weather = self._initialize_weather(weather_source)
        self.control = self._initialize_control(control_source)
        self.other_input = self._initialize_other_input(other_input_source)
        self.constraint = self._initialize_constraint(constraint_source)
        self.price = self._initialize_price(price_source)
        # Initialize model
        self.model, self.init_vm = self._initialize_model()
        # Initialize building measurements
        self.system = self._initialize_system(system_source)
        # Instantiate optimization object
        self.opt_object = self._initialize_opt_problem(objective)

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


    def _initialize_weather(self, weather_source):
        '''Instantiate an MPCPy weather object with the appropriate source.
        
        Parameters
        ----------
        weather_source : str
            If file path to .csv file, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific 
            source of DataFrame encoded.
            
        Returns
        -------
        weather : mpcpy.exodata.WeatherFrom[CSV][DF]
            Object to obtain and format weather data.

        '''

        # Specify geography
        geography = ()
        # Specify weather variable map
        weather_vm = dict()
        # Instantiate object
        if os.path.splitext(weather_source)[-1] is '.csv':
            weather = exodata.WeatherFromCSV(weather_source,
                                             weather_vm,
                                             geography)
        else:
            weather_df = pd.DataFrame()
            weather = exodata.WeatherFromDF(weather_df,
                                            weather_vm,
                                            geography)

        return weather
                                                 
    def _initialize_control(self, control_source):
        '''Instantiate an MPCPy control object with the appropriate source.
        
        Parameters
        ----------
        control_source : str
            If file path to .csv file, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific 
            source of DataFrame encoded.
            
        Returns
        -------
        control : mpcpy.exodata.ControlFrom[CSV][DF]
            Object to obtain and format control data.

        '''

        # Specify control variable map
        control_vm = dict()
        # Instantiate object
        if os.path.splitext(control_source)[-1] is '.csv':
            control = exodata.ControlFromCSV(control_source,
                                                  control_vm)
        else:
            control_df = pd.DataFrame()
            control = exodata.ControlFromDF(control_df,
                                            control_vm)

        return control
                                                 
    def _initialize_other_input(self, other_input_source):
        '''Instantiate an MPCPy other input object with the appropriate source.
        
        Parameters
        ----------
        other_input_source : str
            If file path to .csv file, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific 
            source of DataFrame encoded.

        Returns
        -------
        control : mpcpy.exodata.OtherInputFrom[CSV][DF]
            Object to obtain and format other input data.
            
        '''

        # Specify other input variable map
        other_input_vm = dict()
        # Instantiate object
        if os.path.splitext(other_input_source)[-1] is '.csv':
            other_input = exodata.OtherInputFromCSV(other_input_source,
                                                         other_input_vm)
        else:
            other_input_df = pd.DataFrame()
            other_input = exodata.OtherInputFromDF(other_input_df,
                                                   other_input_vm)

        return other_input
                                                        
    def _initialize_price(self, price_source):
        '''Instantiate an MPCPy price object with the appropriate source.
        
        Parameters
        ----------
        price_source : str
            If file path to .csv file, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific 
            source of DataFrame encoded.
            
        Returns
        -------
        price : mpcpy.exodata.PriceFrom[CSV][DF]
            Object to obtain and format price data.

        '''

        # Specify price variable map
        price_vm = dict()
        # Instantiate object
        if os.path.splitext(price_source)[-1] is '.csv':
            price = exodata.PriceFromCSV(price_source,
                                         price_vm)
        else:
            price_df = pd.DataFrame()
            price = exodata.PriceFromDF(price_df,
                                        price_vm)

        return price

    def _initialize_constraint(self, constraint_source):
        '''Instantiate an MPCPy constraint object with the appropriate source.
        
        Parameters
        ----------
        constraint_source : str
            If file path to .csv file, then instantiated as csv source.
            Otherwise, instantiated as DataFrame source, with specific 
            source of DataFrame encoded.
            
        Returns
        -------
        price : mpcpy.exodata.ConstraintFrom[CSV][DF]
            Object to obtain and format constraint data.

        '''

        # Specify constraint variable map
        constraint_vm = dict()
        # Instantiate object
        if os.path.splitext(constraint_source)[-1] is '.csv':
            constraint = exodata.ConstraintFromCSV(constraint_source,
                                                   constraint_vm)
        else:
            constraint_df = pd.DataFrame()
            constraint = exodata.ConstraintFromDF(constraint_df,
                                                  constraint_vm)

        return constraint
    
    def _initialize_system(self, system_source):
        '''Instantiate an MPCPy systems object from the appropriate source.
        
        Parameters
        ----------
        system_source : str
            If file path to .csv file, then instantiated as csv source.
            
        Returns
        -------
        system : mpcpy.systems.RealFromCSV
            Object to obtain and format system data.

        '''

        # Specify systems variable map
        system_vm = dict()
        # Instantiate object
        if os.path.splitext(system_source)[-1] is '.csv':
            # Instantiate csv source
            system = systems.RealFromCSV(system_source,
                                         self.model.measurements,
                                         system_vm)
        else:
            raise ValueError('System data must come from csv source.')

        return system

    def _initialize_model(self):
        '''Instantiate an MPCPy model object.
        
        Returns
        -------
        model : mpcpy.models.Modelica
            Object to represent the MPC model.
        init_vm : dict
            Variable map for parameters representing initial state variables
            and their associated measurement variable.

        '''
        
        # Specify definition
        mopath = 'models/SolarPlus.mo'
        modelpath = 'SolarPlus.Building.Whole_Inputs'
        libraries = []
        # Specify measurements
        meas_list = ['Trtu', 'Tref', 'Tfre', 'weaTDryBul', 'SOC', 
                     'Prtu', 'Pref', 'Pfre', 'Pcharge', 'Pdischarge', 'Pnet', 'Ppv',
                     'uCharge', 'uDischarge', 'uHeat', 'uCool', 'uRef', 'uFreCool']
        sample_rate = 3600;
        measurements = dict()
        for meas in meas_list:
            measurements[meas] = {'Sample' : variables.Static('{0}_sample'.format(meas), sample_rate, units.s)};
        # Specify parameters
        pars = {'Name':      ['Trtu_0', 'Tref_0', 'Tfre_0', 'SOC_0'], 
                'Free':      [False,    False,    False,    False],
                'Value':     [0,        0,        0,        0],
                'Minimum':   [10,       0,        -40,      0],
                'Maximum':   [35,       20,       0,        1],
                'Covariance':[0,        0,        0,        0],
                'Unit' :     ['degC',   'degC',   'degC',   '1']}
        par_df = pd.DataFrame(pars).set_index('Name')
        self.parameter = exodata.ParameterFromDF(par_df)
        self.parameter.collect_data()
        # Specify initial parameter dictionary
        init_vm =  {'Trtu_0' : 'Trtu',
                    'Tref_0' : 'Tref',
                    'Tfre_0' : 'Tfre',
                    'SOC_0' : 'SOC'}
        # Instantiate object
        moinfo = (mopath, modelpath, libraries)
        model = models.Modelica(models.JModelica,
                                     models.RMSE,
                                     measurements,
                                     moinfo = moinfo,
                                     weather_data = self.weather.data,
                                     control_data = self.control.data,
                                     other_inputs = self.other_input.data,
                                     parameter_data = self.parameter.data,
                                     tz_name = self.weather.tz_name)

        return model, init_vm

    def _initialize_opt_problem(self, objective):
        '''Instantiate an MPCPy optimization object.
        
        Returns
        -------
        opt_object : mpcpy.optimization.Optimization
            Object to represent the control optimization.

        '''
        
        # Specify objective
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
                                                'J',
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
        