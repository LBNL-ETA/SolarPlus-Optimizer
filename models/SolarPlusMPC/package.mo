within ;
package SolarPlusMPC "This package contains models for MPC control optimization."






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
      Modelica.Blocks.Interfaces.RealInput uHeat(min=0,max=1)
      "Heating signal input"
        annotation (Placement(transformation(extent={{-140,60},{-100,100}})));
      Modelica.Blocks.Interfaces.RealInput uCool(min=0,max=1)
      "Cooling signal input"
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
    connect(coolingPowerGain.u, negHeatFlow.u) annotation (Line(points={{58,-80},
            {20,-80},{20,-40},{58,-40}}, color={0,0,127}));
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
      "Simple battery model with SOC as state including charging, discharging, and standing losses seperately"
      parameter Modelica.SIunits.Energy Ecap  "Battery capacity";
      parameter Modelica.SIunits.Power P_cap_charge "Charging capacity";
      parameter Modelica.SIunits.Power P_cap_discharge "Discharging capacity";
      parameter Modelica.SIunits.DimensionlessRatio eta_charge=0.9 "Charging efficiency";
      parameter Modelica.SIunits.DimensionlessRatio eta_discharge=0.9 "Discharging efficiency";
      parameter Modelica.SIunits.DimensionlessRatio tau_sl=0.001 "Standing loss coefficient";
      parameter Real SOC_0 = 0 "Initial state of charge";
      Modelica.SIunits.Energy E(start=SOC_0*Ecap) "Battery energy level";
      Modelica.SIunits.Power P_loss_charge "Charging losses of battery";
      Modelica.SIunits.Power P_loss_discharge "Discharging losses of battery";
      Modelica.SIunits.Power P_loss_standing "Standing losses of battery";
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
      der(E) =Pcharge - Pdischarge - P_loss_charge - P_loss_discharge -
      P_loss_standing;
    Pcharge = uCharge*P_cap_charge;
    Pdischarge = uDischarge*P_cap_discharge;
      P_loss_charge =Pcharge*(1 - eta_charge);
      P_loss_discharge =Pdischarge*(1 - eta_discharge);
      P_loss_standing = SOC*tau_sl/3600;
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
      connect(uCharge.y, simple.uCharge) annotation (Line(points={{-39,10},{-30,
              10},{-30,-4},{-12,-4}}, color={0,0,127}));
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

    model Thermal
    Envelope.R1C1 r1C1_1
      annotation (Placement(transformation(extent={{-12,-10},{8,10}})));
    HVAC.SimpleHeaterCooler simpleHeaterCooler(heatingCap=1000, coolingCap=1000)
      annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
    Modelica.Blocks.Interfaces.RealInput Tadj "Adjacent temperature"
      annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
    Modelica.Blocks.Interfaces.RealInput uCool
      "Cooling signal input (must be negative)"
      annotation (Placement(transformation(extent={{-140,-100},{-100,-60}})));
    Modelica.Blocks.Interfaces.RealInput uHeat
      "Heating signal input (must be positive)"
      annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
    Modelica.Blocks.Interfaces.RealOutput Tzone "Zone air temperature"
      annotation (Placement(transformation(extent={{100,-10},{120,10}})));
    Modelica.Blocks.Interfaces.RealOutput PHeat
      "Heating electrical power output"
      annotation (Placement(transformation(extent={{100,-50},{120,-30}})));
    Modelica.Blocks.Interfaces.RealOutput PCool
      "Cooling electrical power output"
      annotation (Placement(transformation(extent={{100,-90},{120,-70}})));
    equation
    connect(simpleHeaterCooler.qHeat, r1C1_1.qHeat) annotation (Line(points={{
            -39,6},{-28,6},{-28,-4},{-14,-4}}, color={0,0,127}));
    connect(simpleHeaterCooler.qCool, r1C1_1.qCool) annotation (Line(points={{
            -39,-4},{-34,-4},{-34,-8},{-14,-8}}, color={0,0,127}));
    connect(r1C1_1.Tadj, Tadj) annotation (Line(points={{-14,6},{-20,6},{-20,60},
            {-120,60}}, color={0,0,127}));
    connect(simpleHeaterCooler.uCool, uCool) annotation (Line(points={{-62,-8},
            {-80,-8},{-80,-80},{-120,-80}}, color={0,0,127}));
    connect(simpleHeaterCooler.uHeat, uHeat) annotation (Line(points={{-62,8},{
            -90,8},{-90,-40},{-120,-40}}, color={0,0,127}));
    connect(r1C1_1.Tzone, Tzone)
      annotation (Line(points={{9,0},{110,0}}, color={0,0,127}));
    connect(simpleHeaterCooler.PHeat, PHeat) annotation (Line(points={{-39,2},{
            -30,2},{-30,-40},{110,-40}}, color={0,0,127}));
    connect(simpleHeaterCooler.PCool, PCool) annotation (Line(points={{-39,-8},
            {-36,-8},{-36,-80},{110,-80}}, color={0,0,127}));
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

    model Whole
    Thermal thermal
      annotation (Placement(transformation(extent={{-40,0},{-20,20}})));
    Batteries.Simple battery(
      Ecap(displayUnit="kWh") = 21600000,
      P_cap_charge=1000,
      P_cap_discharge=1000,
      SOC_0=1)
      annotation (Placement(transformation(extent={{-40,-40},{-20,-20}})));
    PV.Simple pv(A=5)
      annotation (Placement(transformation(extent={{-40,40},{-20,60}})));
    Modelica.Blocks.Interfaces.RealInput uCharge "Control signal for charging"
      annotation (Placement(transformation(extent={{-140,-80},{-100,-40}})));
    Modelica.Blocks.Interfaces.RealInput uDischarge
      "Control signal for discharging"
      annotation (Placement(transformation(extent={{-140,-120},{-100,-80}})));
    Modelica.Blocks.Interfaces.RealInput uCool
      "Cooling signal input (must be negative)"
      annotation (Placement(transformation(extent={{-140,-40},{-100,0}})));
    Modelica.Blocks.Interfaces.RealInput uHeat
      "Heating signal input (must be positive)"
      annotation (Placement(transformation(extent={{-140,0},{-100,40}})));
    Modelica.Blocks.Interfaces.RealInput weaHGlo
      "Global horizontal irradiation"
      annotation (Placement(transformation(extent={{-140,80},{-100,120}})));
    Modelica.Blocks.Interfaces.RealInput weaTDryBul
      "Outside air drybulb temperature"
      annotation (Placement(transformation(extent={{-140,40},{-100,80}})));
    Modelica.Blocks.Math.MultiSum multiSum(nu=5, k={-1,1,1,1,-1})
      annotation (Placement(transformation(extent={{34,-6},{46,6}})));
    Modelica.Blocks.Interfaces.RealOutput Pnet
      annotation (Placement(transformation(extent={{100,-10},{120,10}})));
    Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
      annotation (Placement(transformation(extent={{100,-90},{120,-70}})));
    Modelica.Blocks.Interfaces.RealOutput Tzone1
                                                "Zone air temperature"
      annotation (Placement(transformation(extent={{100,-70},{120,-50}})));
    equation
    connect(battery.uCharge, uCharge) annotation (Line(points={{-42,-34},{-80,
            -34},{-80,-60},{-120,-60}}, color={0,0,127}));
    connect(battery.uDischarge, uDischarge) annotation (Line(points={{-42,-38},
            {-60,-38},{-60,-100},{-120,-100}}, color={0,0,127}));
    connect(thermal.uCool, uCool) annotation (Line(points={{-42,2},{-80,2},{-80,
            -20},{-120,-20}}, color={0,0,127}));
    connect(thermal.uHeat, uHeat) annotation (Line(points={{-42,6},{-80,6},{-80,
            20},{-120,20}}, color={0,0,127}));
    connect(pv.Iinc, weaHGlo) annotation (Line(points={{-42,50},{-60,50},{-60,
            100},{-120,100}}, color={0,0,127}));
    connect(thermal.Tadj, weaTDryBul) annotation (Line(points={{-42,16},{-60,16},
            {-60,40},{-80,40},{-80,60},{-120,60}}, color={0,0,127}));
    connect(pv.Pgen, multiSum.u[1]) annotation (Line(points={{-18.8,50},{4,50},
            {4,3.36},{34,3.36}}, color={0,0,127}));
    connect(thermal.PHeat, multiSum.u[2]) annotation (Line(points={{-19,6},{2,6},
            {2,1.68},{34,1.68}}, color={0,0,127}));
    connect(thermal.PCool, multiSum.u[3])
      annotation (Line(points={{-19,2},{0,2},{0,0},{34,0}}, color={0,0,127}));
    connect(battery.Pcharge, multiSum.u[4]) annotation (Line(points={{-18.8,-34},
            {0,-34},{0,-1.68},{34,-1.68}}, color={0,0,127}));
    connect(battery.Pdischarge, multiSum.u[5]) annotation (Line(points={{-18.8,
            -38},{2,-38},{2,-3.36},{34,-3.36}}, color={0,0,127}));
    connect(multiSum.y, Pnet)
      annotation (Line(points={{47.02,0},{110,0}}, color={0,0,127}));
    connect(battery.SOC, SOC) annotation (Line(points={{-18.8,-30},{-12,-30},{
            -12,-80},{110,-80}}, color={0,0,127}));
    connect(thermal.Tzone, Tzone1) annotation (Line(points={{-19,10},{-10,10},{
            -10,-60},{110,-60}}, color={0,0,127}));
    annotation (Icon(coordinateSystem(preserveAspectRatio=false), graphics={
            Rectangle(
            extent={{-100,100},{100,-100}},
            lineColor={0,0,0},
            fillColor={175,175,175},
            fillPattern=FillPattern.Solid)}),                      Diagram(
          coordinateSystem(preserveAspectRatio=false)));
    end Whole;
  end Building;

  package Examples
    extends Modelica.Icons.ExamplesPackage;
    model Simple
      extends Modelica.Icons.Example;
      import SolarPlus = SolarPlusMPC;
      Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(filNam=
            "/home/dhb-lx/git/buildings/modelica-buildings/Buildings/Resources/weatherdata/DRYCOLD.mos")
        annotation (Placement(transformation(extent={{-80,60},{-60,80}})));
      Buildings.BoundaryConditions.WeatherData.Bus weaBus annotation (Placement(
            transformation(extent={{-48,60},{-32,78}}), iconTransformation(extent=
               {{-158,-42},{-138,-22}})));
      Modelica.Blocks.Sources.Pulse uCool(period=3600*2, startTime=3600)
        annotation (Placement(transformation(extent={{-80,-30},{-60,-10}})));
      Modelica.Blocks.Sources.Pulse uCharge(
        offset=0,
        period=3600*6,
        startTime=3600*3,
        amplitude=0.5)
        annotation (Placement(transformation(extent={{-80,-60},{-60,-40}})));
      Modelica.Blocks.Sources.Pulse uDischarge(
        offset=0,
        period=3600*6,
        startTime=0,
        amplitude=0.5)
        annotation (Placement(transformation(extent={{-80,-90},{-60,-70}})));
    SolarPlus.Building.Whole whole
      annotation (Placement(transformation(extent={{20,-10},{40,10}})));
      Modelica.Blocks.Sources.Pulse uHeat(period=3600*2, startTime=3600*2)
      annotation (Placement(transformation(extent={{-80,0},{-60,20}})));
    equation
      connect(weaDat.weaBus, weaBus) annotation (Line(
          points={{-60,70},{-50,70},{-50,69},{-40,69}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%second",
          index=1,
          extent={{6,3},{6,3}}));
    connect(weaBus.HGloHor, whole.weaHGlo) annotation (Line(
        points={{-40,69},{-26,69},{-26,68},{0,68},{0,10},{18,10}},
        color={255,204,51},
        thickness=0.5), Text(
        string="%first",
        index=-1,
        extent={{-6,3},{-6,3}}));
    connect(weaBus.TDryBul, whole.weaTDryBul) annotation (Line(
        points={{-40,69},{-26,69},{-26,68},{0,68},{0,6},{18,6}},
        color={255,204,51},
        thickness=0.5), Text(
        string="%first",
        index=-1,
        extent={{-6,3},{-6,3}}));
    connect(uHeat.y, whole.uHeat) annotation (Line(points={{-59,10},{-6,10},{-6,
            2},{18,2}}, color={0,0,127}));
    connect(uCool.y, whole.uCool) annotation (Line(points={{-59,-20},{-6,-20},{
            -6,-2},{18,-2}}, color={0,0,127}));
    connect(uCharge.y, whole.uCharge) annotation (Line(points={{-59,-50},{0,-50},
            {0,-6},{18,-6}}, color={0,0,127}));
    connect(uDischarge.y, whole.uDischarge) annotation (Line(points={{-59,-80},
            {4,-80},{4,-10},{18,-10}}, color={0,0,127}));
      annotation (
        Icon(coordinateSystem(preserveAspectRatio=false)),
        Diagram(coordinateSystem(preserveAspectRatio=false)),
        experiment(
        StartTime=15552000,
        StopTime=15638400,
        Interval=300,
        Tolerance=1e-06,
        __Dymola_Algorithm="Cvode"));
    end Simple;
  end Examples;

annotation (uses(Modelica(version="3.2.2"), Buildings(version="5.0.0")));
end SolarPlusMPC;
