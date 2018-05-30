within ;
package MPC "This package contains models for MPC control optimization."

  package Envelope "Package for envelope thermal response models"
    model R1C1 "Zone thermal model"
      parameter Modelica.SIunits.HeatCapacity C=1e6 "Heat capacity of zone";
      parameter Modelica.SIunits.ThermalResistance R=0.01 "Thermal resistance of zone";
      parameter Modelica.SIunits.Temperature Tzone_0 "Initial temperature of zone";
      Modelica.Thermal.HeatTransfer.Components.HeatCapacitor capAir(C=C, T(fixed=true,
                                                                         start = Tzone_0))
        annotation (Placement(transformation(extent={{-10,0},{10,20}})));
    Modelica.Thermal.HeatTransfer.Components.ThermalResistor resAdj(R=R)
        annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
      Modelica.Thermal.HeatTransfer.Sources.PrescribedTemperature preAdj
        annotation (Placement(transformation(extent={{-70,-10},{-50,10}})));
      Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow preHeat
        annotation (Placement(transformation(extent={{-58,-50},{-38,-30}})));
      Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow preCool
        annotation (Placement(transformation(extent={{-58,-70},{-38,-50}})));
      Modelica.Blocks.Interfaces.RealInput Tadj "Adjacent temperature"
        annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
      Modelica.Blocks.Interfaces.RealInput qHeat "Heat floww for heating"
        annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
      Modelica.Blocks.Interfaces.RealInput qCool "Heat flow for cooling"
        annotation (Placement(transformation(extent={{-140,-100},{-100,-60}})));
      Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor temperatureSensor
        annotation (Placement(transformation(extent={{42,-10},{62,10}})));
      Modelica.Blocks.Interfaces.RealOutput Tzone "Zone air temperature"
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
    equation
      connect(resAdj.port_b, capAir.port)
        annotation (Line(points={{-20,0},{0,0}}, color={191,0,0}));
      connect(preAdj.port, resAdj.port_a)
        annotation (Line(points={{-50,0},{-40,0}}, color={191,0,0}));
      connect(preHeat.port, capAir.port)
        annotation (Line(points={{-38,-40},{0,-40},{0,0}}, color={191,0,0}));
      connect(preCool.port, capAir.port)
        annotation (Line(points={{-38,-60},{0,-60},{0,0}}, color={191,0,0}));
      connect(preAdj.T, Tadj) annotation (Line(points={{-72,0},{-80,0},{-80,60},{-120,
              60}}, color={0,0,127}));
      connect(qHeat, preHeat.Q_flow)
        annotation (Line(points={{-120,-40},{-58,-40}}, color={0,0,127}));
      connect(qCool, preCool.Q_flow) annotation (Line(points={{-120,-80},{-80,-80},{
              -80,-60},{-58,-60}}, color={0,0,127}));
      connect(capAir.port, temperatureSensor.port)
        annotation (Line(points={{0,0},{42,0}}, color={191,0,0}));
      connect(temperatureSensor.T, Tzone)
        annotation (Line(points={{62,0},{110,0}}, color={0,0,127}));
    annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
          Rectangle(
            extent={{-100,100},{100,-100}},
            lineColor={0,0,0},
            fillColor={255,231,231},
            fillPattern=FillPattern.Solid),
          Rectangle(
            extent={{-64,66},{-22,52}},
            lineColor={0,0,0},
            fillColor={255,231,231},
            fillPattern=FillPattern.Solid),
          Line(points={{-64,60},{-100,60}},
                                          color={0,0,0}),
          Line(points={{2,60},{-22,60}},
                                       color={0,0,0}),
          Line(points={{2,60},{2,-14}},color={0,0,0}),
          Line(points={{14,-14},{-10,-14}}, color={0,0,0}),
          Line(points={{14,-22},{-10,-22}}, color={0,0,0}),
          Line(points={{14,-36},{-10,-36}}, color={0,0,0}),
          Line(points={{2,-22},{2,-36}}, color={0,0,0}),
          Line(points={{12,-40},{-8,-40}}, color={0,0,0}),
          Line(points={{10,-44},{-6,-44}}, color={0,0,0}),
          Line(points={{-46,-40},{-100,-40}},
                                       color={0,0,0}),
          Line(points={{-46,-80},{-100,-80}},
                                       color={0,0,0}),
          Line(points={{-46,0},{-46,-80}},
                                       color={0,0,0}),
          Line(points={{2,0},{-46,0}}, color={0,0,0}),
            Ellipse(extent={{-88,-28},{-62,-54}}, lineColor={238,46,47}),
            Line(points={{-62,-40},{-70,-34}}, color={238,46,47}),
            Line(points={{-62,-40},{-70,-46}}, color={238,46,47}),
            Ellipse(extent={{-88,-68},{-62,-94}}, lineColor={28,108,200}),
            Line(points={{-62,-80},{-70,-74}}, color={28,108,200}),
            Line(points={{-62,-80},{-70,-86}}, color={28,108,200}),
          Line(points={{100,0},{2,0}}, color={0,0,0},
              pattern=LinePattern.Dot),
            Text(
              extent={{-150,140},{150,100}},
              textString="%name",
              lineColor={0,0,255})}),
                                Diagram(coordinateSystem(preserveAspectRatio=
              false)));
    end R1C1;

  end Envelope;

  package HVAC "Package for HVAC models"
    model SimpleHeaterCooler
      "A simple heater and cooler with constant efficiency and COP"
      parameter Modelica.SIunits.Power heatingCap = 10000 "Capacity of heater";
      parameter Modelica.SIunits.DimensionlessRatio heatingEff = 0.99 "Efficiency of heater";
      parameter Modelica.SIunits.Power coolingCap = 10000 "Capacity of cooler";
      parameter Modelica.SIunits.DimensionlessRatio coolingCOP = 3 "COP of cooler";
      Modelica.Blocks.Math.Gain heatingCapGain(k=heatingCap)
        annotation (Placement(transformation(extent={{-20,70},{0,90}})));
      Modelica.Blocks.Math.Gain coolingCapGain(k=coolingCap)
        annotation (Placement(transformation(extent={{-20,-90},{0,-70}})));
      Modelica.Blocks.Math.Gain heatingPowerGain(k=1/heatingEff)
        annotation (Placement(transformation(extent={{60,10},{80,30}})));
      Modelica.Blocks.Math.Gain coolingPowerGain(k=1/coolingCOP)
        annotation (Placement(transformation(extent={{60,-90},{80,-70}})));
      Modelica.Blocks.Interfaces.RealOutput PCool(unit="W")
      "Cooling electrical power output"
        annotation (Placement(transformation(extent={{100,-90},{120,-70}})));
      Modelica.Blocks.Interfaces.RealOutput PHeat(unit="W")
      "Heating electrical power output"
        annotation (Placement(transformation(extent={{100,10},{120,30}}),
            iconTransformation(extent={{100,10},{120,30}})));
      Modelica.Blocks.Interfaces.RealInput uHeat "Heating signal input"
        annotation (Placement(transformation(extent={{-140,60},{-100,100}})));
      Modelica.Blocks.Interfaces.RealInput uCool "Cooling signal input"
        annotation (Placement(transformation(extent={{-140,-100},{-100,-60}}),
            iconTransformation(extent={{-140,-100},{-100,-60}})));
      Modelica.Blocks.Interfaces.RealOutput qHeat(unit="W") "Heating heatflow output"
        annotation (Placement(transformation(extent={{100,50},{120,70}})));
      Modelica.Blocks.Interfaces.RealOutput qCool(unit="W") "Cooling heatflow output"
        annotation (Placement(transformation(extent={{100,-50},{120,-30}}),
            iconTransformation(extent={{100,-50},{120,-30}})));
      Modelica.Blocks.Math.Gain negHeatFlow(k=-1)
        annotation (Placement(transformation(extent={{60,-50},{80,-30}})));
    equation
      connect(heatingCapGain.y, heatingPowerGain.u) annotation (Line(points={{1,80},{
              20,80},{20,20},{58,20}},                color={0,0,127}));
      connect(coolingCapGain.y, coolingPowerGain.u) annotation (Line(points={{1,-80},
              {58,-80}},                 color={0,0,127}));
      connect(coolingPowerGain.y, PCool)
        annotation (Line(points={{81,-80},{110,-80}}, color={0,0,127}));
      connect(heatingPowerGain.y, PHeat)
        annotation (Line(points={{81,20},{110,20}}, color={0,0,127}));
      connect(heatingCapGain.u, uHeat) annotation (Line(points={{-22,80},{-120,80}},
                              color={0,0,127}));
      connect(uCool, coolingCapGain.u) annotation (Line(points={{-120,-80},{-22,-80}},
                                   color={0,0,127}));
      connect(heatingCapGain.y, qHeat) annotation (Line(points={{1,80},{60,80},{60,60},
              {110,60}},         color={0,0,127}));
      connect(coolingPowerGain.u, negHeatFlow.u) annotation (Line(points={{58,
              -80},{20,-80},{20,-40},{58,-40}}, color={0,0,127}));
      connect(negHeatFlow.y, qCool)
        annotation (Line(points={{81,-40},{110,-40}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-100,100},{100,0}},
              lineColor={0,0,0},
              fillColor={238,46,47},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-100,0},{100,-100}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{-150,140},{150,100}},
              textString="%name",
              lineColor={0,0,255})}),                                Diagram(
            coordinateSystem(preserveAspectRatio=false)));
    end SimpleHeaterCooler;
  end HVAC;

  package Refrigeration "Package for refrigeration models"
    model Refrigerator
      parameter Modelica.SIunits.Power Cap "Refrigerator cooling capacity";
      parameter Modelica.SIunits.DimensionlessRatio COP "Refrigerator coefficient of performance";
      Modelica.Thermal.HeatTransfer.Components.HeatCapacitor air(C=1e6)
        annotation (Placement(transformation(extent={{-10,0},{10,20}})));
      Modelica.Thermal.HeatTransfer.Components.ThermalResistor wall(R=0.01)
        annotation (Placement(transformation(extent={{-40,-10},{-20,10}})));
      Modelica.Thermal.HeatTransfer.Sources.PrescribedTemperature preAmb
        annotation (Placement(transformation(extent={{-80,-10},{-60,10}})));
      Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow preCool
        annotation (Placement(transformation(extent={{-40,-50},{-20,-30}})));
      Modelica.Blocks.Math.Gain gain(k=-Cap)
        annotation (Placement(transformation(extent={{-80,-50},{-60,-30}})));
      Modelica.Blocks.Math.Gain gain1(k=-1/COP)
        annotation (Placement(transformation(extent={{20,-70},{40,-50}})));
      Modelica.Blocks.Interfaces.RealInput Tamb
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealInput uCool
        annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
      Modelica.Blocks.Interfaces.RealOutput P "Output signal connector"
        annotation (Placement(transformation(extent={{100,-70},{120,-50}})));
      Modelica.Thermal.HeatTransfer.Sensors.TemperatureSensor temperatureSensor
        annotation (Placement(transformation(extent={{40,-10},{60,10}})));
      Modelica.Blocks.Interfaces.RealOutput T
        "Absolute temperature as output signal"
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
    equation
      connect(wall.port_b,air. port)
        annotation (Line(points={{-20,0},{0,0}}, color={191,0,0}));
      connect(preAmb.port,wall. port_a)
        annotation (Line(points={{-60,0},{-40,0}}, color={191,0,0}));
      connect(preCool.port,air. port)
        annotation (Line(points={{-20,-40},{0,-40},{0,0}}, color={191,0,0}));
      connect(gain.y,preCool. Q_flow)
        annotation (Line(points={{-59,-40},{-40,-40}}, color={0,0,127}));
      connect(gain.y,gain1. u) annotation (Line(points={{-59,-40},{-50,-40},{-50,
              -60},{18,-60}}, color={0,0,127}));
      connect(gain.u, uCool)
        annotation (Line(points={{-82,-40},{-120,-40}}, color={0,0,127}));
      connect(preAmb.T, Tamb)
        annotation (Line(points={{-82,0},{-120,0}}, color={0,0,127}));
      connect(gain1.y, P)
        annotation (Line(points={{41,-60},{110,-60}}, color={0,0,127}));
      connect(air.port, temperatureSensor.port)
        annotation (Line(points={{0,0},{40,0}}, color={191,0,0}));
      connect(temperatureSensor.T, T)
        annotation (Line(points={{60,0},{110,0}}, color={0,0,127}));
    annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
          coordinateSystem(preserveAspectRatio=false)));
    end Refrigerator;

    model Freezer
    annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
          coordinateSystem(preserveAspectRatio=false)));
    end Freezer;
  end Refrigeration;

  package Batteries "Package for battery models"

    model Simple
      "Simple battery model with SOC as state including charging, discharging"
      parameter Modelica.SIunits.Energy Ecap  "Battery capacity";
      parameter Modelica.SIunits.Power P_cap_charge "Charging capacity";
      parameter Modelica.SIunits.Power P_cap_discharge "Discharging capacity";
      parameter Modelica.SIunits.DimensionlessRatio eta_charge=0.9 "Charging efficiency";
      parameter Modelica.SIunits.DimensionlessRatio eta_discharge=0.9 "Discharging efficiency";
      parameter Modelica.SIunits.DimensionlessRatio SOC_0 "Initial state of charge";
      Modelica.SIunits.Energy E(fixed=true,start=SOC_0*Ecap) "Battery energy level";
      Modelica.SIunits.Power P_loss_charge "Charging losses of battery";
      Modelica.SIunits.Power P_loss_discharge "Discharging losses of battery";
      Modelica.Blocks.Interfaces.RealInput uCharge(min=0, max=1)
      "Control signal for charging"
        annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
      Modelica.Blocks.Interfaces.RealInput uDischarge(min=0, max=1)
      "Control signal for discharging"
        annotation (Placement(transformation(extent={{-140,-100},{-100,-60}})));
      Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
        annotation (Placement(transformation(extent={{100,-12},{124,12}})));
      Modelica.Blocks.Interfaces.RealOutput Pcharge "Battery charging power"
        annotation (Placement(transformation(extent={{100,-52},{124,-28}})));
      Modelica.Blocks.Interfaces.RealOutput Pdischarge
        "Battery discharging power"
        annotation (Placement(transformation(extent={{100,-92},{124,-68}})));
    equation
      SOC = E/Ecap;
      der(E) =Pcharge - Pdischarge - P_loss_charge - P_loss_discharge;
      Pcharge = uCharge*P_cap_charge;
      Pdischarge = uDischarge*P_cap_discharge;
      P_loss_charge =Pcharge*(1 - eta_charge);
      P_loss_discharge =Pdischarge*(1 - eta_discharge);
      annotation (Icon(graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-60,20},{62,-56}},
              lineColor={0,0,0},
              fillColor={135,135,135},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-40,42},{-18,20}},
              lineColor={0,0,0},
              fillColor={135,135,135},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{20,42},{42,20}},
              lineColor={0,0,0},
              fillColor={135,135,135},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{-250,170},{250,110}},
              textString="%name",
              lineColor={0,0,255})}));
    end Simple;

    package Examples
      extends Modelica.Icons.ExamplesPackage;
      model BatteryTest
        extends Modelica.Icons.Example;

        Modelica.Blocks.Sources.Pulse uCharge(
          offset=0,
          period=3600*6,
          startTime=3600*3,
          amplitude=0.5)
          annotation (Placement(transformation(extent={{-60,0},{-40,20}})));
        Modelica.Blocks.Sources.Pulse uDischarge(
          offset=0,
          period=3600*6,
          startTime=0,
          amplitude=0.5)
          annotation (Placement(transformation(extent={{-60,-30},{-40,-10}})));
        Simple simple(
          Ecap(displayUnit="kWh") = 180000000,
          P_cap_charge=500,
          P_cap_discharge=500,
          SOC_0=1)
          annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
      equation
        connect(uCharge.y, simple.uCharge) annotation (Line(points={{-39,10},{
                -30,10},{-30,-4},{-12,-4}}, color={0,0,127}));
        connect(uDischarge.y, simple.uDischarge) annotation (Line(points={{-39,
                -20},{-30,-20},{-30,-8},{-12,-8}}, color={0,0,127}));
        annotation (experiment(
            StopTime=86400,
            Interval=300,
            Tolerance=1e-06,
            __Dymola_Algorithm="Cvode"));
      end BatteryTest;
    end Examples;
  end Batteries;

  package PV "Package for PV models"
    model Simple
      "A simple PV model that uses single efficiency to account for module and inverter losses"
      parameter Modelica.SIunits.Area A "PV array area";
      parameter Modelica.SIunits.DimensionlessRatio eff=0.20 "Total efficiency of panel";
      Modelica.Blocks.Interfaces.RealInput Iinc
        "Solar irradiation incident on array"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealOutput Pgen "Power genereated by array"
        annotation (Placement(transformation(extent={{100,-12},{124,12}})));
      Modelica.Blocks.Math.Gain gainA(k=A)
        annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
      Modelica.Blocks.Math.Gain gainEff(k=eff)
        annotation (Placement(transformation(extent={{0,-10},{20,10}})));
    equation
      connect(gainA.u, Iinc)
        annotation (Line(points={{-62,0},{-120,0}}, color={0,0,127}));
      connect(gainA.y, gainEff.u)
        annotation (Line(points={{-39,0},{-2,0}}, color={0,0,127}));
      connect(gainEff.y, Pgen)
        annotation (Line(points={{21,0},{112,0}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
            Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={255,255,255},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-48,76},{0,24}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{0,76},{48,24}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{0,24},{48,-28}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-48,24},{0,-28}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{0,-28},{48,-80}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Rectangle(
              extent={{-48,-28},{0,-80}},
              lineColor={0,0,0},
              fillColor={28,108,200},
              fillPattern=FillPattern.Solid),
            Text(
              extent={{-250,170},{250,110}},
              textString="%name",
              lineColor={0,0,255})}),                                Diagram(
            coordinateSystem(preserveAspectRatio=false)));
    end Simple;
  end PV;

  package Building "Package for building models"

    model Whole_Derivative
      extends BaseClasses.Whole;
      parameter Modelica.SIunits.DimensionlessRatio uHeat_0 = 0.0 "Initial heating signal";
      parameter Modelica.SIunits.DimensionlessRatio uCool_0 = 0.0 "Initial cooling signal";
      parameter Modelica.SIunits.DimensionlessRatio uCharge_0 = 0.0 "Initial charging signal";
      parameter Modelica.SIunits.DimensionlessRatio uDischarge_0 = 0.0 "Initial discharging signal";
      Modelica.Blocks.Interfaces.RealInput duHeat
        "Derivative of heating signal input"
        annotation (Placement(transformation(extent={{-140,0},{-100,40}})));
      Modelica.Blocks.Continuous.Integrator intHeat(initType=Modelica.Blocks.Types.Init.InitialState, y_start=
          uHeat_0)
        annotation (Placement(transformation(extent={{-94,16},{-86,24}})));
      Modelica.Blocks.Continuous.Integrator intCool(initType=Modelica.Blocks.Types.Init.InitialState, y_start=
          uCool_0)
        annotation (Placement(transformation(extent={{-94,-24},{-86,-16}})));
      Modelica.Blocks.Interfaces.RealInput duCool
        "Derivative of cooling signal input"
        annotation (Placement(transformation(extent={{-140,-40},{-100,0}})));
      Modelica.Blocks.Interfaces.RealInput duCharge
        "Derivative of control signal for charging"
        annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
      Modelica.Blocks.Continuous.Integrator intCharge(initType=Modelica.Blocks.Types.Init.InitialState, y_start=
          uCharge_0)
        annotation (Placement(transformation(extent={{-94,-64},{-86,-56}})));
      Modelica.Blocks.Continuous.Integrator intDischarge(initType=Modelica.Blocks.Types.Init.InitialState, y_start=
          uDischarge_0)
        annotation (Placement(transformation(extent={{-94,-104},{-86,-96}})));
      Modelica.Blocks.Interfaces.RealInput duDischarge
        "Derivative of control signal for discharging"
        annotation (Placement(transformation(extent={{-140,-120},{-100,-80}})));
    Modelica.Blocks.Interfaces.RealOutput uDischarge
      "Connector of Real output signal"
      annotation (Placement(transformation(extent={{100,-130},{120,-110}})));
    Modelica.Blocks.Interfaces.RealOutput uCharge
      "Connector of Real output signal"
      annotation (Placement(transformation(extent={{100,-110},{120,-90}})));
    Modelica.Blocks.Interfaces.RealOutput uCool
      "Connector of Real output signal"
      annotation (Placement(transformation(extent={{100,-90},{120,-70}})));
    Modelica.Blocks.Interfaces.RealOutput uHeat
      "Connector of Real output signal"
      annotation (Placement(transformation(extent={{100,-70},{120,-50}})));
    equation
      connect(duHeat, intHeat.u)
        annotation (Line(points={{-120,20},{-94.8,20}}, color={0,0,127}));
      connect(duCool, intCool.u)
        annotation (Line(points={{-120,-20},{-94.8,-20}}, color={0,0,127}));
      connect(duCharge, intCharge.u) annotation (Line(points={{-120,-60},{-108,-60},
              {-108,-60},{-94.8,-60}}, color={0,0,127}));
      connect(duDischarge, intDischarge.u)
        annotation (Line(points={{-120,-100},{-94.8,-100}}, color={0,0,127}));
      connect(intHeat.y, thermal.uHeat) annotation (Line(points={{-85.6,20},{
            -70,20},{-70,16},{-42,16}},
                                color={0,0,127}));
      connect(thermal.uCool, intCool.y) annotation (Line(points={{-42,12},{-70,
            12},{-70,-20},{-85.6,-20}},
                                 color={0,0,127}));
      connect(battery.uCharge, intCharge.y) annotation (Line(points={{-42,-34},{-70,
              -34},{-70,-60},{-85.6,-60}}, color={0,0,127}));
      connect(battery.uDischarge, intDischarge.y) annotation (Line(points={{-42,-38},
              {-60,-38},{-60,-100},{-85.6,-100}}, color={0,0,127}));
      connect(intHeat.y, uHeat) annotation (Line(points={{-85.6,20},{-70,20},{-70,6},
              {-50,6},{-50,-60},{110,-60}}, color={0,0,127}));
      connect(intCool.y, uCool) annotation (Line(points={{-85.6,-20},{-70,-20},{-70,
              2},{-52,2},{-52,-80},{110,-80}}, color={0,0,127}));
      connect(intCharge.y, uCharge) annotation (Line(points={{-85.6,-60},{-70,-60},{
              -70,-34},{-54,-34},{-54,-100},{110,-100}}, color={0,0,127}));
      connect(intDischarge.y, uDischarge) annotation (Line(points={{-85.6,-100},{-60,
              -100},{-60,-120},{110,-120}}, color={0,0,127}));
    annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={175,175,175},
              fillPattern=FillPattern.Solid)}),                    Diagram(
          coordinateSystem(preserveAspectRatio=false)));
    end Whole_Derivative;

    model Whole_Inputs
      extends BaseClasses.Whole(pv(A=300), battery(
        Ecap=626400000,
        P_cap_charge=109000,
        P_cap_discharge=109000));
    Modelica.Blocks.Interfaces.RealInput uHeat
      "Heating signal input (must be positive)"
      annotation (Placement(transformation(extent={{-140,0},{-100,40}})));
    Modelica.Blocks.Interfaces.RealInput uCool
      "Cooling signal input (must be negative)"
      annotation (Placement(transformation(extent={{-140,-40},{-100,0}})));
    Modelica.Blocks.Interfaces.RealInput uCharge "Control signal for charging"
      annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
    Modelica.Blocks.Interfaces.RealInput uDischarge
      "Control signal for discharging"
      annotation (Placement(transformation(extent={{-140,-120},{-100,-80}})));
      Modelica.Blocks.Interfaces.RealOutput J
      "Objective function for optimization"
      annotation (Placement(transformation(extent={{100,-190},{120,-170}})));
    Modelica.Blocks.Math.Product squareHeat
      annotation (Placement(transformation(extent={{42,-156},{48,-150}})));
    Modelica.Blocks.Math.Product squareCool
      annotation (Placement(transformation(extent={{42,-166},{48,-160}})));
    Modelica.Blocks.Math.Gain gainDischarge(k=10)
      annotation (Placement(transformation(extent={{54,-186},{60,-180}})));
    Modelica.Blocks.Math.Product squareCharge
      annotation (Placement(transformation(extent={{42,-176},{48,-170}})));
    Modelica.Blocks.Math.Product squareDischarge
      annotation (Placement(transformation(extent={{42,-186},{48,-180}})));
    Modelica.Blocks.Math.Gain gainCharge(k=10)
      annotation (Placement(transformation(extent={{54,-176},{60,-170}})));
    Modelica.Blocks.Math.Gain gainCool(k=1000)
      annotation (Placement(transformation(extent={{54,-166},{60,-160}})));
    Modelica.Blocks.Math.Gain gainHeat(k=1000)
      annotation (Placement(transformation(extent={{54,-156},{60,-150}})));
      Modelica.Blocks.Math.MultiSum sumJ(nu=8, k={1,1,1,1,1,1,1,1})
      annotation (Placement(transformation(extent={{78,-186},{90,-174}})));
    Modelica.Blocks.Interfaces.RealInput uRef
      "Cooling signal input for refrigerator"
      annotation (Placement(transformation(extent={{-140,-160},{-100,-120}})));
    Modelica.Blocks.Interfaces.RealInput uFreDef
      "Defrost signal input for freezer"
      annotation (Placement(transformation(extent={{-140,-200},{-100,-160}})));
    Modelica.Blocks.Interfaces.RealInput uFreCool
      "Cooling signal input for freezer"
      annotation (Placement(transformation(extent={{-140,-240},{-100,-200}})));
    Modelica.Blocks.Math.Gain gainDischarge1(
                                            k=10)
      annotation (Placement(transformation(extent={{54,-196},{60,-190}})));
    Modelica.Blocks.Math.Product squareDischarge1
      annotation (Placement(transformation(extent={{42,-196},{48,-190}})));
    Modelica.Blocks.Math.Gain gainDischarge2(
                                            k=10)
      annotation (Placement(transformation(extent={{54,-206},{60,-200}})));
    Modelica.Blocks.Math.Product squareDischarge2
      annotation (Placement(transformation(extent={{42,-206},{48,-200}})));
    Modelica.Blocks.Math.Gain gainDischarge3(
                                            k=10)
      annotation (Placement(transformation(extent={{54,-216},{60,-210}})));
    Modelica.Blocks.Math.Product squareDischarge3
      annotation (Placement(transformation(extent={{42,-216},{48,-210}})));
    equation
    connect(thermal.uHeat, uHeat) annotation (Line(points={{-42,16},{-80,16},{
            -80,20},{-120,20}},
                            color={0,0,127}));
    connect(thermal.uCool, uCool) annotation (Line(points={{-42,12},{-94,12},{
            -94,-20},{-120,-20}},
                              color={0,0,127}));
    connect(battery.uCharge, uCharge) annotation (Line(points={{-42,-34},{-86,
            -34},{-86,-60},{-120,-60}}, color={0,0,127}));
    connect(battery.uDischarge, uDischarge) annotation (Line(points={{-42,-38},
            {-82,-38},{-82,-100},{-120,-100}}, color={0,0,127}));
    connect(squareDischarge.y, gainDischarge.u)
      annotation (Line(points={{48.3,-183},{53.4,-183}},
                                                       color={0,0,127}));
    connect(squareCharge.y, gainCharge.u)
      annotation (Line(points={{48.3,-173},{53.4,-173}},
                                                       color={0,0,127}));
    connect(squareCool.y, gainCool.u)
      annotation (Line(points={{48.3,-163},{53.4,-163}},
                                                       color={0,0,127}));
    connect(squareHeat.y, gainHeat.u)
      annotation (Line(points={{48.3,-153},{53.4,-153}},
                                                       color={0,0,127}));
    connect(sumPnet.y, sumJ.u[1]) annotation (Line(points={{89.02,0},{94,0},{94,
            -30},{74,-30},{74,-176.325},{78,-176.325}},        color={0,0,127}));
    connect(gainHeat.y, sumJ.u[2]) annotation (Line(points={{60.3,-153},{66,
            -153},{66,-177.375},{78,-177.375}},
                                      color={0,0,127}));
    connect(gainCool.y, sumJ.u[3]) annotation (Line(points={{60.3,-163},{70,
            -163},{70,-178.425},{78,-178.425}},
                                color={0,0,127}));
    connect(gainCharge.y, sumJ.u[4]) annotation (Line(points={{60.3,-173},{66,
            -173},{66,-179.475},{78,-179.475}},
                                           color={0,0,127}));
    connect(gainDischarge.y, sumJ.u[5]) annotation (Line(points={{60.3,-183},{
            74,-183},{74,-180.525},{78,-180.525}},
                                           color={0,0,127}));
    connect(sumJ.y, J) annotation (Line(points={{91.02,-180},{110,-180}},
                       color={0,0,127}));
    connect(uHeat, squareHeat.u1) annotation (Line(points={{-120,20},{-98,20},{
            -98,6},{-98,6},{-98,-151.2},{41.4,-151.2}},
                                                      color={0,0,127}));
    connect(squareHeat.u2, squareHeat.u1) annotation (Line(points={{41.4,-154.8},
            {20,-154.8},{20,-151.2},{41.4,-151.2}},
                                                 color={0,0,127}));
    connect(uCool, squareCool.u1) annotation (Line(points={{-120,-20},{-94,-20},
            {-94,-20},{-94,-20},{-94,-161.2},{41.4,-161.2}},
                                                       color={0,0,127}));
    connect(squareCool.u2, squareCool.u1) annotation (Line(points={{41.4,-164.8},
            {20,-164.8},{20,-161.2},{41.4,-161.2}},
                                                 color={0,0,127}));
    connect(uCharge, squareCharge.u1) annotation (Line(points={{-120,-60},{-90,
            -60},{-90,-60},{-86,-60},{-86,-171.2},{41.4,-171.2}},
                                                                color={0,0,127}));
    connect(squareCharge.u2, squareCharge.u1) annotation (Line(points={{41.4,
            -174.8},{20,-174.8},{20,-171.2},{41.4,-171.2}},
                                                        color={0,0,127}));
    connect(uDischarge, squareDischarge.u1) annotation (Line(points={{-120,-100},
            {-82,-100},{-82,-181.2},{41.4,-181.2}},
                                                  color={0,0,127}));
    connect(squareDischarge.u2, squareDischarge.u1) annotation (Line(points={{41.4,
            -184.8},{20,-184.8},{20,-181.2},{41.4,-181.2}},  color={0,0,127}));
    connect(thermal.uRef, uRef) annotation (Line(points={{-42,8},{-90,8},{-90,
            -20},{-90,-20},{-90,-140},{-120,-140}}, color={0,0,127}));
    connect(thermal.uFreDef, uFreDef) annotation (Line(points={{-42,4},{-78,4},
            {-78,-180},{-120,-180}}, color={0,0,127}));
    connect(thermal.uFreCool, uFreCool) annotation (Line(points={{-42,0},{-74,0},
            {-74,-220},{-120,-220}}, color={0,0,127}));
    connect(squareDischarge1.y, gainDischarge1.u)
      annotation (Line(points={{48.3,-193},{53.4,-193}},
                                                       color={0,0,127}));
    connect(squareDischarge2.y, gainDischarge2.u)
      annotation (Line(points={{48.3,-203},{53.4,-203}},
                                                       color={0,0,127}));
    connect(squareDischarge3.y, gainDischarge3.u)
      annotation (Line(points={{48.3,-213},{53.4,-213}}, color={0,0,127}));
    connect(gainDischarge1.y, sumJ.u[6]) annotation (Line(points={{60.3,-193},{
            68,-193},{68,-181.575},{78,-181.575}},
                                                color={0,0,127}));
    connect(gainDischarge2.y, sumJ.u[7]) annotation (Line(points={{60.3,-203},{
            72,-203},{72,-182.625},{78,-182.625}},
                                                color={0,0,127}));
    connect(gainDischarge3.y, sumJ.u[8]) annotation (Line(points={{60.3,-213},{
            76,-213},{76,-183.675},{78,-183.675}},
                                                 color={0,0,127}));
    connect(uRef, squareDischarge1.u1) annotation (Line(points={{-120,-140},{
            -90,-140},{-90,-140},{-90,-140},{-90,-191.2},{41.4,-191.2}},
                                                                       color={0,
            0,127}));
    connect(squareDischarge1.u2, squareDischarge1.u1) annotation (Line(points={{41.4,
            -194.8},{20,-194.8},{20,-191.2},{41.4,-191.2}},   color={0,0,127}));
    connect(uFreDef, squareDischarge2.u1) annotation (Line(points={{-120,-180},
            {-78,-180},{-78,-202},{-4,-202},{-4,-201.2},{41.4,-201.2}},
                                                  color={0,0,127}));
    connect(squareDischarge2.u2, squareDischarge2.u1) annotation (Line(points={{41.4,
            -204.8},{20,-204.8},{20,-201.2},{41.4,-201.2}},     color={0,0,127}));
    connect(uFreCool, squareDischarge3.u1) annotation (Line(points={{-120,-220},
            {0,-220},{0,-211.2},{41.4,-211.2}}, color={0,0,127}));
    connect(squareDischarge3.u2, squareDischarge3.u1) annotation (Line(points={{41.4,
            -214.8},{20,-214.8},{20,-211.2},{41.4,-211.2}},       color={0,0,
            127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
            coordinateSystem(preserveAspectRatio=false)));
    end Whole_Inputs;

    package Examples
      extends Modelica.Icons.ExamplesPackage;
      model Building
        extends Modelica.Icons.Example
        annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
              coordinateSystem(preserveAspectRatio=false)));
      end Building;
    end Examples;

    package BaseClasses
      model Whole
        parameter Modelica.SIunits.Temperature Tzone_0=22+273.15 "Initial temperature of zone";
        parameter Modelica.SIunits.DimensionlessRatio SOC_0 = 0.5 "Initial SOC of battery";
        Thermal thermal(Tzone_0=Tzone_0)
        annotation (Placement(transformation(extent={{-40,0},{-20,20}})));
        Batteries.Simple battery(
          Ecap(displayUnit="kWh") = 21600000,
          P_cap_charge=1000,
          P_cap_discharge=1000,
        SOC_0=SOC_0)
          annotation (Placement(transformation(extent={{-40,-40},{-20,-20}})));
        PV.Simple pv(A=5)
          annotation (Placement(transformation(extent={{-40,70},{-20,90}})));
        Modelica.Blocks.Interfaces.RealInput weaHGloHor
          "Global horizontal irradiation"
          annotation (Placement(transformation(extent={{-140,80},{-100,120}})));
        Modelica.Blocks.Interfaces.RealInput weaTDryBul
          "Outside air drybulb temperature"
          annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
        Modelica.Blocks.Interfaces.RealOutput Pnet
          annotation (Placement(transformation(extent={{100,-70},{120,-50}})));
        Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
          annotation (Placement(transformation(extent={{100,-110},{120,-90}})));
        Modelica.Blocks.Interfaces.RealOutput Tzone "Zone air temperature"
          annotation (Placement(transformation(extent={{100,-90},{120,-70}})));
        Modelica.Blocks.Math.Gain gainPVGen(k=-1)
          annotation (Placement(transformation(extent={{28,94},{40,106}})));
        Modelica.Blocks.Interfaces.RealOutput Ppv "Power generated by PV system"
          annotation (Placement(transformation(extent={{100,90},{120,110}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu
        "RTU electrical power consumption"
        annotation (Placement(transformation(extent={{100,70},{120,90}})));
        Modelica.Blocks.Interfaces.RealOutput Pcharge
          "Battery charging power consumption"
          annotation (Placement(transformation(extent={{100,10},{120,30}})));
        Modelica.Blocks.Interfaces.RealOutput Pdischarge
          "Battery discharging power generation"
          annotation (Placement(transformation(extent={{100,-10},{120,10}})));
        Modelica.Blocks.Math.Gain gainBatteryGen(k=-1)
          annotation (Placement(transformation(extent={{28,-6},{40,6}})));
      Modelica.Blocks.Interfaces.RealOutput Tref "Refrigerator air temperature"
        annotation (Placement(transformation(extent={{100,-130},{120,-110}})));
      Modelica.Blocks.Interfaces.RealOutput Pref "Refrigerator power"
        annotation (Placement(transformation(extent={{100,50},{120,70}})));
      Modelica.Blocks.Interfaces.RealOutput Pfre "Freezer power"
        annotation (Placement(transformation(extent={{100,30},{120,50}})));
      Modelica.Blocks.Interfaces.RealOutput Tfre "Freezer air temperature"
        annotation (Placement(transformation(extent={{100,-150},{120,-130}})));
      Modelica.Blocks.Math.MultiSum multiSum(k={-1,1,1,1,1,-1}, nu=6)
        annotation (Placement(transformation(extent={{80,-66},{92,-54}})));
      equation
        connect(pv.Iinc, weaHGloHor) annotation (Line(points={{-42,80},{-50,80},
              {-50,100},{-120,100}},  color={0,0,127}));
        connect(thermal.Tout, weaTDryBul) annotation (Line(points={{-42,20},{
              -60,20},{-60,60},{-80,60},{-80,60},{-120,60}},
                                                           color={0,0,127}));
        connect(battery.SOC, SOC) annotation (Line(points={{-18.8,-30},{-12,-30},
              {-12,-100},{110,-100}}, color={0,0,127}));
      connect(thermal.Trtu, Tzone) annotation (Line(points={{-19,20},{10,20},{
              10,-80},{110,-80}},  color={0,0,127}));
        connect(pv.Pgen, gainPVGen.u)
          annotation (Line(points={{-18.8,80},{-10,80},{-10,100},{26.8,100}},
                                                           color={0,0,127}));
        connect(gainPVGen.y, Ppv) annotation (Line(points={{40.6,100},{110,100}},
                                 color={0,0,127}));
      connect(thermal.Prtu, Prtu) annotation (Line(points={{-19,18},{-4,18},{-4,
              80},{110,80}}, color={0,0,127}));
        connect(battery.Pcharge, Pcharge) annotation (Line(points={{-18.8,-34},
              {18,-34},{18,20},{110,20}},  color={0,0,127}));
        connect(battery.Pdischarge, gainBatteryGen.u)
          annotation (Line(points={{-18.8,-38},{20,-38},{20,0},{26.8,0}},
                                                            color={0,0,127}));
        connect(gainBatteryGen.y, Pdischarge) annotation (Line(points={{40.6,0},
              {110,0}},                     color={0,0,127}));
      connect(thermal.Tref, Tref) annotation (Line(points={{-19,14},{8,14},{8,
              -120},{110,-120}},                 color={0,0,127}));
      connect(thermal.Pref, Pref) annotation (Line(points={{-19,12},{0,12},{0,
              60},{110,60}},                 color={0,0,127}));
      connect(thermal.Pfre, Pfre) annotation (Line(points={{-19,6},{4,6},{4,40},
              {110,40}}, color={0,0,127}));
      connect(thermal.Tfre, Tfre) annotation (Line(points={{-19,8},{6,8},{6,
              -140},{110,-140}},                 color={0,0,127}));
      connect(multiSum.y, Pnet)
        annotation (Line(points={{93.02,-60},{110,-60}},
                                                     color={0,0,127}));
      connect(gainPVGen.y, multiSum.u[1]) annotation (Line(points={{40.6,100},{
              50,100},{50,-56.5},{80,-56.5}},
                                          color={0,0,127}));
      connect(Prtu, Prtu)
        annotation (Line(points={{110,80},{110,80}}, color={0,0,127}));
      connect(multiSum.u[2], Prtu) annotation (Line(points={{80,-57.9},{52,
              -57.9},{52,80},{110,80}},
                                color={0,0,127}));
      connect(multiSum.u[3], Pref) annotation (Line(points={{80,-59.3},{54,
              -59.3},{54,60},{110,60}},
                                color={0,0,127}));
      connect(multiSum.u[4], Pfre) annotation (Line(points={{80,-60.7},{56,
              -60.7},{56,40},{110,40}},          color={0,0,127}));
      connect(multiSum.u[5], Pcharge) annotation (Line(points={{80,-62.1},{80,
              -62},{58,-62},{58,20},{110,20}},
                                       color={0,0,127}));
      connect(multiSum.u[6], Pdischarge) annotation (Line(points={{80,-63.5},{
              80,-62},{60,-62},{60,0},{110,0}},
                                             color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{
                -100,-220},{100,100}}),                             graphics={
                Rectangle(
                extent={{-100,100},{100,-100}},
                lineColor={0,0,0},
                fillColor={175,175,175},
                fillPattern=FillPattern.Solid)}),                    Diagram(
            coordinateSystem(preserveAspectRatio=false, extent={{-100,-220},{
                100,100}})));
      end Whole;

      model Thermal
        parameter Modelica.SIunits.Temperature Trtu_0 "Initial temperature of rtu zone";
        parameter Modelica.SIunits.Temperature Tref_0 "Initial temperature of ref zone";
        parameter Modelica.SIunits.Temperature Tfre_0 "Initial temperature of fre zone";
        Envelope.R1C1 rtuZone(Tzone_0=Trtu_0)
          annotation (Placement(transformation(extent={{-10,80},{10,100}})));
        HVAC.SimpleHeaterCooler RTU1(heatingCap=2000, coolingCap=18000)
          annotation (Placement(transformation(extent={{-60,70},{-40,90}})));
        Modelica.Blocks.Interfaces.RealInput Tout "Adjacent temperature"
        annotation (Placement(transformation(extent={{-140,80},{-100,120}})));
        Modelica.Blocks.Interfaces.RealInput uCool "Cooling signal input for RTU"
        annotation (Placement(transformation(extent={{-140,0},{-100,40}})));
        Modelica.Blocks.Interfaces.RealInput uHeat "Heating signal input"
        annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
        Modelica.Blocks.Interfaces.RealOutput Trtu "Zone air temperature"
          annotation (Placement(transformation(extent={{100,90},{120,110}})));
        Modelica.Blocks.Interfaces.RealOutput Prtu "RTU power"
          annotation (Placement(transformation(extent={{100,70},{120,90}})));
        Envelope.R1C1 refZone(Tzone_0=Tref_0)
          annotation (Placement(transformation(extent={{40,20},{60,40}})));
        Modelica.Blocks.Interfaces.RealOutput Tref "Refrigerator air temperature"
          annotation (Placement(transformation(extent={{100,30},{120,50}})));
        HVAC.SimpleHeaterCooler refCooler(                 heatingCap=0,
          coolingCap=1500)
          annotation (Placement(transformation(extent={{-10,10},{10,30}})));
        Modelica.Blocks.Math.Add addRTU
          annotation (Placement(transformation(extent={{50,50},{70,70}})));
        Modelica.Blocks.Interfaces.RealOutput Pref "Refrigerator power"
          annotation (Placement(transformation(extent={{100,10},{120,30}})));
        Modelica.Blocks.Math.Add addRef
          annotation (Placement(transformation(extent={{50,-10},{70,10}})));
        Modelica.Blocks.Sources.Constant uRefHeat(k=0)
          annotation (Placement(transformation(extent={{-60,10},{-40,30}})));
        Modelica.Blocks.Interfaces.RealInput uRef
          "Cooling signal input for refrigerator"
          annotation (Placement(transformation(extent={{-140,-40},{-100,0}})));
        Envelope.R1C1 freZone(Tzone_0=Tfre_0)
          annotation (Placement(transformation(extent={{40,-40},{60,-20}})));
        Modelica.Blocks.Math.Add addFre
          annotation (Placement(transformation(extent={{50,-70},{70,-50}})));
        Modelica.Blocks.Interfaces.RealOutput Pfre "Freezer power"
          annotation (Placement(transformation(extent={{100,-50},{120,-30}})));
        HVAC.SimpleHeaterCooler freCooler(                 heatingCap=0,
          coolingCap=1500)
          annotation (Placement(transformation(extent={{-10,-50},{10,-30}})));
        Modelica.Blocks.Interfaces.RealInput uFreCool
          "Cooling signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-120},{-100,-80}})));
        Modelica.Blocks.Interfaces.RealInput uFreDef
          "Defrost signal input for freezer"
          annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
        Modelica.Blocks.Interfaces.RealOutput Tfre "Freezer air temperature"
          annotation (Placement(transformation(extent={{100,-30},{120,-10}})));
      equation
        connect(RTU1.qHeat, rtuZone.qHeat)
          annotation (Line(points={{-39,86},{-12,86}}, color={0,0,127}));
        connect(RTU1.qCool, rtuZone.qCool) annotation (Line(points={{-39,76},{
              -22,76},{-22,82},{-12,82}},
                                    color={0,0,127}));
        connect(rtuZone.Tadj, Tout) annotation (Line(points={{-12,96},{-68,96},
              {-68,100},{-120,100}},
                             color={0,0,127}));
        connect(RTU1.uCool, uCool) annotation (Line(points={{-62,72},{-80,72},{
              -80,20},{-120,20}},
                            color={0,0,127}));
        connect(RTU1.uHeat, uHeat) annotation (Line(points={{-62,88},{-90,88},{
              -90,60},{-120,60}},
                            color={0,0,127}));
        connect(rtuZone.Tzone, Trtu)
          annotation (Line(points={{11,90},{20,90},{20,100},{110,100}},
                                                      color={0,0,127}));
        connect(refZone.Tzone, Tref)
          annotation (Line(points={{61,30},{80,30},{80,40},{110,40}},
                                                      color={0,0,127}));
        connect(rtuZone.Tzone, refZone.Tadj) annotation (Line(points={{11,90},{
              20,90},{20,36},{38,36}},
                                  color={0,0,127}));
        connect(RTU1.PHeat, addRTU.u1) annotation (Line(points={{-39,82},{-30,
              82},{-30,66},{48,66}},
                                color={0,0,127}));
        connect(RTU1.PCool, addRTU.u2) annotation (Line(points={{-39,72},{-34,
              72},{-34,54},{48,54}},
                                  color={0,0,127}));
        connect(addRTU.y, Prtu) annotation (Line(points={{71,60},{80,60},{80,80},
              {110,80}},                         color={0,0,127}));
        connect(refCooler.qCool, refZone.qCool) annotation (Line(points={{11,16},{32,16},
                {32,22},{38,22}}, color={0,0,127}));
        connect(addRef.y, Pref)
          annotation (Line(points={{71,0},{80,0},{80,20},{110,20}},
                                                    color={0,0,127}));
        connect(refCooler.PCool, addRef.u2) annotation (Line(points={{11,12},{
              24,12},{24,-6},{48,-6}},
                                 color={0,0,127}));
        connect(refCooler.PHeat, addRef.u1)
          annotation (Line(points={{11,22},{26,22},{26,6},{48,6}}, color={0,0,127}));
        connect(refCooler.qHeat, refZone.qHeat)
          annotation (Line(points={{11,26},{38,26}}, color={0,0,127}));
        connect(uRefHeat.y, refCooler.uHeat) annotation (Line(points={{-39,20},{-22,20},
                {-22,28},{-12,28}}, color={0,0,127}));
        connect(refCooler.uCool, uRef) annotation (Line(points={{-12,12},{-20,12},{-20,
                -20},{-120,-20}}, color={0,0,127}));
        connect(rtuZone.Tzone, freZone.Tadj) annotation (Line(points={{11,90},{
              20,90},{20,-24},{38,-24}},
                                    color={0,0,127}));
        connect(addFre.y, Pfre)
          annotation (Line(points={{71,-60},{80,-60},{80,-40},{110,-40}},
                                                        color={0,0,127}));
        connect(uFreDef, freCooler.uHeat) annotation (Line(points={{-120,-60},{-60,-60},
                {-60,-32},{-12,-32}}, color={0,0,127}));
        connect(freCooler.uCool, uFreCool) annotation (Line(points={{-12,-48},{-40,-48},
                {-40,-100},{-120,-100}}, color={0,0,127}));
        connect(freCooler.qHeat, freZone.qHeat)
          annotation (Line(points={{11,-34},{38,-34}}, color={0,0,127}));
        connect(freCooler.qCool, freZone.qCool) annotation (Line(points={{11,-44},{32,
                -44},{32,-38},{38,-38}}, color={0,0,127}));
        connect(freCooler.PHeat, addFre.u1) annotation (Line(points={{11,-38},{
              26,-38},{26,-54},{48,-54}},
                                    color={0,0,127}));
        connect(freCooler.PCool, addFre.u2) annotation (Line(points={{11,-48},{
              24,-48},{24,-66},{48,-66}},
                                    color={0,0,127}));
        connect(freZone.Tzone, Tfre)
          annotation (Line(points={{61,-30},{80,-30},{80,-20},{110,-20}},
                                                        color={0,0,127}));
        connect(Tfre, Tfre)
          annotation (Line(points={{110,-20},{110,-20}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
              Rectangle(
              extent={{-100,100},{100,-100}},
              lineColor={0,0,0},
              fillColor={255,170,170},
              fillPattern=FillPattern.Solid), Text(
              extent={{-26,8},{26,-4}},
              lineColor={0,0,0},
              fillColor={255,170,170},
              fillPattern=FillPattern.Solid,
              textString="Thermal"),
              Text(
                extent={{-250,170},{250,110}},
                textString="%name",
                lineColor={0,0,255})}),                              Diagram(
            coordinateSystem(preserveAspectRatio=false)));
      end Thermal;
    end BaseClasses;
  end Building;


annotation (uses(Modelica(version="3.2.2"), Buildings(version="5.0.0")));
end MPC;
