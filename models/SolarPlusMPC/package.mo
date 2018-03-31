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
      Modelica.Blocks.Math.Gain coolingPowerGain(k=-1/coolingCOP)
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
      Modelica.Blocks.Interfaces.RealInput uCool(min=-1,max=0)
      "Cooling signal input"
        annotation (Placement(transformation(extent={{-140,-100},{-100,-60}}),
            iconTransformation(extent={{-140,-100},{-100,-60}})));
      Modelica.Blocks.Interfaces.RealOutput qHeat(unit="W") "Heating heatflow output"
        annotation (Placement(transformation(extent={{100,50},{120,70}})));
      Modelica.Blocks.Interfaces.RealOutput qCool(unit="W") "Cooling heatflow output"
        annotation (Placement(transformation(extent={{100,-50},{120,-30}}),
            iconTransformation(extent={{100,-50},{120,-30}})));
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
      connect(coolingPowerGain.u, qCool) annotation (Line(points={{58,-80},{20,-80},
              {20,-40},{110,-40}}, color={0,0,127}));
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
    model SimpleBattery
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
      Modelica.Blocks.Interfaces.RealInput u_charge(min=0, max=1) "Control signal for charging"
        annotation (Placement(transformation(extent={{-140,60},{-100,100}})));
      Modelica.Blocks.Interfaces.RealInput u_discharge(min=0, max=1) "Control signal for discharging"
        annotation (Placement(transformation(extent={{-140,20},{-100,60}})));
      Modelica.Blocks.Interfaces.RealOutput SOC "Battery state of charge"
        annotation (Placement(transformation(extent={{100,20},{140,60}})));
      Modelica.Blocks.Interfaces.RealOutput P_charge "Battery charging power"
        annotation (Placement(transformation(extent={{100,-60},{140,-20}})));
      Modelica.Blocks.Interfaces.RealOutput P_discharge "Battery discharging power"
        annotation (Placement(transformation(extent={{100,-100},{140,-60}})));
    equation
      SOC = E/Ecap;
      der(E) = P_charge-P_discharge-P_loss_charge-P_loss_discharge-P_loss_standing;
      P_charge = u_charge*P_cap_charge;
      P_discharge = u_discharge*P_cap_discharge;
      P_loss_charge = P_charge*(1-eta_charge);
      P_loss_discharge = P_discharge*(1-eta_discharge);
      P_loss_standing = SOC*tau_sl/3600
      annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
            coordinateSystem(preserveAspectRatio=false)));
    end SimpleBattery;

    package Examples
      extends Modelica.Icons.ExamplesPackage;
      model BatteryTest
        extends Modelica.Icons.Example;

        SolarPlusMPC.Batteries.SimpleBattery battery(Ecap(displayUnit="kWh")=
          144000000, Pcap(displayUnit="kW") = 10000)
        annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
        Modelica.Blocks.Sources.Step step(startTime=1000)
          annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
      equation
        connect(step.y, battery.u)
          annotation (Line(points={{-39,0},{-12,0}}, color={0,0,127}));
        annotation (experiment(StopTime=15400, Interval=300));
      end BatteryTest;
    end Examples;
  end Batteries;

  package PV "Package for PV models"
    model PVSimple
      parameter Modelica.SIunits.Area A "PV array area";
      parameter Modelica.SIunits.DimensionlessRatio eff "Total efficiency of panel";
      Modelica.Blocks.Interfaces.RealInput I "Solar irradiation incident on array"
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealOutput P "Power genereated by array"
        annotation (Placement(transformation(extent={{100,-20},{140,20}})));
      Modelica.Blocks.Math.Gain gain(k=A)
        annotation (Placement(transformation(extent={{-60,-10},{-40,10}})));
      Modelica.Blocks.Math.Gain gain1(k=eff)
        annotation (Placement(transformation(extent={{0,-10},{20,10}})));
    equation
      connect(gain.u, I)
        annotation (Line(points={{-62,0},{-120,0}}, color={0,0,127}));
      connect(gain.y, gain1.u)
        annotation (Line(points={{-39,0},{-2,0}}, color={0,0,127}));
      connect(gain1.y, P)
        annotation (Line(points={{21,0},{120,0}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
            coordinateSystem(preserveAspectRatio=false)));
    end PVSimple;
  end PV;

  package Building "Package for building models"
    model Simple
      import SolarPlus = SolarPlusMPC;
      Modelica.Blocks.Interfaces.RealInput weaTDryBul
        annotation (Placement(transformation(extent={{-140,-20},{-100,20}})));
      Modelica.Blocks.Interfaces.RealInput uCool
        annotation (Placement(transformation(extent={{-140,-60},{-100,-20}})));
      Modelica.Blocks.Interfaces.RealOutput Pcool "Output signal connector"
        annotation (Placement(transformation(extent={{100,-70},{120,-50}})));
      Modelica.Blocks.Interfaces.RealInput weaHGloHor
        annotation (Placement(transformation(extent={{-140,60},{-100,100}})));
      Modelica.Blocks.Interfaces.RealOutput Ppv "Output signal connector"
        annotation (Placement(transformation(extent={{100,70},{120,90}})));
      Modelica.Blocks.Interfaces.RealInput uCharge
        annotation (Placement(transformation(extent={{-140,28},{-100,68}})));
      SolarPlus.Batteries.SimpleBattery battery(
        SOC_0=1,
        P_cap_charge=500,
        P_cap_discharge=500,
        Ecap(displayUnit="kWh") = 18000000)
        annotation (Placement(transformation(extent={{-60,30},{-40,50}})));
      Modelica.Blocks.Interfaces.RealOutput SOC
        annotation (Placement(transformation(extent={{100,34},{120,54}})));
      Modelica.Blocks.Interfaces.RealOutput Pcharge
        annotation (Placement(transformation(extent={{100,20},{120,40}})));
      Modelica.Blocks.Interfaces.RealOutput Pnet
        annotation (Placement(transformation(extent={{100,-10},{120,10}})));
      Modelica.Blocks.Math.Sum sum1(                      nin=5, k={1,-1,-1,-1,1})
        annotation (Placement(transformation(extent={{60,-10},{80,10}})));
      Modelica.Blocks.Interfaces.RealInput othLoad
        annotation (Placement(transformation(extent={{-140,-100},{-100,-60}})));
      SolarPlus.PV.PVSimple pV(eff=0.15, A=5)
        annotation (Placement(transformation(extent={{-60,70},{-40,90}})));
      SolarPlus.Refrigeration.Refrigerator refrigerator(Cap(displayUnit="kW")=
          1000, COP=3)
        annotation (Placement(transformation(extent={{-60,-30},{-40,-10}})));
      Modelica.Blocks.Interfaces.RealOutput Tref
        "Absolute temperature as output signal"
        annotation (Placement(transformation(extent={{100,-30},{120,-10}})));
      Modelica.Blocks.Interfaces.RealInput uDischarge
        annotation (Placement(transformation(extent={{-140,8},{-100,48}})));
      Modelica.Blocks.Interfaces.RealOutput Pdischarge
        annotation (Placement(transformation(extent={{100,10},{120,30}})));
    equation
      connect(battery.SOC, SOC)
        annotation (Line(points={{-38,44},{110,44}}, color={0,0,127}));
      connect(othLoad, sum1.u[4]) annotation (Line(points={{-120,-80},{52,-80},{52,
              4},{58,4},{58,0.8},{58,0.8}}, color={0,0,127}));
      connect(Pnet, sum1.y)
        annotation (Line(points={{110,0},{81,0}}, color={0,0,127}));
      connect(weaHGloHor, pV.I)
        annotation (Line(points={{-120,80},{-62,80}}, color={0,0,127}));
      connect(pV.P, Ppv)
        annotation (Line(points={{-38,80},{110,80}}, color={0,0,127}));
      connect(pV.P, sum1.u[1]) annotation (Line(points={{-38,80},{40,80},{40,-1.6},
              {58,-1.6}}, color={0,0,127}));
      connect(weaTDryBul, refrigerator.Tamb) annotation (Line(points={{-120,0},{-72,
              0},{-72,-20},{-62,-20}}, color={0,0,127}));
      connect(uCool, refrigerator.uCool) annotation (Line(points={{-120,-40},{-72,
              -40},{-72,-24},{-62,-24}}, color={0,0,127}));
      connect(refrigerator.P, Pcool) annotation (Line(points={{-39,-26},{0,-26},{0,
              -60},{110,-60}}, color={0,0,127}));
      connect(refrigerator.P, sum1.u[3]) annotation (Line(points={{-39,-26},{0,-26},
              {0,0},{58,0}},     color={0,0,127}));
      connect(refrigerator.T, Tref)
        annotation (Line(points={{-39,-20},{110,-20}}, color={0,0,127}));
      connect(uCharge, battery.u_charge)
        annotation (Line(points={{-120,48},{-62,48}}, color={0,0,127}));
      connect(battery.u_discharge, uDischarge) annotation (Line(points={{-62,44},
              {-76,44},{-76,28},{-120,28}}, color={0,0,127}));
      connect(battery.P_charge, sum1.u[2]) annotation (Line(points={{-38,36},{28,
              36},{28,-0.8},{58,-0.8}}, color={0,0,127}));
      connect(battery.P_discharge, sum1.u[5]) annotation (Line(points={{-38,32},{
              12,32},{12,1.6},{58,1.6}}, color={0,0,127}));
      connect(battery.P_charge, Pcharge) annotation (Line(points={{-38,36},{84,36},
              {84,30},{110,30}}, color={0,0,127}));
      connect(Pdischarge, battery.P_discharge) annotation (Line(points={{110,20},
              {70,20},{70,32},{-38,32}}, color={0,0,127}));
      annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
            coordinateSystem(preserveAspectRatio=false)));
    end Simple;

    model Thermal
    Envelope.R1C1 r1C1_1
      annotation (Placement(transformation(extent={{-12,-10},{8,10}})));
    HVAC.SimpleHeaterCooler simpleHeaterCooler
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
            textString="Thermal")}),                               Diagram(
          coordinateSystem(preserveAspectRatio=false)));
    end Thermal;

    model Whole
    Thermal thermal
      annotation (Placement(transformation(extent={{-40,20},{-20,40}})));
    annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
          coordinateSystem(preserveAspectRatio=false)));
    end Whole;
  end Building;

  package Examples
    extends Modelica.Icons.ExamplesPackage;
    model Simple
      extends Modelica.Icons.Example;
      import SolarPlus = SolarPlusMPC;
      SolarPlus.Building.Simple simple
        annotation (Placement(transformation(extent={{48,-10},{68,10}})));
      Buildings.BoundaryConditions.WeatherData.ReaderTMY3 weaDat(filNam=
            "/home/dhb-lx/git/buildings/modelica-buildings/Buildings/Resources/weatherdata/DRYCOLD.mos")
        annotation (Placement(transformation(extent={{-80,20},{-60,40}})));
      Buildings.BoundaryConditions.WeatherData.Bus weaBus annotation (Placement(
            transformation(extent={{-48,20},{-32,38}}), iconTransformation(extent=
               {{-158,-42},{-138,-22}})));
      Modelica.Blocks.Sources.Pulse uCool(period=3600*2, startTime=3600*2)
        annotation (Placement(transformation(extent={{-80,-50},{-60,-30}})));
      Modelica.Blocks.Sources.Pulse uCharge(
        offset=0,
        period=3600*6,
        startTime=3600*3,
        amplitude=0.5)
        annotation (Placement(transformation(extent={{-80,-6},{-60,14}})));
      Modelica.Blocks.Sources.Constant othLoad(k=0)
        annotation (Placement(transformation(extent={{-80,-80},{-60,-60}})));
      Modelica.Blocks.Sources.Pulse uDischarge(
        offset=0,
        period=3600*6,
        startTime=0,
        amplitude=0.5)
        annotation (Placement(transformation(extent={{-60,-30},{-40,-10}})));
    equation
      connect(weaDat.weaBus, weaBus) annotation (Line(
          points={{-60,30},{-50,30},{-50,29},{-40,29}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%second",
          index=1,
          extent={{6,3},{6,3}}));
      connect(weaBus.HGloHor, simple.weaHGloHor) annotation (Line(
          points={{-40,29},{2,29},{2,8},{46,8}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%first",
          index=-1,
          extent={{-6,3},{-6,3}}));
      connect(weaBus.TDryBul, simple.weaTDryBul) annotation (Line(
          points={{-40,29},{2,29},{2,0},{46,0}},
          color={255,204,51},
          thickness=0.5), Text(
          string="%first",
          index=-1,
          extent={{-6,3},{-6,3}}));
      connect(uCool.y, simple.uCool) annotation (Line(points={{-59,-40},{-4,-40},
              {-4,-4},{46,-4}},   color={0,0,127}));
      connect(othLoad.y, simple.othLoad) annotation (Line(points={{-59,-70},{0,
              -70},{0,-8},{46,-8}},    color={0,0,127}));
      connect(uCharge.y, simple.uCharge) annotation (Line(points={{-59,4},{-38,4},
              {-38,4.8},{46,4.8}}, color={0,0,127}));
      connect(uDischarge.y, simple.uDischarge) annotation (Line(points={{-39,-20},
              {-20,-20},{-20,2.8},{46,2.8}}, color={0,0,127}));
      annotation (
        Icon(coordinateSystem(preserveAspectRatio=false)),
        Diagram(coordinateSystem(preserveAspectRatio=false)),
        experiment(
          StopTime=86400,
          Interval=300,
          Tolerance=1e-06,
          __Dymola_Algorithm="Cvode"));
    end Simple;
  end Examples;

annotation (uses(Modelica(version="3.2.2"), Buildings(version="5.0.0")));
end SolarPlusMPC;
